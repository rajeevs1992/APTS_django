from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.shortcuts import render_to_response
from django.utils.encoding import smart_str
from django.core.servers.basehttp import FileWrapper
import os
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import datetime
from git import Repo

def is_student(u):
	l=u.groups.all()
	for i in l:
		if i.name=='student':
			return True
	return False
@login_required
@user_passes_test(lambda u: is_student(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def mkdir(request):
	if request.method=='POST':
		target=''
		if request.POST['mode'] == 'project':
			proj=getproj(request.user.username,settings.USERS)
			target=os.path.join(settings.REPOS,proj)
			target=target+request.POST['destn']+'/'
		else:
			target=os.path.join(settings.STORE,request.user.username+'/')
		target=target+request.POST['dirname']
		try:
			os.mkdir(target)
		except OSError:
			pass
		return HttpResponseRedirect('/home?message=Directory Created.')
	else:
		ret={}
		if request.GET['target']=='project':
			ret['listing']=getlisting(request.user.username,'project')
			ret['mode']='project'
			ret['dstn']='p'
		else:
			ret['listing']=getlisting(request.user.username,'store')
			ret['mode']='store'
			ret['dstn']='s'
		if 'message' in request.GET:
			ret['message']=request.GET['message']
		return render_to_response('mkdir.html',ret,context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: is_student(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def upload(request):
	if request.method=='POST':
		if request.POST['mode'] == 'project':
			proj=getproj(request.user.username,settings.USERS)
			target=os.path.join(settings.REPOS,proj)
			target=target+request.POST['destn']+'/'
			head=os.path.join(settings.COMMITS,proj+'/head')
		else:
			target=os.path.join(settings.STORE,request.user.username+'/')
			target=target+request.POST['destn']+'/'
			head='/dev/null'
		if request.FILES.has_key('file'):
			dialogue='%s uploaded %s at %s'
			f=open(head,'a')
			time=str(datetime.now())
			for i in request.FILES.getlist('file'):
				move_uploaded_file(i,target)
				f.write(dialogue%(request.user.username,str(i),time))
			f.close()
			return HttpResponseRedirect('/home?message=Files Uploaded.')
		else:
			return HttpResponseRedirect('/home?message=No Files Selected.')
	else:
		ret={}
		if request.GET['target']=='project':
			ret['listing']=getlisting(request.user.username,'project')
			ret['mode']='project'
			ret['dstn']='p'
		else:
			ret['listing']=getlisting(request.user.username,'store')
			ret['mode']='store'
			ret['dstn']='s'
		if 'message' in request.GET:
			ret['message']=request.GET['message']
		return render_to_response('upload.html',ret,context_instance=RequestContext(request))
def getlisting(uname,mode):
	if mode=='project':
		proj=getproj(uname,settings.USERS)
		target=os.path.join(settings.REPOS,proj)
	else:
		target=os.path.join(settings.STORE,uname)
	return listDirectory(target)
def listDirectory(d):
	l=[]
	for dirname, dirnames,filename in os.walk(d):
		for subdirname in dirnames:
			if '.git' not in subdirname+dirname:
				l.append(os.path.join(dirname, subdirname)[len(d):])
	return l
def getproj(uname,target):
	target=os.path.join(target,uname)
	f=open(target)
	proj=f.readline().strip()
	f.close()
	return proj
def move_uploaded_file(f,d):
	destination = open(d+f.name,'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
		destination.close()
	return
def viewproject(request):
	loc=''
	ret={}
	if request.GET['target']=='project':
		proj=getproj(request.user.username,settings.USERS)
		loc=os.path.join(settings.REPOS,proj)
		ret['flag']='project'
	else:
		ret['flag']='store'
		loc=os.path.join(settings.STORE,request.user.username)
	l=[]
	chop=len(loc)
	for dirname, dirnames, filenames in os.walk(loc):
		for filename in filenames:
			if '.git' not in dirname+filename:
				temp=os.path.join(dirname, filename)[chop:]
				l.append(temp)
	ret['listing']=l
	return render_to_response('viewproject.html',ret)

def viewfile(request):
	loc=''
	ret={}
	if request.GET['flag']=='project':
		proj=getproj(request.user.username,settings.USERS)
		loc=os.path.join(settings.REPOS,proj)
		ret['flag']='project'
	else:
		loc=os.path.join(settings.STORE,request.user.username)
		ret['flag']='store'
	loc=loc+'/'
	target=loc+request.GET['target']
	f=open(target)
	content=f.read()
	f.close()
	ret['data']=content
	ret['filename']=request.GET['target']
	return render_to_response('viewfile.html',ret)
@login_required
@user_passes_test(lambda u: is_student(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def rm(request):
	if request.method=='POST':
		from shutil import rmtree
		if request.POST['mode'] == 'project':
			proj=getproj(request.user.username,settings.USERS)
			target=os.path.join(settings.REPOS,proj)
			head=os.path.join(settings.COMMITS,proj+'/head')
		else:
			target=os.path.join(settings.STORE,request.user.username+'/')
			head='/dev/null'
		if request.POST.has_key('destn'):
			dialogue='%s deleted %s at %s'
			f=open(head,'a')
			time=str(datetime.now())
			for i in request.POST.getlist('destn'):
				try:
					rmtree(target+i)
				except OSError:
					try:
						os.remove(target+i)
					except OSError:
						pass
				f.write(dialogue%(request.user.username,str(i),time))
			f.close()
			return HttpResponseRedirect('/home?message=Files Deleted.')
		else:
			return HttpResponseRedirect('/home?message=No Files Selected.')
	else:
		ret={}
		if request.GET['target']=='project':
			ret['listing']=getlisting(request.user.username,'project')[1:]
			ret['listing2']=getlisting_files(request.user.username,'project')
			ret['mode']='project'
			ret['dstn']='p'
		else:
			ret['listing']=getlisting(request.user.username,'store')
			ret['listing2']=getlisting_files(request.user.username,'store')
			ret['mode']='store'
			ret['dstn']='s'
		if 'message' in request.GET:
			ret['message']=request.GET['message']
		return render_to_response('rm.html',ret,context_instance=RequestContext(request))
def getlisting_files(uname,target):
	l=[]
	d=''
	p=''
	if target=='project':
		p=getproj(uname,settings.USERS)
		d=os.path.join(settings.REPOS,p)
		d=d+'/'+p
	else:
		d=os.path.join(settings.STORE,uname)
	for dirname, dirnames,filename in os.walk(d):
		for files in filename:
			if '.git' not in files+dirname:
				t=os.path.join(dirname,files)[len(d):]
				if target=='project':
					t='/'+p+t
				l.append(t)
	return l
@login_required
@user_passes_test(lambda u: is_student(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def download(request):
	loc=''
	if request.GET['flag']=='project':
		proj=getproj(request.user.username,settings.USERS)
		loc=os.path.join(settings.REPOS,proj)
		loc=loc+'/'
		loc=loc+request.GET['target']
	elif request.GET['flag']=='store':
		loc=os.path.join(settings.STORE,request.user.username)
		loc=loc+'/'
		loc=loc+request.GET['target']
	else:
		proj=getproj(request.user.username,settings.USERS)
		loc=os.path.join(settings.REPOS,proj)
		r=Repo(loc)
		f=open(settings.DOWNLOADS+proj+request.user.username+'.tar',"w")
		r.archive(f)
		f.close()
		loc=settings.DOWNLOADS+proj+request.user.username+'.tar'
	w=FileWrapper(file(loc))
	response = HttpResponse(w,mimetype='text/plain')
	n=loc.split('/')
	response['Content-Disposition'] = "attachment; filename=%s"%(n[-1])
	return response
def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))
def archive(target,source):
	import zipfile
	zip = zipfile.ZipFile(target, 'w')
	zipdir(source, zip)
	zip.close()
@login_required
@user_passes_test(lambda u: is_student(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def downloadVersion(request):
	from django.conf import settings
	from django.core.servers.basehttp import FileWrapper
	import mimetypes
	proj=getproj(request.user.username,settings.USERS)
	zipTmp="/tmp/"+proj;
        archive(zipTmp,settings.REPOS+proj+'/'+proj)
	response = HttpResponse(FileWrapper(open(zipTmp)),mimetype='application/zip')
	response['Content-Disposition'] = "attachment; filename='"+proj+"'"
	response['Content-Length']=os.path.getsize(zipTmp)
	return response
