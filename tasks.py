import magic
from ocrlib import OCR
from pypdflib import PDFExtractor
import requests
import boto3
import subprocess
import datetime
import time
import os
import shutil
from zappa.async import task
from natsort import natsort_keygen, ns


session = boto3.Session()
s3 = session.resource('s3')
bucket = 'ocr-lambda-text'
converted_bucket = 'ocr-lambda-converted'
pages_bucket = 'ocr-lambda-pages'
do_parallel_url = 'https://2jnc0k39k9.execute-api.us-west-2.amazonaws.com/dev/v1/job'
do_parallel_callback = 'https://ahs8ek59h2.execute-api.us-west-2.amazonaws.com/dev/finish'
task_url = 'https://ahs8ek59h2.execute-api.us-west-2.amazonaws.com/dev'


@task
def finish(payload):
    text = ''
    for x in range(len(payload.keys())):
        text += payload["task{}".format(x)]['result']
    try:
        os.remove('/tmp/text.txt')
    except OSError:
        pass
    with open('/tmp/text.txt', 'w') as f:
        f.write(str(text))
    upload('/tmp/text.txt', bucket, 'completed-{}.txt'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))


@task
def process(file):
    # pages = get_pages(file)
    r = requests.get(file)
    try:
        os.remove('/tmp/file')
    except OSError:
        pass
    with open('/tmp/file', 'wb') as f:
        f.write(r.content)
    num_pages = PDFExtractor.total_pages('/tmp/file')
    payload = {
        "callback": do_parallel_callback,
        "tasks": []
    }
    for page in range(num_pages):
        payload["tasks"].append(
            {
                "endpoint": task_url,
                "params": {
                    "file": file,
                    "page_num": int(page + 1)
                }
            }
        )
    requests.post(do_parallel_url, json=payload)


@task
def split(file):
    get_pages(file)


def get_pages(file):
    try:
        shutil.rmtree('/tmp/pages')
    except OSError:
        pass
    os.mkdir('/tmp/pages')
    r = requests.get(file)
    try:
        os.remove('/tmp/file')
    except OSError:
        pass
    with open('/tmp/file', 'wb') as f:
        f.write(r.content)
    PDFExtractor.get_pages('/tmp/file', '/tmp/pages')
    pages = []
    dir_pages = os.listdir('/tmp/pages')
    natsort_key = natsort_keygen(alg=ns.IGNORECASE)
    dir_pages.sort(key=natsort_key)
    for page in dir_pages:
        dst = os.path.join('/tmp/pages', page)
        key = '{}-{}.pdf'.format(page, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        upload(dst, pages_bucket, key)
        # https://s3.amazonaws.com/ocr-lambda-pages/file_page_2.pdf-2018-09-24+19%3A31%3A03.pdf
        pages.append('https://s3.amazonaws.com/{}/{}'.format(
            pages_bucket,
            key
        ))
    return pages


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


def upload(local_file, bucket, s3_file):
    content_type = magic.from_file(local_file, mime=True)
    s3.meta.client.upload_file(
        local_file,
        bucket,
        s3_file,
        {'ACL': 'public-read', 'ContentType': content_type}
    )


@task
def get_text(file, payload=None, page_num=None):
    r = requests.get(file)
    try:
        os.remove('/tmp/file')
    except OSError:
        pass
    with open('/tmp/file', 'wb') as f:
        f.write(r.content)
    if page_num is not None:
        try:
            shutil.rmtree('/tmp/pages')
        except OSError:
            pass
        os.mkdir('/tmp/pages')
        os.rename('/tmp/file', '/tmp/tmp_file')
        page = PDFExtractor.get_page('/tmp/tmp_file', '/tmp/pages/', page_num)
        os.rename(page, '/tmp/file')
    text = ""
    if magic.from_file('/tmp/file', mime=True) == 'application/pdf':
        text = PDFExtractor.get_text('/tmp/file')
        if not text:
            if magic.from_file('/tmp/file', mime=True) != 'image/png':
                subprocess.call(['convert', '-verbose', '-density', '150', '/tmp/file', '-quality', '100', '-sharpen', '0x1.0', '-append', '/tmp/file.png'])
            else:
                os.rename('/tmp/file', '/tmp/file.png')
            text = OCR.get_text('/tmp/file.png')
    else:
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
        f.write(str(text))
    upload('/tmp/text.txt', bucket, 'text-{}.txt'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
    result = str(text)
    if payload is not None:
        payload['result'] = result
        requests.post(
            payload['submit_work_url'],
            json=payload
        )
