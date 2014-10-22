from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
import game.views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fantasyfootball.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', lambda r : HttpResponseRedirect('players/')),
    url(r'', include('game.urls', namespace='game')),
    url(r'^admin/', include(admin.site.urls)),
)
