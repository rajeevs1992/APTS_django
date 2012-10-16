from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User,Group
from django.db import IntegrityError
from hashlib import sha1
import os
from time import time
from django.contrib.auth.decorators import login_required,user_passes_test

def is_admin(u):
	l=u.groups.all()
	for i in l:
		if i.name=='admin':
			return True
	return False
@login_required
@user_passes_test(lambda u: is_admin(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def addproj(request):
	if request.method=='POST':
		from django.conf import settings
		repo=os.path.join(settings.REPOS,request.POST['pname'])
		commits=os.path.join(settings.COMMITS,request.POST['pname'])
		config=os.path.join(settings.USERS,request.POST['pname'])
		if os.path.exists(repo):
			return HttpResponseRedirect('/home?message=Project Already Exists!!')
		else:
			from git import Repo
			try:
				User.objects.create_user(request.POST['pname'],'','')
				os.mkdir(repo)
				os.mkdir(commits)
				f=open(config,'a')
				f.write('active\n')
				f.close()
			except OSError,IntegrityError:
				return HttpResponseRedirect('/home?message=Project Already Exists!!')
			Repo.init(repo)
			os.mkdir(os.path.join(repo,request.POST['pname']))
			target=os.path.join(settings.COMMITS,request.POST['pname']+'/head')
			f=open(target,'a')
			f.write('Initial commit\n')
			f.close()
		return HttpResponseRedirect('/a/user/add?message=Project Created!!')
	else:
		ret=''
		if 'message' in request.GET:
			ret={'message':request.GET['message']}
		return render_to_response('addproj.html',ret,context_instance=RequestContext(request))
@login_required
@user_passes_test(lambda u: is_admin(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def adduser(request):
	if request.method=='POST':
		from django.conf import settings
		for i in range(1,10):
			if request.POST['uname'+str(i)] and request.POST['email'+str(i)]:
				passwd=getpass()
				email=request.POST['email'+str(i)]
				try:
					user=User.objects.create_user(request.POST['uname'+str(i)],email,passwd)
					g=Group.objects.get(name=request.POST['group'+str(i)])
					g.user_set.add(user.id)
					create_env(user,passwd,request.POST['project'+str(i)])
				except IntegrityError:
					from mails import ChangeStudentProj
					u=User.objects.filter(username=request.POST['uname'+str(i)])[0]
					u.email_user('Project notification',ChangeStudentProj%(request.POST['project'+str(i)]))
				config=os.path.join(settings.USERS,request.POST['uname'+str(i)])
				if request.POST['group'+str(i)] == 'student':
					f=open(config,'w')
				else:
					f=open(config,'a')
				if 'none' not in request.POST['project'+str(i)]:
					f.write(request.POST['project'+str(i)]+"\n")
					config=os.path.join(settings.USERS,request.POST['project'+str(i)])
					f2=open(config,'a')
					f2.write(request.POST['uname'+str(i)]+"\n")
					f2.close()
					f.close()
		return HttpResponseRedirect('/a/user/addguide')
	else:
		from django.conf import settings 
		proj=os.listdir(settings.REPOS)
		ret={'projList':proj}
		if 'message' in request.GET:
			ret['message']=request.GET['message']
		return render_to_response('adduser.html',ret,context_instance=RequestContext(request))

def create_env(user,passwd,project):
	flag=False
	from django.conf import settings 
	uname=user.username
	level=user.groups.all()[0].name
	personal=os.path.join(settings.STORE,uname)
	config=os.path.join(settings.USERS,uname)
	try:
		os.mkdir(personal)
	except OSError:
		pass
	email=''
	if level=='student':
		from mails import StudentReg
		email=StudentReg%(project,uname,passwd)
	elif level=='guide':
		from mails import GuideReg
		email=GuideReg%(uname,passwd)
	elif level=='evalueator':
		from mails import EvalReg
		email=EvalReg%(uname,passwd)
	if email:
		user.email_user('Project Tracker Account Information',email)
		f=open(config,'a')
		if 'none' not in project:
			f.write(project+'\n')
		f.close()
	return 

def getpass():
	return sha1(str(time())).hexdigest()[:6]

@login_required
@user_passes_test(lambda u: is_admin(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def addguide(request):
	if request.method=='POST':
		projects=''
		data=''
		from django.conf import settings
		config=os.path.join(settings.USERS,request.POST['guide'])
		f=open(config,'r')
		data=f.read()
		f.close()
		f=open(config,'a')
		proj=request.POST.getlist('proj')
		if proj:
			for p in proj:
				if p not in data:
					f.write(p+'\n')
					projects+=p+'\n'
		f.close()
		if projects:
			guide=User.objects.filter(username=request.POST['guide'])
			from mails import AddProj2Guide
			message=AddProj2Guide%(projects)
			guide[0].email_user('Projects to Guide',message)
			return HttpResponseRedirect("/home?message=Guides added!!")
		else:
			return HttpResponseRedirect("/home?message=No new projects selected!!")
	else:
		ret={'plist':getActiveProjects()}
		ret['glist']=User.objects.filter(groups__name='guide')
		if 'message' in request.GET:
			ret['message']=request.GET['message']
		return render_to_response('addguide.html',ret,context_instance=RequestContext(request))
def getActiveProjects():
	from django.conf import settings
	listing=os.listdir(settings.REPOS)
	ret=[]
	for i in listing:
		file=os.path.join(settings.USERS,i)
		f=open(file)
		file=f.readline()
		if 'active' in file:
			ret.append(i)
	return ret
def delete(request):
	pass
def reset(request):
	pass
def modify(request):
	pass
def auth(request):
	pass
