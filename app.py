from flask import Flask, jsonify, make_response, request, abort
import magic
from ocrlib import OCR
import requests
import boto3
import subprocess
from zappa.async import task


app = Flask(__name__)



@task
def get_text(file):
    r = requests.get(img)
    try:
        os.remove('/tmp/file')
    except OSError:
        pass
    with open('/tmp/file', 'wb') as f:
        f.write(r.content)
    if magic.from_file('/tmp/file', mime=True) == 'application/pdf':
        subprocess.call(['convert', '/tmp/file', '-append', '/tmp/file.png'])
    text = OCR.get_text('/tmp/file.png')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def ocr_lambda():
    get_text(request.args.get('file'))
    return {"msg": "Request Received"}


if __name__ == '__main__':
    app.run()
