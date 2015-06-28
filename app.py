from flask import Flask, Response, render_template, redirect, url_for, flash, request
from flask import make_response
from jinja2 import Template
import os
import json
import requests
import hmac
from hashlib import sha1, md5

app = Flask(__name__)

if 'DEPLOY_ENV' in os.environ and os.environ['DEPLOY_ENV'] != 'local':

    DEPLOY_ENV = os.environ['DEPLOY_ENV']
    DEBUG = True if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'true' else False
    GOODREADS_API_KEY = os.environ.get('GOODREADS_API_KEY')
    SHELFIE_ACCESS_KEY = os.environ.get('SHELFIE_ACCESS_KEY')
    SHELFIE_SECRET_KEY = os.environ.get('SHELFIE_SECRET_KEY')

else:

    DEPLOY_ENV = 'local'
    DEBUG = True
    try:
        from settings_local import *
    except ImportError:
        print '\nYou must create a settings_local.py file!\n'

def review_list_url(user_id, query_string):
    base = 'https://www.goodreads.com/review/list/'
    return base + str(user_id) + '?format=xml&key=' + GOODREADS_API_KEY + '&' + query_string

def review_show_url(review_id):
    return 'https://www.goodreads.com/review/show.xml?id=' + str(review_id) + '&key=' + GOODREADS_API_KEY

def hmac_auth(secret, value):
    return hmac.new(secret, value, sha1).digest().encode('base64')

def crt_date():
    from wsgiref.handlers import format_date_time
    from datetime import datetime
    from time import mktime

    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)

def request_with_auth(method, url, body, headers):
    HOST = 'apis.shelfie.com'
    md5sum = md5(body).hexdigest()
    content_type = headers['Content-Type']
    date = crt_date()
    headers['Date'] = date
    headers['Content-MD5'] = md5sum

    auth_value = '%s\n%s\n%s\n%s\n%s' % (method, md5sum, content_type, date, url)
    auth = 'hmac %s:%s' % (SHELFIE_ACCESS_KEY, hmac_auth(SHELFIE_SECRET_KEY, auth_value).strip())
    headers['Authorization'] = auth

    resp = requests.request(method, 'http://'+HOST+url, headers=headers, data=body)
    #resp.raise_for_status()
    return resp

def book_cover(isbn):
    headers = {'Content-Type': 'application/json'}
    response = request_with_auth('GET', '/codex/books/%s/cover?size=medium' % isbn, '', headers)
    response.raise_for_status()
    return response

@app.route('/')
def index():
    return 'go to /goodreads/USERID'

@app.route('/goodreads/<int:user_id>')
def dashboard(user_id):
	return render_template("dashboard.html", user_id=user_id)

@app.route('/currently-reading/<int:user_id>')
def show_current_book(user_id):
    url = review_list_url(user_id, 'v=2&shelf=currently-reading&sort=position&order=a')
    r = requests.get(url)
    return Response(r.content, mimetype='text/xml')

@app.route('/to-read/<int:user_id>')
def show_next_books(user_id):
    url = review_list_url(user_id, 'v=2&shelf=to-read&sort=position&order=a')
    r = requests.get(url)
    return Response(r.content, mimetype='text/xml')

@app.route('/cover/<int:isbn>')
def cover(isbn):
    r = book_cover(isbn)
    return Response(r.content, mimetype='img/jpeg')

@app.route('/review/<int:review_id>')
def review(review_id):
    r = requests.get(review_show_url(review_id))
    return Response(r.content, mimetype='text/xml')

if __name__ == '__main__':
	app.run(debug=True)