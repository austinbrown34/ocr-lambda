from flask import Flask, jsonify, make_response, request, abort
import magic
from ocrlib import OCR
import requests
import boto3
import subprocess
import datetime
import time
import os
from zappa.async import task


app = Flask(__name__)

session = boto3.Session()
s3 = session.resource('s3')
bucket = 'ocr-lambda-text'


@task
def upload_text(text):
    try:
        os.remove('/tmp/text.txt')
    except OSError:
        pass
    with open('/tmp/text.txt', 'w') as f:
        f.write(text)

    s3.meta.client.upload_file(
        '/tmp/text.txt',
        bucket,
        'text-{}.txt'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    )


@task
def get_text(file):
    r = requests.get(file)
    try:
        os.remove('/tmp/file')
    except OSError:
        pass
    with open('/tmp/file', 'wb') as f:
        f.write(r.content)
    if magic.from_file('/tmp/file', mime=True) != 'image/png':
        subprocess.call(['convert', '/tmp/file', '-append', '/tmp/file.png'])
    else:
        os.rename('/tmp/file', '/tmp/file.png')
    text = OCR.get_text('/tmp/file.png')
    upload_text(text)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def ocr_lambda():
    get_text(request.args.get('file'))
    return "Request Received"


if __name__ == '__main__':
    app.run()
