This repo collects a set of python scripts for parsing and enriching transcript data for the OPOH project. 
Right now, only the parsing script is operational: parse_SYNC.py. 

All the required instructions to dockerize the scripts and run them on a server are also included in the Dockerfile. 
Simply type: `docker build -t opoh_docker` to build the docker image

You can run directly run this image using the following syntax
`docker run -e File_Name="SOMEFILE.docx"  opoh_docker`

Alternatively it can also be launched using a FLASK API 
Type `flask run` to start the service, indicating the file path in the URL (parameter=filename). The HTML page will deliver the resulting JSON object. 

`http://127.0.0.1:5000/run_docker?filename=SOMEFILE.docx`

