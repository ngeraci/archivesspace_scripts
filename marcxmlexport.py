import requests
import json
import secrets
import codecs
import re
from lxml import etree

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

                        #append individual record to xmlAll list
                        xmlAll.append(marcXML.text)

    xmlAll = ''.join(xmlAll)                    
    return xmlAll

def marcxmlProcess(xmlAll):
#make the combined output a valid xml file
    #scrub repeated xml declarations
    xmlAll = xmlAll.replace('<?xml version="1.0" encoding="UTF-8"?>','')
    #add outer tag
    xmlAll = '<document>' + xmlAll + '</document>'

    #placeholder for OAC URL - figure out how to get
    oacURL = 'https://oac.cdlib.org/ARK'

#lxml processing
    root = etree.XML(xmlAll)  
    datafield = root.xpath("/document/*[namespace-uri()='http://www.loc.gov/MARC21/slim' and local-name()='collection']/*[namespace-uri()='http://www.loc.gov/MARC21/slim' and local-name()='record']/*[namespace-uri()='http://www.loc.gov/MARC21/slim' and local-name()='datafield']")
    for field in datafield:
        #remove 555 field
        if field.attrib['tag'] == '555':
            field.getparent().remove(field)
        #change field 534 to 524, per Yoko
        elif field.attrib['tag'] == '534':
            field.attrib['tag'] = '524'
        #600 and 610 fields with second indicator '7' should be changed to second indicator '0', per Yoko
        elif field.attrib['ind2'] == '7':
            if field.attrib['tag'] == '600' or field.attrib['tag'] == '610':
                field.attrib['ind2'] = '0'
        #856
        elif field.attrib['tag'] == '856':
            #add subfield u (URL)
            field.append(etree.Element('subfield', code='u'))
            #get subfields
            subfield = field.getchildren()
            #update subfield 3 (text that precedes URL)
            subfield[0].attrib['code'] = '3'
            subfield[0].text = 'Finding aid'
            #add URL to subfield U
            subfield[1].text = oacURL

    #write to string        
    xmlAll = etree.tostring(root, encoding='unicode')

#miscellaneous text processing
    #address spacing issues caused by ead markup like <emph>
    doubleSpace = re.compile(r'(\S)  (\S)')
    xmlAll = doubleSpace.sub(r'\1 \2',xmlAll)
    punctWithSpace = re.compile(r' (\.|,|:|>)')
    xmlAll = punctWithSpace.sub(r'\1',xmlAll)

    #replace period with space in collection numbers
    collNumber = re.compile(r'(MS|UA|WRCA)\.([0-9]{3})')
    xmlAll = collNumber.sub(r'\1 \2',xmlAll)
    collNumberAlt = re.compile(r'(WR)\.([0-9]{2})\.([0-9]{2})')
    xmlAll = collNumberAlt.sub(r'\1 \2 \3',xmlAll)

    #change double paren in 300 field to single
    xmlAll = xmlAll.replace('((','(')
    xmlAll = xmlAll.replace('))',')')

    #lowercase 'Linear Feet'
    xmlAll = xmlAll.replace('Linear Feet','linear feet')

    #xml declaration
    xmlAll = '<?xml version="1.0" encoding="UTF-8"?>' + xmlAll
 
#write out to file
    path = 'export.xml'
    f = codecs.open(path, 'w', 'utf-8')
    f.write(xmlAll)
    f.close()                 

marcxmlProcess(marcxmlExport())