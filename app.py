from flask import Flask, jsonify, make_response, request, abort
import magic
from ocrlib import OCR
from pypdflib import PDFExtractor
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
converted_bucket = 'ocr-lambda-converted'
pages_bucket = 'ocr-lambda-pages'


@task
def convert(file):
    r = requests.get(file)
    try:
        os.remove('/tmp/file')
    except OSError:
        pass
    with open('/tmp/file', 'wb') as f:
        f.write(r.content)
    subprocess.call(['convert', '-verbose', '-density', '150', '-trim', '/tmp/file', '-quality', '100', '-flatten', '-sharpen', '0x1.0', '-append', '/tmp/file.png'])
    upload('/tmp/file.png', converted_bucket, 'png-{}.png'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))


@task
def upload(local_file, bucket, s3_file):
    s3.meta.client.upload_file(
        local_file,
        bucket,
        s3_file
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
        subprocess.call(['convert', '-verbose', '-density', '150', '-trim', '/tmp/file', '-quality', '100', '-flatten', '-sharpen', '0x1.0', '-append', '/tmp/file.png'])
    else:
        os.rename('/tmp/file', '/tmp/file.png')
    text = OCR.get_text('/tmp/file.png')
    try:
        os.remove('/tmp/text.txt')
    except OSError:
        pass
    with open('/tmp/text.txt', 'w') as f:
        f.write(text)
    upload('/tmp/text.txt', bucket, 'text-{}.txt'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))


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
def convert():
    if request.method == 'GET':
        file = request.args.get('file')
    elif request.method == 'POST':
        if not (request.json):
            abort(400)
        file = request.json['file']
    convert(file)
    return "Request Received"


if __name__ == '__main__':
    app.run()
