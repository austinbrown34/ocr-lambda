from flask import Flask, jsonify, make_response, request, abort
from tasks import convert, get_text, get_pages


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
        file = request.json['file']
    get_text(file)
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
    get_pages(file)
    return "Request Received"


if __name__ == '__main__':
    app.run()
