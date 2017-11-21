[:GET] /repositories/:repo_id/resources/marc21/:id.xml

example:
curl -H "X-ArchivesSpace-Session:$TOKEN" http://aspace.ucr.edu:8089/repositories/3/resources/marc21/189.xml


* in curl, have to use >> to save output to file
* find and replace in oxygen 
	* --_curl_--http://aspace.ucr.edu:8089/repositories/3/resources/marc21/[0-9]+\.xml
	* {"error":"Resource not found"}
	* XML header line
	* replace tag="534" with tag="534" 
	* replace ind2="7" tag="600" with ind2="0" tag="600"
	* replace ind2="7" tag="610" with ind2="0" tag="610"

