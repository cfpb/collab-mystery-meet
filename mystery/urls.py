from django.conf.urls import patterns, url

urlpatterns = patterns('mystery.views',
    url(r'^$', 'index', name='mystery'),
    url(r'^close/(?P<interest_id>.+)/cancel/$', 'close_cancel', name='close_cancel'),
    url(r'^close/(?P<interest_id>.+)/complete/$', 'close_complete', name='close_complete'),
    url(r'^close/(?P<interest_id>.+)/incomplete/$', 'close_incomplete', name='close_incomplete'),
)

