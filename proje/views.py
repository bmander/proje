from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.api import users
import logging
from django.utils import simplejson as json
from google.appengine.ext.db import GeoPt
from models import Project

def membersonly(f):
    def new_f(request, *args, **kwargs):
        
        user = users.get_current_user()
        if user:
            return f(request, user, *args, **kwargs)
        else:
            return HttpResponseRedirect( "/welcome" )
    
    return new_f

def welcome(request):
    user = users.get_current_user()
    
    if user:
        enter_url="/"
    else:
        enter_url=users.create_login_url("/")
    
    return render_to_response( "welcome.html", {'enter_url':enter_url} )
    
@membersonly
def home(request, user):
    signout_url = users.create_logout_url("/welcome")
    
    projects = Project.all().filter('user =', user)
    
    return render_to_response( "home.html", {'user':user,'signout_url':signout_url,'projects':projects} )
    
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
        
        # return redirect to main page
        return HttpResponseRedirect( "/" )
    
    return render_to_response( "add_project.html", {'error':request.GET.get('error',None)} )
    