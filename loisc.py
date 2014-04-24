import httplib
import base64
import re
import datetime
import time
import os
from random import choice, randrange
from urllib import urlencode
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy import desc, create_engine
from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, MetaData, 
                        and_, desc, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (backref, joinedload, subqueryload, sessionmaker,
                            relationship)
from bottle import template, request, response, redirect, Bottle, debug, run

# INSERT SILLY COMMENT HERE
# You know, there is a lot of crazy crap that you can do with stuff...
# AgentBS says Find out what the Sumbitch needs and give it to him
#

Base = declarative_base()
engine = create_engine('sqlite:///barcodes.db')
Session = sessionmaker(engine)
app = Bottle()

class ShmooBall(Base):
    __tablename__ = 'barcode'
    barcode = Column(String, primary_key=True)
    user = Column(String)
    cookie = Column(String)
    
    def __init__(self, barcode, user_id, cookie=None):
        self.barcode = barcode
        self.user = user_id
        if cookie is not None:
            self.cookie = cookie
        else:
            self.register()
    
    def register(self):
        return self._login()
    
    def _login(self):
        return self._post('/register', {'barcode': self.barcode, 
                                 'nick': self.user})
    
    def _get(self, url, headers={}, cookie=False):
        if cookie:
            headers['Cookie'] = self.cookie
        http = httplib.HTTPConnection('moose.shmoocon.org')
        http.request('GET', url, headers=headers)
        resp = http.getresponse()
        if resp.getheader('set-cookie') is not None:
            self.cookie = resp.getheader('set-cookie')
        return resp.read()
    
    def _post(self, url, payload={}, headers={}, cookie=False):
        content = urlencode(payload)
        if cookie:
            headers['Cookie'] = self.cookie
        headers['Content-Length'] = len(content)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        http = httplib.HTTPConnection('moose.shmoocon.org')
        http.request('POST', url, body=content, headers=headers)
        resp = http.getresponse()
        if resp.getheader('set-cookie') is not None:
            self.cookie = resp.getheader('set-cookie')
        return resp.read()
    
    def throw(self, track):
        rex = re.compile(r'Headshot')
        self.register()
        data = self._post('/throw/%s' % track, payload={'lol': 1}, 
                          cookie=True, headers={'Referer': 'http://moose.shmoocon.org/throw/2'})
        if len(rex.findall(data)) > 0:
            return True
        else:
            return False
ShmooBall.metadata.create_all(engine)

@app.route('/')
def home_page():
    return "Low Orbit Ion Shmooball Cannon (LOISC)"

@app.route('/:balls/:victim')
def prepare_to_fire(balls, victim):
    response.headers['Content-Type'] = 'application/json'
    balls = int(balls)
    fails = 0
    thrown = 0
    s = Session()
    codes = s.query(ShmooBall).all()
    while balls > 0:
        time.sleep(0.5)
        if choice(codes).throw(victim):
            print 'Successfully Thrown Ball'
            balls -= 1
            thrown += 1
        else:
            print 'Ball Throw Failed'
            fails += 1
        if fails >= len(codes):
            balls = 0
    return '{"thrown": %s, "failed": %s}' % (thrown, fails)

def gen_cookies():
    s = Session()
    codes = open('loisc_codes.txt')
    for line in codes.readlines():
        time.sleep(1)
        name = 'loisc%s' % randrange(1000,9000)
        print name
        try:
            s.add(ShmooBall(line.strip('\n'), name))
            s.commit()
        except:
            print 'Code Exists.'
    s.close()

if __name__ == '__main__':
    if os.path.exists('loisc_codes.txt'):
        gen_cookies()
    else:
        debug(True)
        run(app=app, reloader=True, host='0.0.0.0', port=8085)
