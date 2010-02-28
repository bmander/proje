from django.conf.urls.defaults import *
from django.conf.urls.defaults import url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'proje.views',
    url(r'^welcome$', 'welcome', name='welcome'),
    url(r'^$', 'home', name='home'),
    url(r'^add_project/$', 'add_project', name='add_project'),
    url(r'^project/delete/(.*)/', 'delete_project', name='delete_project'),
    url(r'^project/(.*)/', 'project', name='project'),
    url(r'^user/(.*)/', 'user', name='user'),
    url(r'^feed/(.*)/', 'feed', name='feed'),
    url(r'^add_scrap/$', 'add_scrap', name='add_scrap'),
    url(r'^scrap_icon/(.*)/', 'scrap_icon', name='scrap_icon'),
    url(r'^update_feed_scrap/(.*)/', 'update_feed_scrap', name='update_feed_scrap'),
    # Example:
    # (r'^proje/', include('proje.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
