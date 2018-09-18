from flask import Flask, jsonify, make_response, request, abort
from ocrlib import OCR


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def ocr_lambda():
    text = OCR.get_text('images/example_03.png')
    return text


if __name__ == '__main__':
    app.run()
