#!/usr/bin/python

from flask import Flask, jsonify, request, render_template
import json, ast
import os
import logging


data_json = ''
api_post_message = {'data':'error'}
SYSTEM_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_message(): # NEED GLOBAL !!!!!!!!!!!!!!!!!!!!!!!!
    FILE_PATH = SYSTEM_SCRIPT_DIR + '/buffers/api_output_data_buffer.txt'
    with open(FILE_PATH) as json_file:
        CFG_json_object = json.load(json_file)
        CFG_json_object = ast.literal_eval(json.dumps(CFG_json_object))
        #
        global api_post_message
        #
        if CFG_json_object != None or CFG_json_object != '':
            api_post_message = CFG_json_object
        else:
            api_post_message = {'data':'error'}

def post_message(data):
    FILE_PATH = SYSTEM_SCRIPT_DIR + '/buffers/api_input_data_buffer.txt'
    with open(FILE_PATH, 'w') as outfile:
        json.dump(data, outfile)

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = False
log.setLevel(logging.ERROR)

@app.route('/api/v1', methods=['GET', 'POST'])
def hello():

# POST request
    if request.method == 'POST':
        post_message(request.get_json())
        return 'OK', 200

# GET request
    else:
        get_message()
        message = api_post_message #{'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers

@app.route('/test')
def test_page():
    # look inside `templates` and serve `index.html`
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='5000')

