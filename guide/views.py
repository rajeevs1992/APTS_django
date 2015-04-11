from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
import os
from datetime import datetime
import re
from git import Repo
from django.conf import settings
def is_guide(u):
    l=u.groups.all()
    for i in l:
        if i.name=='guide':
            return True
    return False
@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def switch(request):
    if request.method=='GET':
        ret={}
        if 'message' in request.GET:
            ret['message']=request.GET['message']
        r=Repo(settings.REPOS+request.session['project'])
        cur=r.active_branch.name
        heads=r.heads
        h=[]
        for i in heads:
            if i.name != cur:
                h.append(i)
        ret['cur']=cur
        ret['h']=h
        ret['project']=request.session['project']
        return render_to_response('switch.html',ret,context_instance=RequestContext(request))
    else:
        r=Repo(settings.REPOS+request.session['project'])
        r.git.checkout(request.POST['branch'])
        return HttpResponseRedirect('/home/?message=Switched to branch %s'%(request.POST['branch']))
            
@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def commit(request):
    if request.method=='GET':
        arg={}
        arg['proj']=request.session['project']
        return render_to_response('commit.html',arg,context_instance=RequestContext(request))
    else:
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
        request.session['project']=request.POST['proj']
        return HttpResponseRedirect('/home')
    else:
        ret={}
        ret['proj']=getActiveProjects()
        return render_to_response("selectProject.html",ret,context_instance=RequestContext(request))

def getActiveProjects():
    listing=os.listdir(settings.REPOS)
    ret=[]
    for i in listing:
        file=os.path.join(settings.USERS,i)
        f=open(file)
        file=f.readline()
        if 'active' in file:
            ret.append(i)
    return ret
    
@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def selectcommit(request):
    if request.method=='GET':
        if 'nextAction' not in request.GET:
            return HttpResponseRedirect('/home?message=Invalid request')
        t=[]
        os.chdir(settings.REPOS+request.session['project'])
        tree=os.popen('git log --all --graph --oneline --decorate -n 50').read()
        tree=tree.split('\n')
        for i in tree:
           m=re.search('\w',i)
           if m:
                t.append(i[:m.start()]+"<input type='radio' name=commit value='"+i[m.start():].split(" ")[0]+
                "' onclick=form.submit()>"+i[m.start():]+"<br/>");
        else:
            t.append(i+"<br/>");
        ret={}
        ret['tree']=t
        ret['action']=request.GET['nextAction']
        return render_to_response('selcommit.html',ret,context_instance=RequestContext(request))
    else:
        pass

@login_required
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def branch(request):
    if request.method=='GET':
        if 'commit' not in request.GET:
            return HttpResponseRedirect('/guide/selectcommit?nextAction=/guide/branch')
        arg={}
        arg['proj']=request.session['project']
        arg['commit']=request.GET['commit']
        return render_to_response('branch.html',arg,context_instance=RequestContext(request))
    else:
        r=Repo(settings.REPOS+request.session['project'])
        r.git.checkout(request.POST['commit'],b=request.POST['branch'])
        return HttpResponseRedirect('/home/?message=Switched to branch %s'%(request.POST['branch']))
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
@user_passes_test(lambda u: is_guide(u),login_url='/logout')
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def download(request):
    from django.conf import settings
    from django.core.servers.basehttp import FileWrapper
    import mimetypes
    if request.method=='GET':
        if 'commit' not in request.GET:
                    return HttpResponseRedirect('/home?message=Invalid request')
        else:
            ret={}
            ret['commit']=request.GET['commit']
            os.chdir(settings.REPOS+request.session['project'])
            cur=os.popen("git describe --contains --all HEAD").read();
            os.popen("git checkout "+request.GET['commit']);
            os.popen("git checkout "+cur);
            zipTmp="/tmp/"+request.session['project'];
            archive(zipTmp,settings.REPOS+request.session['project']+'/'+request.session['project'])
            response = HttpResponse(FileWrapper(open(zipTmp)),mimetype='application/zip')
            response['Content-Disposition'] = "attachment; filename='"+request.session['project']+request.GET['commit']+"'"
            response['Content-Length']=os.path.getsize(zipTmp)
            return response
