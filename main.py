import os
import webapp2
import jinja2
import urllib


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class MainPage(Handler):
	def get(self):
		blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

		self.render("front.html", blogs=blogs)


class Blog(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)


class NewPostPage(Handler):
	def render_newpost(self, subject="", content="", error=""):
		self.render("newpost.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_newpost()

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')

		if subject and content:
			b = Blog(subject = subject, content = content)
			b.put()
			blog_id = str(b.key().id())

			self.redirect("/%s" % blog_id)

		else:
			error = "We need both a subject and a blog!"
			self.render_newpost(subject, content, error)

class ShowSinglePost(Handler):
	def get(self, resource):
		blog_id = int(urllib.unquote(resource))
		blog = Blog.get_by_id(blog_id, parent=None)
		subject = blog.subject
		content = blog.content
		created = blog.created
		self.render("success.html", subject=subject, content=content, created=created)


app = webapp2.WSGIApplication([('/', MainPage), ('/newpost', NewPostPage), ('/([^/]+)?', ShowSinglePost)], debug=True)


