from django.conf.urls.defaults import *
from django.conf.urls.defaults import url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'proje.views',
    url(r'^welcome$', 'welcome', name='welcome'),
    url(r'^learn$', 'learn', name='learn'),
    url(r'^$', 'home', name='home'),
    url(r'^add_project/$', 'add_project', name='add_project'),
    url(r'^project/delete/(.*)/', 'delete_project', name='delete_project'),
    url(r'^project/(.*)/', 'project', name='project'),
    url(r'^user/(.*)/', 'user', name='user'),
    url(r'^feed/(.*)/', 'feed', name='feed'),
    url(r'^add_scrap/$', 'add_scrap', name='add_scrap'),
    url(r'^scrap_icon/(.*)/', 'scrap_icon', name='scrap_icon'),
    url(r'^update_feed_scrap/(.*)/', 'update_feed_scrap', name='update_feed_scrap'),
    url(r'^users/', 'users_list', name='users_list'),
    url(r'^projects/', 'projects_list', name='projects_list'),
    url(r'^update_project_counts/', 'update_project_counts', name='update_project_counts'),
    url(r'^set_project_updated/', 'set_project_updated', name='set_project_updated'),
    # Example:
    # (r'^proje/', include('proje.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
