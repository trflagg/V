from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from V.Vsite.forms import AuthenticationForm
from V.Vsite.forms import NewUserForm
from V.Vsite import userHelper
	
###############
# Accounts Login
###############
def accounts_login(request):
	"""
	Displays page for logging in as a user, and handles
	submission of the login form by validating it, passing
	the form off to the helper method, then checking the 
	result of the helper to see if to redisplay form, or
	redirect to game index page.
	"""
	# If user is submitting form, pass off to helper.
	if request.method == 'POST':	
		form = AuthenticationForm(request.POST)
		if userHelper.loginUser(form,request):
			# If both pass, redirect to game_index
			return HttpResponseRedirect(reverse('game_index'))
		else:
			pass
	# If not post, create an empty form
	else:
		form = AuthenticationForm()

	# Either we're sending back the form w/ errors, or a new form
	return render_to_response('login.html', {'form': form})


###############
# Accounts New
###############
def accounts_new(request):
	"""
	Displays page for creating a new user and
	handles the submission of the NewUserForm.
	If from is POSTed, pass it off to the helper.
	If helper returns true, login user. 
	If helper returns false, display form with
	errors.
	"""
	# If user is submitting form, pass off to helper.
	if request.method == 'POST':
		form = NewUserForm(request.POST)
		
		# REMOVE ME TO ALLOW SIGNUP
		return HttpResponseRedirect("http://www.google.com")
		
		# Validate form and create User. If validation
		# is successful, try to login user and redirect.
		if userHelper.newUser(form):
			form = AuthenticationForm({'username':form.get_username(), 'password':form.get_password()})
			if userHelper.loginUser(form, request, bypassActive=True):
				return HttpResponseRedirect(reverse('game_index'))	
	else:
		form = NewUserForm()
	return render_to_response('newUser.html', {'form': form})
	

