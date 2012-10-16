from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$','login.views.userLogin'),
	(r'^logout/$','login.views.userLogout'),
	(r'^home/$','login.views.home'),
	(r'^guide/commit$','guide.views.commit'),
	(r'^guide/selectproject$','guide.views.selectproject'),
	(r'^student/upload$','student.views.upload'),
	(r'^a/user/add$','admin.views.adduser'),
	(r'^a/project/add$','admin.views.addproj'),
	(r'^a/user/addguide$','admin.views.addguide'),
    (r'^admin/', include(admin.site.urls))

)
if settings.DEBUG:
	urlpatterns += patterns('',
		url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
		     'document_root': settings.MEDIA_ROOT,}),)
