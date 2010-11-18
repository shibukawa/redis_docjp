var util = require('util'),
    path = require('path'),
    http = require('http'),
    crypto = require('crypto');

var express = require('express'),
    redis = require('redis').createClient();

function getrand(){
   var bitstr = "";
   for(var i=0; i<16; i++){
      bitstr += String.fromCharCode(Math.random() * 256);
   }
   return crypto.createHash('md5').update(bitstr).digest('hex');
}

function Application(routes, settings){
   var app = express.createServer();
   app.configure(function(){
      app.use(express.cookieDecoder());
      app.use(express.bodyDecoder());
      if( settings.staticPath ){
         app.use(express.staticProvider(settings.staticPath));
      }
      if( settings.templatePath ){
         app.set('views', settings.templatePath);
      }
      if( settings.loginUrl ){
         app.set('loginUrl', settings.loginUrl);
      }

      app.dynamicHelpers({
         logout: function(req, res){
            return req.currentUser != null;
         }
      });

      app.use(app.router);
   });

   // mount routes
   for(var i=0, len=routes.length; i<len; i++){
      var map = routes[i];
      var path = map[0];
      var handler = map[1];
      ['get', 'post', 'put', 'del'].forEach(function(method){
         if( typeof handler[method] === 'function' ){
            app[method](path, handler[method]);
         }
      });
   }

   return app;
}

http.IncomingMessage.prototype.getCurrentUser = function(callback){
   var self = this;
   var authcookie = self.cookies.auth;
   if( authcookie ){
      redis.get("auth:" + authcookie, function(err1, userid){
         if( userid ){
            redis.get("uid:" + userid + ":auth", function(err2, authsecret){
               if( authsecret == authcookie ){
                  redis.get("uid:" + userid + ":username", function(err3, username){
                     self._currentUser = {
                        id: userid.toString(),
                        name: username.toString()
                     };
                     callback(null, self._currentUser);
                  });
               }else{
                  callback(null, null);
               }
            });
         }else{
            callback(null, null);
         }
      });
   }else{
      callback(undefined, null);
   }
}

http.IncomingMessage.prototype.__defineGetter__('currentUser', function(){
   return this._currentUser;
});

function authenticated(fun){
   return function(req, res){
      req.getCurrentUser(function(err, user){
         if( user ){
            fun(req, res);
         }else{
            // app.set(name) returns the value of name ...
            var url = req.app.set('loginUrl');
            res.redirect(url);
         }
      });
   };
}


var WelcomeHandler = {
   get: function(req, res){
      res.render('welcome.ejs', {
         locals: {
            loginError: null,
            registerError: null
         }
      });
   },
   post: function(req, res){
      var username = req.param('username');
      var password = req.param('password');
      if( !username || !password ){
         res.render('welcome.ejs', {
            locals: {
               loginError: "You need to enter both username and password to login",
               registerError: null
            }
         });
      }
      redis.get("username:" + username + ":id", function(err, userid){
         if( !userid ){
            res.render('welcome.ejs', {
               locals: {
                  loginError: "Wrong username or password",
                  registerError: null
               }
            });
         }else{
            redis.get("uid:" + userid + ":password", function(err, realpassword){
               if( realpassword != password ){
                  res.render('welcome.ejs', {
                     locals: {
                        loginError: "Wrong username or password",
                        registerError: null
                     }
                  });
               }else{
                  redis.get("uid:" + userid + ":auth", function(err, authsecret){
                     res.cookie("auth", authsecret, {expires: new Date(Date.now() + 31536000000)});
                     res.redirect('/');
                  });
               }
            });
         }
      });
   }
};

var RegisterHandler = {
   post: function(req, res){
      var username = req.param('username');
      var password = req.param('password');
      var password2 = req.param('password2');

      var errorMessage;
      if( !username || !password || !password2 ){
         errorMessage = "Every field of the registration form is needed!";
      }else if( password !== password2 ){
         errorMessage = "The two password fileds don't match!";
      }
      if( errorMessage ){
         res.render('welcome.ejs', {
            locals: {
               loginError: null,
               registerError: errorMessage
            }
         });
      }else{
         redis.get("username:" + username + ":id", function(err, userid){
            if( userid ){
               res.render('welcome.ejs', {
                  locals: {
                     loginError: null,
                     registerError: "Sorry the selected username is already in use."
                  }
               });
            }else{
               redis.incr("global:nextuserId", function(err, userid){
                  redis.set("username:" + username + ":id", userid);
                  redis.set("uid:" + userid + ":username", username);
                  redis.set("uid:" + userid + ":password", password);
                  var authsecret = getrand();
                  redis.set("uid:" + userid + ":auth", authsecret);
                  redis.set("auth:" + authsecret, userid);
                  redis.sadd("global:users", userid);
                  res.cookie("auth", authsecret, {expires: new Date(Date.now() + 31536000000)});
                  res.render('register.ejs', {
                     locals: {
                        username: username
                     }
                  });
               });
            }
         });
      }
   }
};

var HomeHandler = {
   get: authenticated(function(req, res){
      var userid = req.currentUser.id;
      var start = parseInt(req.param('start')) || 0;
      var path = req.url.split("?")[0];
      var formatter = new PostFormatter();
      formatter.userPostWithPagenation(path, null, userid, start, 10, function(){
         redis.scard("uid:" + userid + ":followers", function(err, followers){
            redis.scard("uid:" + userid + ":following", function(err, following){
               res.render('home.ejs', {
                  locals : {
                     username: req.currentUser.name,
                     followers: followers,
                     following: following,
                     userPosts: formatter.post,
                     link: formatter.link
                  }
               });
            });
         });
      });
   })
};


var LogoutHandler = {
   get: authenticated(function(req, res){
      var userid = req.currentUser.id;
      var newauthsecret = getrand();
      redis.get("uid:" + userid + ":auth", function(err, oldauthsecret){
         redis.set("uid:" + userid + ":auth", newauthsecret);
         redis.set("auth:" + newauthsecret, userid);
         redis.del("auth:" + oldauthsecret);
         res.redirect("/");
      });
   })
};

var PostHandler = {
   post: authenticated(function(req, res){
      var self = this;
      var userid = req.currentUser.id;
      var status = req.param('status').replace(/\n/g, " ");
      var post = [userid, Date.now(), status].join("|");
      redis.incr("global:nextPostId", function(err, postid){
         // related resources pushed into redis withought blocking
         redis.set("post:" + postid, post);
         redis.smembers("uid:" + userid + ":followers", function(err, followers){
            if( !followers ){
               followers = [];
            }
            followers.push(userid);
            followers.forEach(function(fid){
               redis.lpush("uid:" + fid + ":posts", postid);
            });
            redis.lpush("global:timeline", postid);
            redis.ltrim("global:timeline", 0, 1000);
         });
         res.redirect("/");
      });
   })
};

var TimelineHandler = {
   get: function(req, res){
      var formatter = new PostFormatter();
      formatter.showUserPosts(null, 0, 50, function(err){
         res.render('timeline.ejs', {
            locals: {
               posts: formatter.post
            }
         });

      });
   }
};

var ProfileHandler = {
   get: authenticated(function(req, res){
      var username = req.param('u');
      redis.get("username:" + username + ":id", function(err, userid){
         if( !userid ){
            res.redirect("/");
         }else{
            redis.sismember("uid:" + req.currentUser.id + ":following", function(err, isfollowing){
               res.render("profile.ejs", {
                  locals: {
                     isfollowing: isfollowing !== undefined,
                     userid: userid,
                     username: username
                  }
               });
            });
         }
      });
   })
};

var FollowHandler = {
   get: authenticated(function(req, res){
      var userid = req.param("uid");
      var flag = req.param("f");
      if( userid && flag ){
         var myuserid = req.currentUser.id;
         if( userid != myuserid ){
            var command = (flag == "0") ? "sadd" : "srem";
            redis[command]("uid:" + userid + ":followers", myuserid);
            redis[command]("uid:" + myuserid + ":following", userid);
         }
      }
      res.redirect("/");
   })
};

function PostFormatter(){
   this._posts = [];
   this._links = [];
   this._isLast = false;
}

PostFormatter.prototype.__defineGetter__("post", function(){
   return this._posts.join("\n");
});

PostFormatter.prototype.__defineGetter__("link", function(){
   if( this._links ){
      return '<div class="rightlink">' +
         this._links.join(" | ") +
         '</div>';
   }else{
      return '';
   }
});

PostFormatter.prototype._elapsed = function(t){
   var d = Date.now() - t;
   if( d < 60000 ){
      return parseInt(d/1000) + " seconds";
   }else if( d < 120000 ){
      return "1 minute";
   }else if( d < 3600000 ){
      return parseInt(d/60000) + " minutes";
   }else if( d < 7200000 ){
      return "1 hour";
   }else if( d < 3600000 * 24 ){
      return parseInt(d/3600000) + " hours";
   }else if( d < 3600000 * 48 ){
      return "1 day";
   }else{
      return parseInt(d/3600000/24) + " days";
   }
}

PostFormatter.prototype.showPost = function(id, callback){
   var self = this;
   redis.get("post:" + id, function(err, postdata){
      if( postdata ){
         postdata = postdata.toString();
         var s = postdata.split('|');
         var userid = s.shift(), time = s.shift(), post = s.join('|');
         redis.get("uid:" + userid + ":username", function(err, username){
            self._posts.push('<div class="post">' +
                             '<a class="username" href="/profile?u=' + encodeURIComponent(username) + '">' + username + '</a>' + post + '<br>' +
                             '<i>posted ' + self._elapsed(parseInt(time)) + ' ago via web</i>' +
                             '</div>');
            callback(null, userid, time, post);
         });
      }else{
         callback(null, null, null, null);
      }
   });
}

PostFormatter.prototype.showUserPosts = function(userid, start, count, callback){
   var self = this;
   if( userid ){
      var key = "uid:" + userid + ":posts";
   }else{
      var key = "global:timeline";
   }
   redis.lrange(key, start, start+count, function(err, posts){
      var len = posts == null ? 0 : posts.length;
      self._isLast = (len != count + 1);
      // recursive call for PostFormatter#showPost
      function showPost(i){
         if( i == len ){
            callback(null); // finally call the callback
         }else{
            var post = posts[i];
            self.showPost(post, function(){
               showPost(i+1);
            });
         }
      }
      showPost(0);
   });
}


PostFormatter.prototype.userPostWithPagenation = function(path, username, userid, start, count,
                                                          callback){
   var self = this;
   if( username ){
      var userstr = '&u=' + encodeURIComponent(username);
   }else{
      var userstr = "";
   }
   this.showUserPosts(userid, start, count, function(){
      if( start > 0 ){
         self._links.push('<a href="' + path + '?start=' + Math.max(start-10, 0) + userstr + '">&laquo; Newer posts</a>');
      }
      if( !self._isLast ){
         self._links.push('<a href="' + path + '?start=' + (start + 10) + userstr + '">Older posts &raquo;</a>');
      }
      callback(null);
   });
}



var settings = {
   staticPath : path.join(__dirname, "static"),
   templatePath : path.join(__dirname, "template"),
   loginUrl: "/welcome"
}

var app = Application([
   ["/", HomeHandler],
   ["/welcome", WelcomeHandler],
   ["/logout", LogoutHandler],
   ["/register", RegisterHandler],
   ["/post", PostHandler],
   ["/timeline", TimelineHandler],
   ["/profile", ProfileHandler],
   ["/follow", FollowHandler]
], settings);
app.listen(8888);
