from flask import Flask, jsonify, make_response, request, abort
from tasks import convert, get_text, split, process, finish


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET', 'POST'])
def ocr_lambda():
    if request.method == 'GET':
        file = request.args.get('file')
    elif request.method == 'POST':
        if not (request.json):
            abort(400)
        print("this is the json")
        print(request.json)
        file = request.json['params']['file']
        # submit_work_url = request.json['submit_work_url']
    get_text(file, payload=request.json)
    return "Request Received"


@app.route('/finish', methods=['GET', 'POST'])
def finish_lambda():
    if request.method == 'GET':
        payload = request.args.get('payload')
    elif request.method == 'POST':
        if not (request.json):
            abort(400)
        payload = request.json
    finish(payload)
    return "Request Received"


@app.route('/convert', methods=['GET', 'POST'])
def convert_lambda():
    if request.method == 'GET':
        file = request.args.get('file')
    elif request.method == 'POST':
        if not (request.json):
            abort(400)
        file = request.json['file']
    convert(file)
    return "Request Received"


@app.route('/split', methods=['GET', 'POST'])
def split_lambda():
    if request.method == 'GET':
        file = request.args.get('file')
    elif request.method == 'POST':
        if not (request.json):
            abort(400)
        file = request.json['file']
    split(file)
    return "Request Received"


@app.route('/process', methods=['GET', 'POST'])
def process_lambda():
    if request.method == 'GET':
        file = request.args.get('file')
    elif request.method == 'POST':
        if not (request.json):
            abort(400)
        file = request.json['file']
    process(file)
    return "Request Received"


if __name__ == '__main__':
    app.run()
