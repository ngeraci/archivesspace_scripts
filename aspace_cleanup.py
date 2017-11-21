#!/usr/bin/env python

import sys
import requests
import json
import re
import ConfigParser
import time

startTime = time.time()

# local config file, contains variables
configFilePath = 'local_settings.cfg'
config = ConfigParser.ConfigParser()
config.read(configFilePath)

# URL parameters dictionary, used to manage common URL patterns
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
baseURL = '{baseURL}'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session}
print ('Authenticated with header ' + str(headers))

endpoint = '/repositories/3/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

records = []
for id in ids:
    endpoint = '/repositories/3/resources/'+str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    if 'finding_aid_status' in output:
        if output['finding_aid_status'] == 'collection-level':

            #Add Resource Type
            if 'papers' in output['title']:
                output['resource_type'] = 'papers'
            elif 'Papers' in output['title']:
                output['resource_type'] = 'papers'
            elif 'records' in output['title']:
                output['resource_type'] = 'records'
            elif 'Records' in output['title']:
                output['resource_type'] = 'records'
            elif 'collection' in output['title']:
                output['resource_type'] = 'collection'
            elif 'collection' in output['title']:
                output['resource_type'] = 'collection'
            else:
                pass #check with jessica : what should happen w colls that don't meet any of these?

            #strip trailing period from date expression
            if output['dates'][0]['expression'].endswith('.'):
                output['dates'][0]['expression'] = output['dates'][0]['expression'][:-1] #https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation
            elif output['dates'][0]['expression'].endswith('. '):
                output['dates'][0]['expression'] = output['dates'][0]['expression'][:-2]    
            else:
                pass

            #check date type        
            # if 'bulk' in output['dates'][0]['expression']:
            #     output['dates'][0]['date_type'] = 'bulk'
            # elif '-' in output['dates'][0]['expression']:
            #     output['dates'][0]['date_type'] = 'inclusive'
            # elif ',' in output['dates'][0]['expression']:
            #     output['dates'][0]['date_type'] = 'inclusive'
            # else:
            #     output['dates'][0]['date_type'] = 'single'
            # print (output['dates'][0]['expression'] + ', ' + output['dates'][0]['date_type'] )    

            #add normalized date
            # ???????


            #remove box type, add parenthesis
            extents = output['extents']

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
            
            # #regexes to clean up box language
            # check with Jessica - do we need to add different type of boxes togheter?
            # i.e. should (17 record storage boxes, 4 flat storage boxes, 4 half-size document boxes, 5 document boxes, 72 index card boxes) be 102 boxes?

            # for index, n in enumerate(extents):
            #     try:
            #        for summary in n['container_summary']:
            #             if 'document boxes' in n['container_summary']:
            #                 n['container_summary'] = n['container_summary'].replace('document boxes', 'boxes')
            #     except:
            #         pass
                              

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
                    if n['type'] == 'accessrestrict':
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
            for index, n in enumerate(notes):
                try:
                    if n['type'] == 'prefercite':
                        for subnote in n['subnotes']:
                            if subnote['content'] == '[identification of item], [date if possible]. ' + output['title'] + ' (' + output['id_0'] + ' ' + output['id_1'] + '). Special Collections & University Archives, University of California, Riverside.':
                                pass
                            else:
                                subnote['content'] = '[identification of item], [date if possible]. ' + output['title'] + ' (' + output['id_0'] + ' ' + output['id_1'] + '). Special Collections & University Archives, University of California, Riverside.'
                except:
                    pass
       
 



            records.append(output)    
        else:
            pass
    else:
        pass

f=open('collectionlevel1.json', 'w')
json.dump(records, f)
f.close()

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)