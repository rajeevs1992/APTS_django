from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
def userLogin(request):
	if request.method=='GET':
		if request.user.is_authenticated():
			group=request.user.groups.all()[0].name
			return HttpResponseRedirect('/home')
		elif 'e' in request.GET:
			return render_to_response('login.html',{'error':'1'},context_instance=RequestContext(request))
		else:
			return render_to_response('login.html',{},context_instance=RequestContext(request))
	else:
		user=authenticate(username=request.POST['uname'],password=request.POST['passwd'])
		if user is not None and user.is_active:
			login(request,user)
			return HttpResponseRedirect('/home')
		else:
			return HttpResponseRedirect('/?e=1')

@login_required
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def home(request):
	page=request.user.groups.all()[0].name+'.html'
	ret={}
	if 'message' in request.GET:
		ret={'message':request.GET['message']}
	return render_to_response(page,ret,context_instance=RequestContext(request))

def userLogout(request):
	logout(request)
	return HttpResponseRedirect('/')
