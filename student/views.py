from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.shortcuts import render_to_response
import os
from shutil import rmtree
from django.contrib.auth.decorators import login_required,user_passes_test

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
	from django.conf import settings
	if request.method=='POST':
		if request.FILES.has_key('file'):
			destn=request.POST['destn']
			if request.POST['mode']=='p':
			else:
			f=open(os.path.join(request.session['projectName'])),'a')
			for i in request.FILES.getlist('file'):
				move_uploaded_file(i,d)
				if request.POST['mode']=='p':
					if destn=='':destn='/';
					message="'%s' Uploaded file '%s' to '%s'\n"%(request.session['uname'],i,destn)
					f.write(message)
			f.close()
			return HttpResponseRedirect('/student/modify/?message=Uploaded files successfully!!')
	else:
		return render_to_response('upload.html',)
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def modifyView(request):
	ret=auth(request)
	if ret==1:
		mode=request.GET['d']
		d=getpath(request)
		args={}
		l=listDirectory(d)
		args={'listing':l,'mode':mode,
				'projectName':request.session['projectName'],'links':StudentLinks}
		if 'message' in request.GET:
			args['message']=request.GET['message']
		if request.GET['action']=='upload':
			args['title']='Upload'
			return render_to_response('upload.html',args,context_instance=RequestContext(request))
		elif request.GET['action']=='mkdir':
			args['title']='Create directory'
			return render_to_response('mkdir.html',args,context_instance=RequestContext(request))
		elif request.GET['action']=='rm':
			l2=[]
			for dirname, dirnames,filename in os.walk(d):
				for f in filename:
					if '.git' not in f:
						l2.append((os.path.join(dirname,f))[len(d):])
			args['title']='Delete files or directories'
			args['listing2']=l2
			return render_to_response('rm.html',args,context_instance=RequestContext(request))
		elif request.GET['action']=='view':
			args['title']='View data'
			return render_to_response('view.html',args,context_instance=RequestContext(request))
	else:
		return render_to_response('login.html',ret,context_instance=RequestContext(request))

def listDirectory(d):
	l=[]
	for dirname, dirnames,filename in os.walk(d):
		for subdirname in dirnames:
			if '.git' not in subdirname:
				l.append(os.path.join(dirname, subdirname)[len(d):])
	return l

def move_uploaded_file(f,d):
	destination = open(d+f.name,'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
		destination.close()
	return

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
	

def auth(request):
	args={'heading':'Govt Engineering College,Thrissur',
		'subHeading':'The Academic Project Tracker',
		'destn':'/login/verify/',
		'error':'Unautorized Access!!Please Login!!'}
	if 'uname' and 'projectName' and 'level' in request.session:
		if request.session['level']==3:
			return 1
	return args

def getpath(request):
	d=''
	if request.method=='GET':
		mode=request.GET['d']
	else:
		mode=request.POST['mode']
	if mode=='p':
		d=os.path.join(cur_dir,'../data/repos/%s/%s'%(request.session['projectName'],request.session['projectName']))
	elif mode=='s':
		d=os.path.join(cur_dir,'../data/personal_area/%s'%(request.session['uname']))
	print d
	return d

