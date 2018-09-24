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
    subprocess.call(['convert', '-verbose', '-density', '150', '/tmp/file', '-quality', '100', '-sharpen', '0x1.0', '-append', '/tmp/file.png'])
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
        subprocess.call(['convert', '-verbose', '-density', '150', '/tmp/file', '-quality', '100', '-sharpen', '0x1.0', '-append', '/tmp/file.png'])
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
