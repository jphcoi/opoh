from flask import Flask, render_template
from flask import request
import time
app = Flask(__name__)


import docker
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parsing')
def parsing():
    filename = request.args.get('filename')
    return 'filename is: '+str(filename)



@app.route('/run_docker')
def run_docker():
    client = docker.from_env()
    filename = request.args.get('filename')

    try:
        container = client.containers.run('opoh_docker', detach=True, environment={'File_Name': filename})
        # Wait for the script to finish executing
        container.wait()
        output = container.logs().decode('utf-8')
        #return f"Container ID: {container.id} started with parameter: {filename}, Output: {output}"
        return output
    except docker.errors.ContainerError as e:
        return f"Container failed to start. Error: {e.stderr.decode('utf-8')}", 500
    except docker.errors.ImageNotFound as e:
        return "Docker image not found.", 500
    except docker.errors.APIError as e:
        return f"Internal server error. Docker API error: {e}", 500
    except Exception as e:
        return f"An error occurred: {e}", 500

    #container = client.containers.run('jphcoi/opoh_docker', filename, detach=True, environment={'File_Name': filename})
    #return f"Container ID: {container.id} started with parameter: {filename}!"
