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

    #select repository (MS=3, UA=4, WRCA=5)
    repo = 3

    #get all resource records in repository
    endpoint = '/repositories/' + str(repo) + '/resources?all_ids=true'
    ids = requests.get(baseURL + endpoint, headers=headers).json()

    records = []
    for id in ids:
        endpoint = '/repositories/' + str(repo) + '/resources/'+str(id)
        output = requests.get(baseURL + endpoint, headers=headers).json()
        if output['publish'] == True:
            if 'finding_aid_status' in output:
                if output['finding_aid_status'] == 'collection-level':

                    #lowercasing titles
                    if ' Papers' in output['title']:
                        output['title'] = output['title'].replace(' Papers', ' papers')
                    elif ' Records' in output['title']:
                        output['title'] = output['title'].replace(' Records', ' records')
                    elif ' Collection' in output['title']:
                        output['title'] = output['title'].replace(' Collection', ' collection')
                    else:
                        pass


                    #Add Resource Type
                    if 'papers' in output['title']:
                        output['resource_type'] = 'papers'
                    elif 'records' in output['title']:
                        output['resource_type'] = 'records'
                    elif 'collection' in output['title']:
                        output['resource_type'] = 'collection'
                    else:
                        pass #check with jessica : what should happen w colls that don't meet any of these?


                    #date stuff
                    dates = output['dates']

                    #strip trailing period from date expression
                    for index, n in enumerate(dates):
                        try:
                            if n['expression'].endswith('.'):
                                n['expression'] = n['expression'][:-1] #slice notation removes last character
                            elif n['expression'].endswith('. '):
                                n['expression'] = n['expression'][:-2] #last two chars if it ends in period, space
                        except:
                            pass

                    #strip leading space        
                    for index, n in enumerate(dates):
                        try:
                            if n['expression'].startswith(' '):
                                n['expression'] = n['expression'][1:] #slice notation removes first character
                        except:
                            pass

                    #strip trailing space
                    for index, n in enumerate(dates):
                        try:
                            if n['expression'].endswith(' '):
                                n['expression'] = n['expression'][:-1] #slice notation removes last character
                        except:
                            pass

                    #correct date types
                    for index, n in enumerate(dates):
                        try:
                            if '-' in (n['expression']) and n['date_type'] == 'single':
                                n['date_type'] = 'inclusive'
                            elif re.match('^[0-9]{4}$',n['expression']):
                                n['date_type'] = 'single'    
                        except:
                            pass

                    #normalize dates
                    for index, n in enumerate(dates):
                        try:
                            #single dates
                            if re.match('^[0-9]{4}$',n['expression']): #match YYYY
                                n['begin'] = n['expression']
                            elif re.match('^[0-9]{4}, undated$',n['expression']): #match YYYY, undated
                                n['begin'] = n['expression'][:4]
                            elif re.match('^circa [0-9]{4}$',n['expression']): #match circa YYYY
                                n['begin'] = n['expression'][6:10]
                            elif re.match('^circa [0-9]{4}, undated$',n['expression']): #match circa YYYY, undated
                                n['begin'] = n['expression'][6:10]
                            #date ranges
                            elif re.match('^[0-9]{4}-[0-9]{4}$', n['expression']): #match YYYY-YYYY
                                n['begin'] = n['expression'][:4]
                                n['end'] = n['expression'][5:9]
                            elif re.match('^[0-9]{4}-[0-9]{4}, undated$', n['expression']): #match YYYY-YYYY, undated
                                n['begin'] = n['expression'][:4]
                                n['end'] = n['expression'][5:9]
                            elif re.match('^circa [0-9]{4}-[0-9]{4}$', n['expression']): #match circa YYYY-YYYY
                                n['begin'] = n['expression'][6:10]
                                n['end'] = n['expression'][11:15]
                            elif re.match('^circa [0-9]{4}-[0-9]{4}, undated$', n['expression']): #match circa YYYY-YYYY, undated
                                n['begin'] = n['expression'][6:10]
                                n['end'] = n['expression'][11:15]
                            elif re.match('^[0-9]{4}-circa [0-9]{4}$', n['expression']): #match YYYY-circa YYYY
                                n['begin'] = n['expression'][:4]
                                n['end'] = n['expression'][11:15]                   
                        except:
                            pass

                    #fix container summaries
                    extents = output['extents']

                    #trim leading space
                    for index, n in enumerate(extents):
                        try:
                           for summary in n['container_summary']:
                                if n['container_summary'].startswith(' '):
                                    n['container_summary'] = n['container_summary'][1:]
                        except:
                            pass

                    #trim trailing space or period
                    for index, n in enumerate(extents):
                        try:
                           for summary in n['container_summary']:
                                if n['container_summary'].endswith(' '):
                                    n['container_summary'] = n['container_summary'][:-1]
                                elif n['container_summary'].endswith('.'):
                                    n['container_summary'] = n['container_summary'][:-1]
                        except:
                            pass


                    #open paren
                    for index, n in enumerate(extents):
                        try:
                           for summary in n['container_summary']:
                                if n['container_summary'].startswith('('):
                                    continue
                                else:
                                    n['container_summary'] = '(' + n['container_summary']
                        except:
                            pass

                    #close paren            
                    for index, n in enumerate(extents):
                        try:
                           for summary in n['container_summary']:
                                if n['container_summary'].endswith(')'):
                                    continue
                                else:
                                    n['container_summary'] = n['container_summary'] + ')'
                        except:
                            pass

                    #remove box type from container summary
                    for index, n in enumerate(extents):
                        try:
                            for summary in n['container_summary']:
                                if re.match('^\([0-9]+ boxe?s?\)$',n['container_summary']):
                                    continue
                                if re.match('^\([0-9]+ cartons?\)$',n['container_summary']):
                                    continue
                                elif re.match('^\([0-9]+ ([A-Za-z ]+) boxe?s?\)$',n['container_summary']):
                                    n['container_summary'] = n['container_summary'].replace('document ', '').replace('half ','').replace('storage ','').replace('record ', '').replace('flat ', '')
                                elif re.match('^\([0-9]+ ([A-Za-z ]+) cartons?\)$',n['container_summary']):
                                    n['container_summary'] = n['container_summary'].replace('document ', '').replace('half ','').replace('storage ','').replace('record ', '').replace('flat ', '').replace('Paige ','')
                                elif n['container_summary'] == '(1 boxes)':
                                    n['container_summary'] = '(1 box)'
                                else:
                                    pass
                        except:
                            pass

                    #take out 'guide to the' from finding aid title
                    if output['finding_aid_title'].startswith('Guide to the '):
                        output['finding_aid_title'] = output['finding_aid_title'][13:] # trim first 13 chars
                    else:
                        pass

                    #remove finding aid author
                    if 'finding_aid_author' in output:
                        del output['finding_aid_author']
                    else:
                        pass


                    notes = output['notes']

                    #update note lanugage for 'Director of Distinctive Collections'               
                    for index, n in enumerate(notes):
                        try:
                           for subnote in n['subnotes']:
                                if 'Head of Special Collections & Archives' in subnote['content']:
                                    subnote['content'] = subnote['content'].replace('Head of Special Collections & Archives', 'Director of Distinctive Collections')
                        except:
                            pass

                    #check and  update accessnote
                    # note : currently only updates note if it exists, doesn't add if it doesn't exist                
                    for index, n in enumerate(notes):
                        try:
                            if n['type'] == 'accessrestrict' and output['ead_id'] is not 'ms391.xml': #exclude tweet collection
                               for subnote in n['subnotes']:
                                    if subnote['content'] == 'This collection is unprocessed. Please contact Special Collections & University Archives regarding the availability of materials for research use.':
                                        pass
                                    else:
                                        subnote['content'] = 'This collection is unprocessed. Please contact Special Collections & University Archives regarding the availability of materials for research use.'
                        except:
                            pass

                    #delete processing history note
                    for index, n in enumerate(notes):
                        try:
                            if n['label'] == 'Processing History':
                               del notes[index]
                        except:
                            pass

                    # scopecontentlabel = 'Collection Scope and Contents'
                    for index, n in enumerate(notes):
                        try:
                            if n['type'] == 'scopecontent':
                                n['label'] = 'Collection Scope and Contents'
                        except:
                            pass           

                    #preferred citation
                    # note : currently only updates note if it exists, doesn't add if it doesn't exist                            
                    for index, n in enumerate(notes):
                        if repo == 3 or repo == 4:
                            try:
                                if n['type'] == 'prefercite':
                                    for subnote in n['subnotes']:
                                        if subnote['content'] == '[identification of item], [date if possible]. ' + output['title'] + ' (' + output['id_0'] + ' ' + output['id_1'] + '). Special Collections & University Archives, University of California, Riverside.':
                                            pass
                                        else:
                                            subnote['content'] = '[identification of item], [date if possible]. ' + output['title'] + ' (' + output['id_0'] + ' ' + output['id_1'] + '). Special Collections & University Archives, University of California, Riverside.'
                            except:
                                pass
                        #wrca collection numbers are weird, skip this for now        
                        elif repo == 5:
                            pass

                    #appends updated output to "records" list
                    records.append(output)
                    
                    #post the updated resource in ASpace
                    post = requests.post(baseURL + endpoint, headers=headers, data=json.dumps(output)).json()

    #save all updated records to a local file
    #i mainly used this to review and test changes before i was ready to post them 
    if repo == 3:
        f=open('resources/spcoll.json', 'w')
        json.dump(records, f)
        f.close()
    elif repo == 4:
        f=open('resources/ua.json', 'w')
        json.dump(records, f)
        f.close()
    elif repo == 5:
        f=open('resources/wrca.json', 'w')
        json.dump(records, f)
        f.close()
    else:
        print ("check repository number, process failed")

if __name__ == '__main__':
    main()