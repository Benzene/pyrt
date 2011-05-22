#!/usr/bin/env python

import cookielib
import Cookie
import cPickle as pickle
import os
import md5
import base64
import random
import string
import config

class User:
    def __init__(self, pass_hash, sess_id=None):
        self.password = pass_hash
        self.sess_id = sess_id
        #self.testing = testing
        
class Login:
    def __init__(self):
        c = config.Config()
        #get this from a pickled object
        #get pyrt root dir
        try:
            self.USER = pickle.load(open(".user.pickle"))
        except:
            #self.USER = User("mountainpenguin", self.hashPassword("testing"))
            self.USER = User(c.CONFIG.password)
        
    def _flush(self):
        pickle.dump(self.USER, open(".user.pickle", "w"))
        
    def checkPassword(self, pw):
        hash = self.USER.password
        salt = base64.b64decode(hash.split("$")[1])
        result = self.hashPassword(pw, salt=salt)
        if result == self.USER.password:
            return True
        else:
            return False
                
    def checkLogin(self, cookies):
        try:
            session_id = cookies.get("sess_id").value
            if session_id == self.USER.sess_id:
            #if session_id in self.USER.testing:
                return True
            else:
                return False
        except:
            return False
        
    def hashPassword(self, pw, salt=None):
        if not salt:
            salt = os.urandom(6)
        salt_encoded = base64.b64encode(salt)
        md5_1 = md5.new(pw).digest()
        md5_2 = md5.new(md5_1 + salt).digest()
        md5_encoded = base64.b64encode(md5_2)
        return "$%s$%s" % (salt_encoded, md5_encoded)
        
    def loginHTML(self, msg=""):
        return """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <title>rTorrent - webUI Login</title>
                <link rel="stylesheet" href="/css/main.css">
                <!-- <script type="text/javascript" src="/javascript/login.js"></script> -->
            </head>
            <body>
                <div id="login_div">
                    <div class="notice">%s</div>
                    <h1>Login to your rTorrent webUI</h1>
                    <form method="POST" action="">
                        <label>Enter Password: </label>
                        <input type="password" name="password">
                    </form>
                </div>
            </body>
        </html>
        """ % msg
        
    def sendCookie(self):
        randstring = "".join([random.choice(string.letters + string.digits) for i in range(20)])
        new_cookie = Cookie.SimpleCookie()
        new_cookie["sess_id"] = randstring
        #add sess_id to self.USER
        self.USER.sess_id = randstring
        #self.USER.testing += [randstring]
        self._flush()
        return new_cookie
