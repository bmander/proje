from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.api import users
import logging
from django.utils import simplejson as json

def membersonly(f):
    def new_f(request, *args, **kwargs):
        
        user = users.get_current_user()
        if user:
            return f(request, *args, **kwargs)
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