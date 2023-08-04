This repo collects a set of python scripts for parsing and enriching transcript data for the OPOH project. 
Right now, only one script if operational: parse_SYNC.py. 

All the required instructions to dockerize the scripts and run them on a server are also included in the Dockerfile. 
Simply type: `docker build -t opoh_docker`

And run it using the following syntax
`docker run -e File_Name="SOMEFILE.docx"  opoh_docker`

The docker image can then be called from a FLASK API 
Just type flask run to start the service, indicating the file path in the URL (parameter=filename). The HTML page will deliver the resulting JSON object. 

`http://127.0.0.1:5000/run_docker?filename=SOMEFILE.docx`

