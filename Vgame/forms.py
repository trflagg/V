from django import forms
from V.Vgame.models import Tribe
from V.Vgame.models import Avatar

class NewAvatarForm(forms.Form):
	name = forms.CharField(max_length = 20)
	gender = forms.ChoiceField(choices=[('male','male'),('female','female')])
	tribe = forms.ModelChoiceField(queryset=Tribe.objects.all())
	general_error = ""

	def clean_name(self):
		if(Avatar.objects.filter(name__exact=self.cleaned_data['name']).count() > 0):
			raise forms.ValidationError, 'Name has already been used.'
		return self.cleaned_data['name']
		
	def clean_tribe(self):
		return self.cleaned_data['tribe']
	
	def clean_geder(self):
		g = self.cleaned_data['gender']
		if (g != 'male' or g != 'female'):
			raise forms.ValidationError, 'Gender must be either "male" or "female".'
		return self.cleaned_data['gender']
		

	
