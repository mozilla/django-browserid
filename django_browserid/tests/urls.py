from django.conf.urls.defaults import include, patterns

urlpatterns = patterns('',
    (r'^browserid/', include('django_browserid.urls')),
)
