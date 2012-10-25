from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
import os
from datetime import datetime

def is_guide(u):
	l=u.groups.all()
	for i in l:
		if i.name=='guide':
			return True
	return False

@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def selectProject(request):
	if request.method=='GET':
		if 'action' in request.GET:
			request.session['action']='commit'
			return render_to_response('selectProject.html',context_instance=RequestContext(request))
	else:
		action=request.session['action']
		del request.session['action']
		return HttpResponseRedirect('/guide/'+action)

@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def commit(request):
	if request.method=='GET':
		if 'proj' not in request.GET:
			return HttpResponseRedirect('/guide/selectproject?next=commit')
		arg={}
		arg['proj']=request.GET['proj']
		return render_to_response('commit.html',arg,context_instance=RequestContext(request))
	else:
		from django.conf import settings
		from git import Repo
		repo=os.path.join(settings.REPOS,request.POST['proj'])
		repo=Repo(repo)
		clean='nothing to commit (working directory clean)'
		if clean not in repo.git.status():
			message=str(datetime.now())+'\n'+request.POST['commitMessage']
			repo.git.add('APTS')
			repo.index.commit(message)
			commitname=repo.head.commit.hexsha[:10]
			commit=os.path.join(settings.COMMITS,request.POST['proj']+'/head')
			commitname=os.path.join(settings.COMMITS,request.POST['proj']+'/%s'%(commitname))
			os.rename(commit,commitname)
			f=open(commit,'w')
			f.close()
			notifyCommit(request.POST['proj'])
		else:
			return HttpResponseRedirect('/home?message=Nothing to commit')
		return HttpResponseRedirect('/home?message=Commited Successfully')
def notifyCommit(proj):
	from django.conf import settings
	from mails import Commit
	from django.contrib.auth.models import User
	proj_conf=os.path.join(settings.USERS,proj)
	f=open(proj_conf)
	f.readline()
	for i in f.readlines():
		u=User.objects.filter(username=i.strip())[0]
		u.email_user("Commit notification",Commit%(proj))
	f.close()
	return

@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def selectproject(request):
	if request.method=='POST':
		url=request.POST['next']+'?proj=%s'%(request.POST['proj'])
		return HttpResponseRedirect(url)
	else:
		if 'next' not in request.GET:
			return HttpResponseRedirect('/home')
		else:
			ret={}
			ret['next']=request.GET['next']
			ret['proj']=getActiveProjects()
	return render_to_response("selectProject.html",ret,context_instance=RequestContext(request))

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

