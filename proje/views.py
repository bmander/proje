from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response
from google.appengine.api import users
import logging
from django.utils import simplejson as json
from google.appengine.ext.db import GeoPt
from models import Project, Nickname, Scrap, LinkScrap
import datetime
import urlparse
from google.appengine.api import urlfetch, images

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
    
    return render_to_response( "welcome.html", {'enter_url':enter_url} )
    
@membersonly
@usercontext
def home(request, context, user):
    # if we haven't already created a Nickname for this google account's current nickname, create one
    if Nickname.all().filter("nickname =", user.nickname()).count() == 0:
        Nickname(user=user, nickname=user.nickname()).put()
    
    signout_url = users.create_logout_url("/welcome")
    
    project_entities = Project.all().filter('user =', user)
    
    projects = []
    for project_entity in project_entities:
        #logging.info( project_entity.scrap_set.order("-created") )
        
        scraps = project_entity.scrap_set.order("-created")
        scraps_count = scraps.count()
        scraps_remainder = scraps_count-5 if scraps_count>=5 else 0

        projects.append( {'name':project_entity.name, 'scraps':scraps.fetch(5), 'id':project_entity.key().id(), 'remainder':scraps_remainder} )
    
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
        project = Project(user=user,name=name)
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
    
    return render_to_response( "project.html", context )
    
@usercontext
def user(request, context, nickname):
    # get a user from the nickname
    nickname = Nickname.all().filter("nickname =", nickname).get()
    
    if nickname is None:
        return HttpResponseNotFound( "No such user" )
        
    projects = Project.all().filter("user =", nickname.user)
    
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
        
    parsed_url = urlparse.urlparse( scrap_content )
    if parsed_url[0]!="" and parsed_url[1]!="":
        # get favicon, if possible
        favicon_url = parsed_url[0]+"://"+parsed_url[1]+"/favicon.ico"
        favicon_resp = urlfetch.fetch(favicon_url)
        if favicon_resp.status_code == 200:
            favicon = favicon_resp.content
        else:
            favicon = None
        
        scrap = LinkScrap( content = scrap_content, project=project, created=datetime.datetime.now(), icon=favicon )
    else:
        scrap = Scrap( content = scrap_content, project=project, created=datetime.datetime.now() )
        
    scrap.put()
        
    return render_to_response( "includes/scrap_div.html", {'scrap':scrap} )
    
def scrap_icon(request, scrap_id):
    link_scrap = LinkScrap.get_by_id( int(scrap_id) )
    
    return HttpResponse( link_scrap.icon, mimetype="image/x-icon" )
    