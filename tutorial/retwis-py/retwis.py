# -*- encoding: utf-8 -*-

import os
import random
import hashlib

from time import time
from redis import Redis

from tornado.web import (Application, RequestHandler, authenticated)
from tornado.escape import (json_encode, json_decode
, url_escape)
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer


posttemplate = """
<div class="post">
    <a class="username" href="/profile?u=%s">%s</a>%s<br>
    <i>posted %s ago via web</i>
</div>
"""

def getrand():
    return random.getrandbits(32)


def encode_cookie(obj):
    return json_encode(obj).encode("base64").replace("\n", "")


def decode_cookie(obj):
    return json_decode(obj.decode("base64"))


class PostFormatter(object):
    def __init__(self, redis):
        self._redis = redis
        self._posts = []
        self._links = []
        self._is_last = False

    @property
    def post(self):
        return "\n".join(self._posts)
    
    @property
    def link(self):
        if not self._links:
            return ''
        return '<div class="rightlink">%s</div>' % " | ".join(self._links)

    def _elapsed(self, t):
        d = time()-int(t);
        if d < 60:
            return "%d seconds" % int(d)
        elif d < 120:
            return "1 minute"
        elif d < 3600:
            return "%d minutes" % int(d/60)
        elif d < 7200:
            return "1 hour"
        elif d < 3600 * 24:
            return "%d hours" % int(d/3600)
        elif d < 3600 * 48:
            return "1 day"
        else:
            return "%d days" % int(d/3600/24)

    def show_post(self, id):
        postdata = self._redis.get("post:%s" % id);
        if not postdata:
            return False;
        userid, time, post = postdata.split("|", 2)
        username = self._redis.get("uid:%s:username" % userid)
        self._posts.append(posttemplate % (url_escape(username), username, post, self._elapsed(time)))
        return True

    def show_user_posts(self, userid, start, count): 
        if userid == None:
            key = "global:timeline"
        else:
            key = "uid:%s:posts" % userid
        posts = self._redis.lrange(key, start, start+count)
        for post in posts:
            self.show_post(post)
            if len(self._posts) == count:
                break
        self._is_last = (len(self._posts) != count+1)

    def user_post_with_pagenation(self, path, username, userid, start, count):
        if username:
            userstr = '&u=%s' % url_escape(username)
        else:
            userstr = ""
        self.show_user_posts(userid, start, count)
        if start > 0:
            self._links.append('<a href="%s?start=%d" %s>&laquo; Newer posts</a>' % (
                path, max(start - 10, 0), userstr)) 
        if not self._is_last:
            self._links.append('<a href="%s?start=%d" %s>Older posts &raquo;</a>' % (
                path, start + 10, userstr))


class RedisAuthMixin(object):
    def get_current_user(self):
        user_json = self.get_cookie("auth", None)
        if not user_json:
            return None
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


class PostHandler(RedisAuthMixin, RequestHandler): 
    @authenticated
    def post(self):
        # save status
        redis = Redis()
        userid = self.current_user["id"]
        postid = redis.incr("blobal:nextPostId")
        status = self.get_argument("status").replace("\n", " ")
        post = "%s|%d|%s" % (userid, int(time()), status)
        redis.set("post:%d" % postid, post)

        # spread status to all followers
        followers = redis.smembers("uid:%s:followers" % userid)
        followers.add(userid)
        for fid in followers:
            redis.rpush("uid:%d:posts" % fid, postid) 
        redis.rpush("global:timeline", postid)
        redis.ltrim("global:timeline", 0, 1000)
        self.redirect("/")


class HomeHandler(RedisAuthMixin, RequestHandler):
    @authenticated
    def get(self):
        redis = Redis()
        user = self.current_user
        start = int(self.get_argument("start", "0"))
        formatter = PostFormatter(redis)
        path = self.request.path.split("?")[0]
        formatter.user_post_with_pagenation(path, None, user["id"], start, 10)
        self.render("template/home.html", 
            username=user["name"],
            followers=redis.scard("uid:%s:followers" % user["id"]),
            following=redis.scard("uid:%s:following" % user["id"]),
            user_posts=formatter.post, link=formatter.link)


class TimelineHandler(RequestHandler):
    def get(self):
        redis = Redis()
        formatter = PostFormatter(redis)
        formatter.show_user_posts(None, 0, 50)
        self.render("template/timeline.html",
            posts = formatter.post)


settings = {
   "static_path": os.path.join(os.path.dirname(__file__), "static"),
   "login_url": "/welcome"
}


application = Application([
    (r"/", HomeHandler),
    (r"/welcome", WelcomeHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/post", PostHandler),
    (r"/timeline", TimelineHandler),
], **settings)


if __name__ == "__main__":
    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()
