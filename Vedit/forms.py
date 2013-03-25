from django import forms
from V.Vgame.models import MapType, MapRegion

class MapEditForm(forms.Form):
	mapType = forms.ModelChoiceField(queryset=MapType.objects.all())
	mapRegion = forms.ModelChoiceField(queryset=MapRegion.objects.all())