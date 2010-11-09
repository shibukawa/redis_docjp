# -*- encoding: utf-8 -*-

import os
import random
import hashlib

from time import time
from redis import Redis

from tornado.web import (Application, RequestHandler, authenticated)
from tornado.escape import url_escape
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer


def getrand():
    bitstr = ""
    for i in range(16):
        bitstr += chr(random.getrandbits(8))
    return hashlib.md5(bitstr).hexdigest()


# <= begin user code



# => end user code 


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
        redis.set("auth:%s" % authsecret, userid)
        redis.sadd("global:users", userid)
        self.set_cookie("auth", authsecret, expires_days=365)

        self.render("template/register.html", username=username)




class HomeHandler(RedisAuthMixin, RequestHandler):
    @authenticated
    def get(self):
        redis = Redis()
        userid = self.current_user
        start = int(self.get_argument("start", "0"))
        formatter = PostFormatter(redis)
        path = self.request.path.split("?")[0]
        formatter.user_post_with_pagenation(path, None, userid, start, 10)
        self.render("template/home.html", 
            username=self.current_user["name"],
            followers=redis.scard("uid:%s:followers" % userid),
            following=redis.scard("uid:%s:following" % userid),
            user_posts=formatter.post, link=formatter.link)


class TimelineHandler(RequestHandler):
    def get(self):
        redis = Redis()
        formatter = PostFormatter(redis)
        formatter.show_user_posts(None, 0, 50)
        self.render("template/timeline.html",
            posts = formatter.post)


class ProfileHandler(RedisAuthMixin, RequestHandler):
    @authenticated
    def get(self):
        redis = Redis()
        username = self.get_argument("u")
        userid = redis.get("username:%s:id" % username)
        if not userid:
            self.redirect("/")
        else:
            isfollowing = redis.sismember(
                "uid:%s:following" % self.current_user["id"],userid);
            self.render("template/profile.html",
                isfollowing = isfollowing, userid = userid, username = username)


class FollowHandler(RedisAuthMixin, RequestHandler):
    @authenticated
    def get(self):
        redis = Redis()
        userid = self.get_argument("uid")
        flag = self.get_argument("f")
        username = redis.get("uid:%s:username" % userid)
        if userid is not None and flag is not None:
            myuserid = self.current_user["id"]
            if userid != myuserid:
                if flag == "0":
                    redis.sadd("uid:%s:followers" % userid, myuserid)
                    redis.sadd("uid:%s:following" % myuserid, userid)
                else:
                    redis.srem("uid:%s:followers" % userid, myuserid)
                    redis.srem("uid:%s:following" % myuserid, userid)
        self.redirect("/")


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
        raise NotImplemented("please implement this method")

    def show_user_posts(self, userid, start, count): 
        raise NotImplemented("please implement this method")

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
    (r"/profile", ProfileHandler),
    (r"/follow", FollowHandler),
], **settings)


if __name__ == "__main__":
    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()
