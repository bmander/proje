from google.appengine.ext import db

class Project(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()