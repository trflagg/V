from django import forms
from django.contrib.auth.models import User

class AuthenticationForm(forms.Form):
	username = forms.CharField(max_length = 10)
	password = forms.CharField(widget=forms.PasswordInput)
	general_error = ""

	def get_username(self):
		return self.cleaned_data['username']


	def get_password(self):
		return self.cleaned_data['password']



class NewUserForm(forms.Form):
	username = forms.CharField(max_length = 10)
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)
	password_confirm = forms.CharField(widget=forms.PasswordInput)
	general_error = ""
		
	def clean_username(self):
		if(User.objects.filter(username__exact=self.cleaned_data['username']).count() > 0):
			raise forms.ValidationError, 'Username has already been used.'
		return self.cleaned_data['username']

	def clean_password_confirm(self):
		password1 = self.cleaned_data["password"]
		password2 = self.cleaned_data["password_confirm"]
		if password1 != password2:
			raise forms.ValidationError, 'Passwords must match.'
		else:
			return password2 

	def get_username(self):
		return self.cleaned_data['username']

	def get_password(self):
		return self.cleaned_data['password']