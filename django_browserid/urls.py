from django.conf.urls.defaults import patterns, url

from views import BrowserID_Verify

urlpatterns = patterns('',
	url('^browserid/verify/', BrowserID_Verify.as_view(), name='browserid_verify')
)
