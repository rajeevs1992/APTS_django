from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.shortcuts import render_to_response
import os
from shutil import rmtree
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import datetime

def is_student(u):
	l=u.groups.all()
	for i in l:
		if i.name=='student':
			return True
	return False

@login_required
@user_passes_test(lambda u: is_student(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def upload(request):
	if request.method=='POST':
		if request.POST['mode'] == 'project':
			proj=getproj(request.user.username,settings.USERS)
			target=os.path.join(settings.REPOS,proj)
			target=os.path.join(target,request.POST['destn']+'/')
			head=os.path.join(settings.COMMITS,proj+'/head')
		else:
			target=os.path.join(settings.STORE,request.user.username+'/')
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
			if '.git' not in subdirname:
				l.append(os.path.join(dirname, subdirname)[len(d):])
	return l
def getproj(uname,target):
	target=os.path.join(target,uname)
	f=open(target)
	proj=f.readline().strip()
	f.close()
	return proj
def listDirectory(d):
	l=[]
	for dirname, dirnames,filename in os.walk(d):
		for subdirname in dirnames:
			if '.git' not in subdirname+dirname:
				l.append(os.path.join(dirname, subdirname)[len(d)+1:])
	return l

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
	if request.GET['flag']=='project':
		proj=getproj(request.user.username,settings.USERS)
		loc=os.path.join(settings.REPOS,proj)
	else:
		loc=os.path.join(settings.STORE,request.user.username)
	loc=loc+'/'
	target=loc+request.GET['target']
	print loc
	print target
	f=open(target)
	content=f.read()
	f.close()
	return render_to_response('viewfile.html',{'data':content,'filename':request.GET['target']})

def rm(request):
	ret=auth(request)
	if ret == 1:
		destn=request.POST.getlist('destn')
		if destn:
			for i in destn:
				path=getpath(request)
				path=os.path.join(path,i)
				print path
			#	try:
			#	rmtree(path)
			#	except OSError:
			#		try:
			#			os.remove(path)
			#		except OSError:
			#			return HttpResponseRedirect('/student/modify/modifyView?d=p&action=rm&message=Delete Failed!')
			return HttpResponseRedirect('/student/modify/modifyView?d=p&action=rm&message=Deletion Complete!!')
		else:
			return HttpResponseRedirect('/student/modify/modifyView?d=p&action=rm&message=No files selected')
	

