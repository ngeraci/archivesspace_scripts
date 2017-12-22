#!/usr/bin/env python

import os
import codecs
import re
import sys
from lxml import etree

def process():

    basedir = 'C:\\Users\\ngeraci\\Documents\\ead_export\\'

    repos = ['MS','UA','WRCA']

    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False, remove_blank_text=True)

    xslFilename = 'stylesheets/aspace_oac.xslt'

    #loop through each repository's local directory for xml files
    for repo in repos:
        directory = os.fsencode(os.path.join(basedir,'raw_export\\',repo))
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith('.xml'):
                xml = etree.parse(os.fsencode(os.path.join(directory,file)))
                
                #apply xslt (does the majority of processing)
                xslt = etree.parse(xslFilename)
                transform = etree.XSLT(xslt)
                newXML = str(transform(xml))

                #python regex processing for things i couldn't figure out how to catch in xslt
                ##remove the namespace declarations within elements
                newXML = re.sub(r'xmlns:xs="http:\/\/www\.w3\.org\/2001\/XMLSchema"\s+xmlns:ead="urn:isbn:1-931666-22-9"','',newXML)
                #lowercase "linear feet"
                newXML = re.sub(r'Linear\s+Feet','linear feet',newXML)

                #write out to new file
                outpath = os.fsencode(os.path.join(basedir,'processed\\',repo,filename))
                f = codecs.open(outpath, 'w', 'utf-8')
                f.write(newXML)
                f.close()

                #print confirmation
                print(filename,' processed to ',outpath)
                sys.stdout.flush()