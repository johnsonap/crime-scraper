import os, simplejson
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    fo = open("foo.txt", "r+")
    suspects = simplejson.loads(fo.read())
    st = "<ul>"
    for suspect in suspects['suspects']:
        st += '<li><img src="' +suspect['img'] + '">' + suspect['name'] + '</li>'
    return st + '</ul>'
    
@app.route('/json')
def json():
    fo = open("foo.txt", "r+")
    return fo.read(), 200, {'Content-Type': 'text/plain'}