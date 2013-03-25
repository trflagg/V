from V.Vsite.models import VUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login

def newUser(form):
	"""
	Takes in NewUserForm and attempts to create a
	new user by validating the form.
	Returns true if new user is created.
	Returns false if error.
	"""

	# authenticate the form
	if form.is_valid():
		# create new user
		user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
	
		# create user profile
		vu = VUser()
		vu.user = user
	
		# Save
		user.save()
		vu.save()

		return True
	else:
		# Do any other error checking or setting of errors here.
		return False

def loginUser(form,request=None,bypassActive=False,bypassRequest=False):
	""" 
	Takes in AuthenticationForm and tries to login the
	user from the form. 
	Returns true if user is logged in.
	Returns false if error, setting the error in form.general_error.
	"""
	
	#authenticate the user
	if form.is_valid():
		user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
		
		if user is not None:
			if user.is_active or bypassActive:
				if request is not None:
					login(request, user)
				else:
					if bypassRequest:
						return True
					else:					
						form.general_error = "Request is NONE."
						return False
				#Return true.
				form.general_error = ""
				return True

			else:
				# Return a 'disabled account' error message
				form.general_error = "Sorry, You're account has been disabled. Please e-mail the admin for reactivation."
				return False
		else:
			# Return an 'invalid login' error message.
			form.general_error = "You supplied an incorrect username or password. Please try again, or give up."
			return False
	else:
		form.general_error = ""
		return False

	#Shouldn't reach here
	form.general_error = "Unknown error."
	return False
