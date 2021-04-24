import os
from urllib.parse import urlparse
from flask import request, Response, abort, g
from flask.app import Flask
import requests
import requests_cache

CACHE_VALIDITY_PERIOD = int(os.getenv('CACHE_VALIDITY_PERIOD', 600))

requests_cache.install_cache('loxodonta_cache', backend='sqlite', expire_after=CACHE_VALIDITY_PERIOD)

app = Flask(__name__)

def _make_request(url, params={}, headers = {}, use_tls=True):
    resp = requests.get(
        url=f'https://{url}' if use_tls else f'http://{url}',
        params=params,
        headers=headers,
        allow_redirects=False)
    return resp

@app.route('/p/<path:url>', methods=['GET'])
def proxy(url):
    headers = {k: v for (k, v) in request.headers if k != 'Host'}
    external_resp = _make_request(url, params={k: v for k, v in request.args.items()}, headers=headers)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'content-disposition']
    resp_headers = [(k, v) for k, v in external_resp.raw.headers.items() if k.lower() not in excluded_headers]
    return Response(
        external_resp.content,
        external_resp.status_code,
        resp_headers)
