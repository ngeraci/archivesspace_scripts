#!/usr/bin/env python

import requests
import json
import secrets
import sys
import codecs

def exportEAD(repoArg):

    #get login info in secrets.py file
    baseURL = secrets.baseURL
    user = secrets.user
    password = secrets.password

    #authenticate
    auth = requests.post(baseURL + '/users/'+ user +'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session}
    print('authenticated')
    sys.stdout.flush()

    #check argument
    if repoArg == 3 or repoArg == 4 or repoArg == 5:
        repo = str(repoArg)
    else:
        print("Error: invalid repository value")
        sys.exit(0)

    #exclude any specific ead_ids
    to_exclude = 'ms091.xml'

    #get ids
    ids = requests.get(baseURL + '/repositories/' + repo + '/resources?all_ids=true', headers=headers)

    #export finding aids
    for i in ids.json():
        resource = (requests.get(baseURL + '/repositories/' + repo + '/resources/' + str(i), headers=headers)).json()

        #set parameters to export
        if resource['publish'] == True:
            if 'finding_aid_status' in resource:
                if resource['finding_aid_status'] == 'collection-level':
                    if resource['ead_id'] not in to_exclude:

                        ead = requests.get(baseURL + '/repositories/'+ repo +'/resource_descriptions/'+str(i)+'.xml', headers=headers)
                        ead.encoding = 'utf-8'

                        # Sets the location where the files should be saved
                        if repo == str(3):
                            repoName = 'MS'
                        elif repo == str(4):
                            repoName = 'UA'
                        elif repo == str(5):
                            repoName = 'WRCA'

                        destination = 'C:\\Users\\ngeraci\\Documents\\ead_export\\raw_export\\' + repoName + '\\'
                        path = destination + resource['ead_id']


                        #write out to file
                        f = codecs.open(path, 'w', 'utf-8')
                        f.write(ead.text)
                        f.close()

                        #print confirmation
                        print(resource['ead_id'] + ' exported to ' + destination)
                        sys.stdout.flush()


for repo in [3,4,5]:
    exportEAD(repo)