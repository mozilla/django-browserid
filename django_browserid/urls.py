from django.conf.urls.defaults import patterns, url

from .views import VerifyView

urlpatterns = patterns('',
    url('^browserid/verify/', VerifyView.as_view(),
        name='browserid_verify')
)
