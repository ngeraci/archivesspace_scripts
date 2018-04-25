# ArchivesSpace scripts

a grab bag of scripts I've used with the ArchivesSpace API to automate various cleanup and export tasks. relatively messy, not under active maintenance, mostly shared here in the case they might be helpful reference for other novice archivist/programmers.

Currently working on a cleaner, more reusable set of tools for our Special Collections & Digital Initiatives workflows at [UCR Archives Tools](https://github.com/ngeraci/ucr_archivestools).

## Requirements
* [requests](http://docs.python-requests.org/en/master/)
* [lxml](http://lxml.de/)

## Authentication
for authentication, create a separate file called `secrets.py` in the following format:
```secrets.py
baseURL='your backend URL'
user='your username'
password='your password'
```

## Scripts
### alpha_subj.py
orders collection-level subject headings alphabetically, with topical, geographic and other headings grouped together first, then form/genre headings.

### aspace_cleanup.py
a giant hulking script that does a bunch of different cleanup requested in Dec. 2017 collection-level record update project, including note updates, date normalization, and container summary updates. want to eventually break it into smaller reusable pieces.

### ead_export.py
bulk export of EAD finding aids

### postprocess.py
clean up finding aids after export so that they display how we want them in the [Online Archive of California](http://www.oac.cdlib.org/). mainly uses lxml to call __stylesheets/aspace_oac.xslt__, also does a couple of quick & dirty regex replacements.

### iso639b_dict.py
a tiny function that returns a Python dictionary where English names of languages are the keys and and [ISO 639-2B](https://www.loc.gov/standards/iso639-2/php/code_list.php) codes are the values. imported in __postprocess.py__ for some markup stuff. 

## Acknowledgements & other resources
I figured out how to do most of this by looking at similar scripts written by [Lora Woodford](https://github.com/lorawoodford/python_scripts) and at the [Rockefeller Archive Center](https://github.com/RockefellerArchiveCenter/scripts/tree/master/archivesspace).
