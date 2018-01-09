import requests
import json
import secrets
import codecs
import re
import csv
from lxml import etree
from lxml.builder import E

def marcxmlExport():
    #get login info in secrets.py file
    baseURL = secrets.baseURL
    user = secrets.user
    password = secrets.password
    
    #authenticate
    auth = requests.post(baseURL + '/users/'+ user +'/login?password='+password).json()
    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session}

    #initialize blank list to hold xml
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
#misc text processing needed at beginning
##make valid xml     
    #scrub repeated xml declarations
    xmlAll = xmlAll.replace('<?xml version="1.0" encoding="UTF-8"?>','')
    #add outer tag
    xmlAll = '<document>' + xmlAll + '</document>'
    #replace period with space in collection numbers, needed for OAC URL retrieval
    matchCollNumber = re.compile(r'(MS|UA|WRCA)\.([0-9]{3})')
    xmlAll = matchCollNumber.sub(r'\1 \2',xmlAll)
    matchAltCollNumber = re.compile(r'(WR)\.([0-9]{2})\.([0-9]{2})')
    xmlAll = matchAltCollNumber.sub(r'\1 \2 \3',xmlAll)


#get OAC urls in dict from CSV export
    with open('reports/ms_oac.csv', mode='r') as infile:
        reader = csv.reader(infile)
        urlDict = {rows[1]:rows[0] for rows in reader}   

#lxml processing
    root = etree.XML(xmlAll)
    records = root.xpath("/document/*[namespace-uri()='http://www.loc.gov/MARC21/slim' and local-name()='collection']/*[namespace-uri()='http://www.loc.gov/MARC21/slim' and local-name()='record']")

#   loop through each record
    for record in records:
        #loop through datafield tags
        for field in record.getchildren():
            #update leader
            if field.tag == '{http://www.loc.gov/MARC21/slim}leader':
                field.text = '00000npcaa2200000Ii 4500'
            elif field.tag == "{http://www.loc.gov/MARC21/slim}datafield":
                #store collection number in variable, then remove 852
                if field.attrib['tag'] == '852':
                    subfield = field.getchildren()
                    collNumber = subfield[2].text
                    field.getparent().remove(field)
                #replace 'CURIV' with 'CRU' OCLC code
                elif field.attrib['tag'] == '040':
                    subfield = field.getchildren()
                    for s in subfield:
                        s.text = s.text.replace('CURIV','CRU')
                #delete date from 245 and store in variable
                elif field.attrib['tag'] == '245':
                    subfield = field.getchildren()
                    for s in subfield:
                        if s.attrib['code'] == 'f':
                            date = s.text
                            s.getparent().remove(s)
                    #add 264 following 245
                    record.insert(record.index(field)+1,
                        E('datafield',
                            E('subfield',date,code='c'),
                            #tagToReplace because having an attribute named 'tag' was throwing an error in this function
                            ind1='',ind2='0',tagToReplace='264'))
                #delete 520 for scopecontent
                elif field.attrib['tag'] == '520' and field.attrib['ind1'] == '2':
                    field.getparent().remove(field)
                #change field 534 to 524
                elif field.attrib['tag'] == '534':
                    field.attrib['tag'] = '524'
                #remove 555 field
                elif field.attrib['tag'] == '555':
                    field.getparent().remove(field)
                #600, 610, 650 & 651 fields with second indicator '7' should be changed to second indicator '0', and delete subfield 2
                elif field.attrib['tag'] in ['600','610','650','651']:
                        field.attrib['ind2'] = '0'
                        subfield = field.getchildren()
                        for s in subfield:
                            if s.attrib['code'] == '2':
                                s.getparent().remove(s)
                #856
                elif field.attrib['tag'] == '856':
                    #add subfield u (URL)
                    field.append(etree.Element('subfield', code='u'))
                    #get subfields
                    subfield = field.getchildren()
                    #update subfield 3 (text that precedes URL)
                    subfield[0].attrib['code'] = '3'
                    subfield[0].text = 'Finding aid:'
                    #add URL to subfield U
                    try:
                        subfield[1].text = urlDict[collNumber]
                    except:
                        print(collNumber + ' URL not found')

    #write to string        
    xmlAll = etree.tostring(root, encoding='unicode')

    #miscellaneous text processing
    #address spacing issues caused by ead markup like <emph>
    doubleSpace = re.compile(r'(\S)  (\S)')
    xmlAll = doubleSpace.sub(r'\1 \2',xmlAll)
    punctWithSpace = re.compile(r' (\.|,|:)')
    xmlAll = punctWithSpace.sub(r'\1',xmlAll)
    xmlAll = xmlAll.replace('> ','>')

    #change double paren in 300 field to single
    xmlAll = xmlAll.replace('((','(')
    xmlAll = xmlAll.replace('))',')')

    #lowercase 'Linear Feet'
    xmlAll = xmlAll.replace('Linear Feet','linear feet')

    #replace tagToReplace with tag
    xmlAll = xmlAll.replace('tagToReplace','tag')

    #xml declaration
    xmlAll = '<?xml version="1.0" encoding="UTF-8"?>' + xmlAll
 
    #write out to file
    path = 'export.xml'
    f = codecs.open(path, 'w', 'utf-8')
    f.write(xmlAll)
    f.close()                 

marcxmlProcess(marcxmlExport())