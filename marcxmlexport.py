import requests
import json
import secrets
import codecs
import re

def marcxmlExport():

    #get login info in secrets.py file
    baseURL = secrets.baseURL
    user = secrets.user
    password = secrets.password

    #authenticate
    auth = requests.post(baseURL + '/users/'+ user +'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session}

    xmlAll = []

    for repo in [3,4,5]:
        #int to string
        repo = str(repo)

        #get ids
        ids = requests.get(baseURL + '/repositories/' + repo + '/resources?all_ids=true', headers=headers)

       

        #loop through ids
        for i in ids.json():
            resource = (requests.get(baseURL + '/repositories/' + repo + '/resources/' + str(i), headers=headers)).json()

            #set parameters to export
            if resource['publish'] == True:
                if 'finding_aid_status' in resource:
                    if resource['finding_aid_status'] == 'collection-level':

                        #get marcxml
                        marcXML = requests.get(baseURL + '/repositories/'+ repo +'/resources/marc21/'+str(i)+'.xml', headers=headers)
                        marcXML.encoding = 'utf-8'

                        #append individual record to xmlAll list
                        xmlAll.append(marcXML.text)

    xmlAll = ''.join(xmlAll)                    
    return xmlAll

def marcxmlProcess(xmlAll):

#query collection registry API to get arks - in progress
    baseURL = 'https://registry.cdlib.org/api/v1/collection/'






#just text processing stuff
    #scrub repeated xml declarations
    xmlAll = xmlAll.replace('<?xml version="1.0" encoding="UTF-8"?>','')
    
    #address spacing issues caused by ead markup like <emph>
    doubleSpace = re.compile(r'(\S)  (\S)')
    xmlAll = doubleSpace.sub(r'\1 \2',xmlAll)
    xmlAll = xmlAll.replace(' .', '.')
    xmlAll = xmlAll.replace(' ,', '.')
    xmlAll = xmlAll.replace('> ', '>')

    #replace period with space in collection numbers
    collNumber = re.compile(r'(MS|UA|WRCA)\.([0-9]{3})')
    xmlAll = collNumber.sub(r'\1 \2',xmlAll)
    collNumberAlt = re.compile(r'(WR)\.([0-9]{2})\.([0-9]{2})')
    xmlAll = collNumberAlt.sub(r'\1 \2 \3',xmlAll)

    #add single xml declaration and outer tag
    xmlAll = '<?xml version="1.0" encoding="UTF-8"?> <document>' + xmlAll + '</document>'

#write out to file
    path = 'C:/Users/ngeraci/Documents/scripts/python/aspacecleanup/marcxml/export.xml'
    f = codecs.open(path, 'w', 'utf-8')
    f.write(xmlAll)
    f.close()                 

marcxmlProcess(marcxmlExport())