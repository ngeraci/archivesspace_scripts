#!/usr/bin/env python

import requests
import secrets
import json
import re

def main(): 

    #authenticate using login info in secrets.py file
    baseURL = secrets.baseURL
    user = secrets.user
    password = secrets.password
    auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

    #select repository (MS = 3, UA = 4, WRCA = 5)
    repo = 3
    
    #get all resource records in repository
    endpoint = '/repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()
    records = []

    #loop through resource records by ID
    for i in ids:
        endpoint = '/repositories/' + str(repo) + '/resources/'+str(i)
        output = requests.get(baseURL + endpoint, headers=headers).json()

        #only operate on published collection-level finding aids
        #take out these three lines and unindent the rest if you want to operate on all finding aids
        if output['publish'] == True:
            if 'finding_aid_status' in output:
                if output['finding_aid_status'] == 'collection-level':
                        
                    #set subject variable                   
                    subjects = output['subjects']
                    #create empty list to hold sub-lists
                    subjRecords = []
                        
                    #loop through subject URIs in each resource and retrieve subject records
                    for index, n in enumerate(subjects):
                        subjEndpoint = n['ref']
                        subjOutput = requests.get(baseURL + subjEndpoint, headers=headers).json()

                        #create empty list to capture minimal info (title, term type and URI) for each subject
                        miniSubj = []

                        #append term type to miniSubj, categorizing all non-genre/form as 'a_subject'
                        if subjOutput['terms'][0]['term_type'] == 'genre_form':
                            miniSubj.append('genre_form')
                        else:
                            miniSubj.append('a_subject')

                        #add title to miniSubj
                        miniSubj.append(subjOutput['title'])

                        #add URI to miniSubj
                        miniSubj.append(subjOutput['uri'])

                        #append individual miniSubj record to meta-list of all subjects attached to resource
                        subjRecords.append(miniSubj)                        

                        #get sorted list with URIs only
                        sortedURIs = [item[2] for item in sorted(subjRecords)]

                        #put sorted URIs back into resource record
                        for index, n in enumerate(subjects):
                            n['ref'] = sortedURIs[int(index)]

                        #post updated resource record to ASpace
                        records.append(output)               
                        post = requests.post(baseURL + endpoint, headers=headers, data=json.dumps(output)).json()

if __name__ == '__main__':
    main()