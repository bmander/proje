from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Project(db.Model):
    user    = db.UserProperty()
    name    = db.StringProperty()
    updated = db.DateTimeProperty()
    
class Nickname(db.Model):
    nickname = db.StringProperty()
    user = db.UserProperty()
    
class Scrap(polymodel.PolyModel):
    content = db.StringProperty()
    project = db.ReferenceProperty(Project)
    created = db.DateTimeProperty()
    creator = db.UserProperty()
    
class LinkScrap( Scrap ):
    icon    = db.BlobProperty()
    
class FeedScrap( LinkScrap ):
    pass
    