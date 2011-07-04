from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'chat.views.home', name='home'),
    # url(r'^chat/', include('chat.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    (r'^$', 'chatapp.views.index'),
    (r'^ajax$', 'chatapp.views.ajax'),
    (r'^message$', 'chatapp.views.message'),
    (r'^nickname$', 'chatapp.views.nickname'),
    (r'^sidemenu$', 'chatapp.views.sidemenu'),
    (r'^download/(.*)$', 'chatapp.views.download'),
    (r'^upload$', 'chatapp.views.upload'),
)



urlpatterns += patterns('',
    (r'^common/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
)