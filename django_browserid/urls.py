from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url('^verify/', 'django_browserid.views.verify', name='browserid_verify')
)
