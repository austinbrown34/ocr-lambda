from flask import Flask, jsonify, make_response, request, abort
from ocrlib import OCR
import requests

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def ocr_lambda():
    img = request.args.get('img')
    r = requests.get(img)
    with open('/tmp/img.png', 'wb') as f:
        f.write(r.content)
    text = OCR.get_text('/tmp/img.png')
    return text


if __name__ == '__main__':
    app.run()
