from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, Template,loader
from django.contrib.auth.decorators import login_required
from V.Vgame.models import *
from V.Vedit.forms import *

###############
# Map Editor
###############
@login_required
def mapEdit(request, x=0, y=0):
	GRID_SIZE_X = 8
	GRID_SIZE_Y = 9
	
	if request.method == 'POST':
		print request.POST['type'], " ", request.POST['region']
		m = Map.objects.get(x=request.POST['x'], y=request.POST['y'])
		m.mapType = MapType.objects.get(id=request.POST['type'])
		m.mapRegion = MapRegion.objects.get(id=request.POST['region'])
		return HttpResponse(m.save())
	
	#Get or make map for x & y
	print x, y
	y = int(y)
	x = int(x)
	#x = int(x) * 10
	#y = int(y) * 10
	mList = {}
	g = MapType.objects.get(id=1)
	r = MapRegion.objects.get(id=1)
	t = loader.get_template('map_edit_cell.html')
	for i in range(y,y+GRID_SIZE_Y):
		mList[i] = {}
		for j in range(x,x+GRID_SIZE_X):
			m = Map.objects.get_or_create(x=j,y=i,defaults={'mapType':g,'mapRegion':r})[0]
			f = MapEditForm({"mapType":m.mapType.id, "mapRegion":str(m.mapRegion.id)}, auto_id="%s"+str(j)+str(i))
			c = Context({"map":m,"form":f})
			mList[i][j] = t.render(c)
			print mList[i][j]
		mList[i] = mList[i].values()
	
	#reverse 'em
	mList = reversed(mList.values())
	return render_to_response('map_edit.html', {'mList':mList})


###############
# Test XML Timer
###############
@login_required
def textXMLTimer(request):
	avatar = Avatar()
	avatar.xLocation = 1
	avatar.yLocation = 1
	#Time the template way
	# Get current and nearby map
	map_list = Map.objects.filter(x__gte=(avatar.xLocation-1),x__lte=(avatar.xLocation+1),y__gte=(avatar.yLocation-1),y__lte=(avatar.yLocation+1)).order_by('-y','x')
	
	#Time the templateToXML way
	#Time the djangoXML way
	#Time the etreeXML way

	#Return the results

def timeTemplate():
	pass

def timeTemplateToXML():
	pass

def timeDjangoXML():
	pass

def timeEtreeXML():
	pass