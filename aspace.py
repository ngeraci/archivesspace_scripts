import requests
import json
import csv
import os

#Modify the ArchivesSpace backend url, username, and password as necessary
aspace_url = 'http://aspace.ucr.edu:8089'
username= 'ngeraci'
password = '2DamnPhones'

auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}