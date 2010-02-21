from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Project(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    
class Nickname(db.Model):
    nickname = db.StringProperty()
    user = db.UserProperty()
    
class Scrap(polymodel.PolyModel):
    content = db.StringProperty()
    project = db.ReferenceProperty(Project)
    created = db.DateTimeProperty()
    
class LinkScrap( Scrap ):
    pass
    