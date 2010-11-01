# -*- encoding: utf-8 -*-

import os
import time
import random

from redis import Redis

from tornado.web import (Application, RequestHandler, authenticated)
from tornado.escape import (json_encode, json_decode)
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer


def getrand():
    return random.randint(0, 2**15)


def encode_cookie(obj):
    return json_encode(obj).encode("base64").replace("\n", "")

def decode_cookie(obj):
    return json_decode(obj.decode("base64"))


class RedisAuthMixin(object):
    def get_current_user(self):
        user_json = self.get_cookie("auth", None)
        if not user_json:
            print "not login"
            return None
        print "login:ok", decode_cookie(user_json)
        return decode_cookie(user_json)


class WelcomeHandler(RequestHandler):
    def get(self):
        self.render("template/welcome.html", register_error=None, login_error=None)

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        # you can change host, port, db with keyword parameter
        if not username or not password:
            self.render("template/welcome.html", register_error=None, login_error=
                "You need to enter both username and password to login")
            return
        redis = Redis()
        userid = redis.get("username:%s:id" % username)
        if not userid:
            self.render("template/welcome.html", register_error=None, login_error=
                "Wrong username or password")
            return
        realpassword = redis.get("uid:%s:password" % userid)
        if realpassword != password:
            self.write("template/welcome.html", register_error=None, login_error=
                "Wrong username or password")
            return
        print "login ok"
        authsecret = redis.get("uid:%s:auth" % userid)
        user_info = {"id":userid, "name":username, "auth":authsecret}
        self.set_cookie("auth",encode_cookie(user_info), expires_days=365)
        self.redirect("/")


class RegisterHandler(RequestHandler):
    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        password2 = self.get_argument("password2", None)

        redis = Redis()
        error_message = None

        if not username or not password or not password2: 
            error_message = "Every field of the registration form is needed!"
        elif password != password2:
            error_message = "The two password fileds don't match!"
        elif redis.get("username:%s:id" % username):
            error_message = "Sorry the selected username is already in use."
        if error_message:
            self.render("template/welcome.html", login_error=None, register_error=error_message)
            return

        userid = redis.incr("global:nextuserId")
        redis.set("username:%s:id" % username, userid)
        redis.set("uid:%s:username" % userid, username)
        redis.set("uid:%s:password" % userid, password)

        authsecret = getrand()
        redis.set("uid:%s:auth" % userid, authsecret)
        redis.set("auth:%d" % authsecret, userid)

        redis.sadd("global:users", userid)

        user_info = {"id":userid, "name":username, "auth":authsecret}
        self.set_cookie("auth", encode_cookie(user_info), expires_days=365)

        self.render("template/register.html", username=username)


class LogoutHandler(RequestHandler, RedisAuthMixin):
    @authenticated
    def get(self):
        redis = Redis()
        newauthsecret = getrand()
        userid = self.current_user["id"]
        oldauthsecret = redis.get("uid:%s:auth" % userid)

        redis.set("uid:%s:auth" % newauthsecret)
        redis.set("auth:%s" % newauthsecret)
        redis.delete("auth:%s" % oldauthsecret)
        self.redirect("/")


class UpdateHandler(RequestHandler, RedisAuthMixin):
    @authenticated
    def post(self):
        # save status
        redis = Redis()
        userid = self.current_user["id"]
        postid = r.incr("blobal:nextPostId")
        status = self.get_argument("status").replace("\n", " ")
        post = "%s|%d|%s" % (userid, int(time.time()), status)
        redis.set("post:"+postid, post)

        # spread status to all followers
        followers = redis.smembers("uid:%s:followers" % userid)
        if not followers:
            followers = set()
        for fid in followers:
            redis.rpush("uid:%s:posts" % fid, postid) 
        redis.rpush("global:timeline", postid)
        redis.ltrim("global:timeline", 0, 1000)
        self.redirect("/")


class HomeHandler(RedisAuthMixin, RequestHandler):
    @authenticated
    def get(self):
        redis = Redis()
        user = self.current_user
        self.render("template/home.html", 
            username=user["name"],
            followers=redis.scard("uid:%s:followers" % user["id"]),
            following=redis.scard("uid:%s:following" % user["id"]),
            user_posts="")


settings = {
   "static_path": os.path.join(os.path.dirname(__file__), "static"),
   "login_url": "/welcome"
}


application = Application([
    (r"/", HomeHandler),
    (r"/welcome", WelcomeHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
], **settings)


if __name__ == "__main__":
    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()
