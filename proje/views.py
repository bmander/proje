from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response
from google.appengine.api import users
import logging
from django.utils import simplejson as json
from google.appengine.ext.db import GeoPt
from models import Project, Nickname, Scrap, LinkScrap, FeedScrap, FeedItemScrap
import datetime
import urlparse
from google.appengine.api import urlfetch, images
from google.appengine.api.urlfetch import DownloadError
from utils import get_projects_with_scraplists
import feedparser

def membersonly(f):
    def new_f(request, *args, **kwargs):
        
        user = users.get_current_user()
        if user:
            return f(request, user, *args, **kwargs)
        else:
            return HttpResponseRedirect( "/welcome" )
    
    return new_f
    
def usercontext(f):
    def new_f(request, *args, **kwargs):
        
        user = users.get_current_user()
        
        if user:
            logout_url = users.create_logout_url("/welcome")
            login_url = None
        else:
            login_url = users.create_login_url("/")
            logout_url = None 
            
        return f(request, {'user':user, 'login_url':login_url, 'logout_url':logout_url}, *args, **kwargs)
        
    return new_f

def welcome(request):
    user = users.get_current_user()
    
    if user:
        enter_url="/"
    else:
        enter_url=users.create_login_url("/")
        
    user_count = Nickname.all().count()
    project_count = Project.all().count()
    
    return render_to_response( "welcome.html", {'enter_url':enter_url, 'user_count':user_count, 'project_count':project_count} )
    
@usercontext
def learn(request, context):
    
    return render_to_response( "learn.html", context )
    
@membersonly
@usercontext
def home(request, context, user):
    # if we haven't already created a Nickname for this google account's current nickname, create one
    if Nickname.all().filter("nickname =", user.nickname()).count() == 0:
        Nickname(user=user, nickname=user.nickname()).put()
        
    projects = get_projects_with_scraplists( user )
    
    context['user'] = user
    context['projects'] = projects
    return render_to_response( "home.html", context )
    
@membersonly
def add_project(request, user):
    
    if request.method=="POST":
        # process form
        
        # fail if the name is blank
        name = request.POST['name'].strip()
        if name == "":
            return HttpResponseRedirect( "?error=the+name+needs+to+contain+letters" )
        project = Project(user=user,name=name,updated=datetime.datetime.now())
        project.put()
        
        logging.info( project.key().id() )
        
        # return rendered project div
        return render_to_response( "includes/project_div.html", {'project':{'name':project.name,'id':project.key().id()}} )
    
    return render_to_response( "add_project.html", {'error':request.GET.get('error',None)} )
    
@membersonly
def delete_project( request, user, id ):
    project = Project.get_by_id(int(id))
    
    if project.user != user:
        return HttpResponseForbidden( "<html><body>That doesn't belong to you</body></html>" )
    
    project.delete()
    
    return HttpResponseRedirect( "/" )

@usercontext
def project(request, context, id):
    project = Project.get_by_id(int(id))
    context['project']=project
    
    scraps = Scrap.all().filter("project =", project).order("-created")
    context['scraps'] = scraps
    
    return render_to_response( "project.html", context )
    
@usercontext
def user(request, context, nickname):
    # get a user from the nickname
    nickname = Nickname.all().filter("nickname =", nickname).get()
    
    if nickname is None:
        return HttpResponseNotFound( "No such user" )
        
    projects = get_projects_with_scraplists( nickname.user )
    
    context.update( {'subject_user':nickname.user,'projects':projects} )
    
    # get projects from the user
    return render_to_response( "user.html", context )

@membersonly
def add_scrap(request, user):
    
    if not ('content' and 'projectid' in request.POST):
        return HttpResponseServerError( "You must include both content and a project id" )
    
    logging.info( str( request.POST ) );
    
    # get project_id
    projectid = int(request.POST['projectid'])
    
    # get project
    project = Project.get_by_id( projectid )
    
    if project is None:
        return HttpResponseNotFound( "Could not find project with id %s"%projectid )
    
    # project needs to be owned by the current user
    if project.user != user:
        return HttpResponseForbidden( "This project is owned by %s. You are %s. They're not the same."%(project.user, user) )
    
    # scrap content needs to be non-blank
    scrap_content = request.POST['content']
    if scrap_content.strip()=="":
        return HttpResponseServerError( "The scrap content needs to have <i>characters</i>" )
    
    # if it's a URL, file it away as a LinkScrap
    parsed_url = urlparse.urlparse( scrap_content )
    if parsed_url[0]!="" and parsed_url[1]!="":
        # get favicon, if possible
        favicon_url = parsed_url[0]+"://"+parsed_url[1]+"/favicon.ico"
        try:
            favicon_resp = urlfetch.fetch(favicon_url)
            
            if favicon_resp.status_code == 200:
                favicon = favicon_resp.content
            else:
                favicon = None
        except DownloadError:
            favicon = None
            
        # if it parses as a feed, file it away as a feed scrap
        parse_attempt = feedparser.parse(scrap_content)
        if parse_attempt.version != "":
            # if we're not already subscribed to this feed
            if FeedScrap.all().filter("content =", scrap_content).filter("project =", project).count()!=0:
                return HttpResponseServerError( "This feed has already been added to this project.Z" )
            
            scrap = FeedScrap( content = scrap_content, project=project, created=datetime.datetime.now(), creator=user, icon=favicon )
            scrap.put()
            
            for entry in parse_attempt.entries:
                if 'guid' in entry and 'link' in entry and ('updated' in entry or 'published' in entry):
                    if 'published' in entry:
                        created = datetime.datetime( *entry.published_parsed[:6] )
                    elif 'updated' in entry:
                        created = datetime.datetime( *entry.updated_parsed[:6] )
                        
                        
                    if FeedItemScrap.all().filter("project=", project).filter("guid =", entry.guid).count()==0:
                        feed_item_scrap = FeedItemScrap( content=entry.link,
                                                         project=project,
                                                         created=created,
                                                         creator=user,
                                                         icon=favicon,
                                                         feed=scrap,
                                                         guid=entry.guid )
                        feed_item_scrap.put()
                        logging.info( feed_item_scrap )
                                                     
        else:
            scrap = LinkScrap( content = scrap_content, project=project, created=datetime.datetime.now(), creator=user, icon=favicon )
            scrap.put()
    else:
        scrap = Scrap( content = scrap_content, project=project, creator=user, created=datetime.datetime.now() )
        scrap.put()
    
    project.updated = datetime.datetime.now()
    project.put()
        
    return render_to_response( "includes/scrap_div.html", {'scrap':scrap} )
    
def scrap_icon(request, scrap_id):
    link_scrap = LinkScrap.get_by_id( int(scrap_id) )
    
    return HttpResponse( link_scrap.icon, mimetype="image/x-icon" )
    
def feed(request, nickname):
    nickname = Nickname.all().filter("nickname =", nickname).get()
    
    if nickname is None:
        return HttpResponseNotFound( "No such user" )
        
    scraps = Scrap.all().filter("creator =", nickname.user).order("-created").fetch(50)
    
    return render_to_response( "feed.xml", {'user':nickname.user, 'scraps':scraps}, mimetype="application/rss+xml" )
    
@membersonly
def update_feed_scrap( request, user, scrap_id ):
    feed_scrap = FeedScrap.get_by_id( int(scrap_id) )
    project = feed_scrap.project
    
    if project.user != user:
        return HttpResponseForbidden( "<html><body>That doesn't belong to you</body></html>" ) 
    
    logging.info( feed_scrap )
    
    parse_attempt = feedparser.parse(feed_scrap.content)
    for entry in parse_attempt.entries:
        if 'guid' in entry and 'link' in entry and ('updated' in entry or 'published' in entry):
            if 'published' in entry:
                created = datetime.datetime( *entry.published_parsed[:6] )
            elif 'updated' in entry:
                created = datetime.datetime( *entry.updated_parsed[:6] )
                
            if FeedItemScrap.all().filter("project =", project).filter("guid =", entry.guid).count()==0:
                feed_item_scrap = FeedItemScrap( content=entry.link,
                                                 project=project,
                                                 created=created,
                                                 creator=user,
                                                 icon=None,
                                                 feed=feed_scrap,
                                                 guid=entry.guid )
                feed_item_scrap.put()
                logging.info( feed_item_scrap )
    
    return HttpResponseRedirect( "/" )

@usercontext
def users_list( request, context ):
    all_users = Nickname.all()
    context['all_users'] = all_users
    
    return render_to_response( "users.html", context )
    