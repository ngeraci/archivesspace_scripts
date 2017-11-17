import re

if recordtype == collectionlevel:

	#Add Resource Type
	if (p|P)apers in title:
		resourcetype = 'Papers'
	elif (r|R)ecords in title:
		resourcetype = 'Records'
	elif (c|C)ollection in title:
		resourcetype = 'Collection'
	else:
		resourcetype = Null

	#strip trailing period from date expression
    if '\.$' in dateexpression:
        dateexpression = dateexpression[:-1] #https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation

    #check date type & add normalized date
    if dateexpression contains '\-' or ','and dontcontain 'bulk': #are there any other characters that would indicate inclusive dates?
        datetype = 'Inclusive Dates'
    elif 'bulk' in dateexpression:
        datetype = 'Bulk Dates'
    else:
        datetype = 'Single'

    #what does "check extent" mean? can a computer do it?

    #remove type of boxes from container summary, put in parenthesis
    containersummarynumber = ^[0-9]+ #use regex to get numeric value from beginning of summary
    if containersummarynumber == 1:
        containersummary = '(' + str(containersummarynumber) + 'box' + ')'
    else:
        containersummary = '(' str(containersummarynumber) + 'boxes' + ')'
        #are there any where this wouldn't work? ie if it says cartons, or another word?

    #take out 'guide to the' from finding aid title
    if findingaidtitle startswith 'Guide to the ':
        findingaidtitle = findingaidtitle[14:] # trim first 13 chars

    #check agents against lcnaf : does it make sense to do this at indiv. collection level?

    #check subjects (against lcsh) : does it make sense to do this at indiv. collection level?

    # put subjects in put in alpha order by subj, then genre form : not sure how to do this // do we need to do this here if it's also happening in export?

    #update accessnote
    accessnote = 'This collection is unprocessed. Please contact Special Collections & University Archives regarding the availability of materials for research use.'

    #update conditionsgoverninguse
    conditionsgoverninguse = re.sub('Head of Special Collections', 'Director of Distinctive Collections', conditionsgoverninguse) #regex substitution

    #preferred citation - tackle this later 

    #delete processinghistory note
    processinghistory = Null

    #s&c label
    scopecontentlabel = 'Collection Scope and Contents'