from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError
from django.http import Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import Context, Template,loader
from django.contrib.auth.decorators import login_required
from V.Vgame.forms import *
from V.Vgame.models import *
from V.Vgame import avatarHelper
from V.Vgame import mapHelper
from django.core.exceptions import ObjectDoesNotExist
from V.Vgame.abilityReply import AbilityReply
from V.Vgame import abilities



######################
#   Game Interface   #
######################

###############
# Index
###############
@login_required
def index(request):
	general_error = ""
	# If POST, get the selected Avatar, set the session, and redirect to map.
	if request.method == 'POST':
		if request.POST.has_key('selected_avatar'):
			# Check that it is a valid avatar for the user
			try:
				avatar = Avatar.objects.get(id=request.POST['selected_avatar'])
				if (avatar.user == request.user):
					request.session['avatar'] = avatar.id
					return HttpResponseRedirect(reverse('base_game_map'))
				else:
					general_error = "That is not your character, try again."
			except ObjectDoesNotExist:
				general_error = "Selected character does not exist."
	
	# get all of the user's avatars
	if request.user.is_authenticated():
		user = request.user
		avatarList = user.avatar_set.all()
		if (len(avatarList) == 0):
			return HttpResponseRedirect(reverse('avatar_new'))

		#Check if user can create a new avatar
		if (len(avatarList) < Avatar.MAX_AVATARS_PER_USER):
			newLink = True
		else:
			newLink = False
	
		return render_to_response('index.html',{'avatarList':avatarList, 'newLink':newLink, 'general_error':general_error})
	else:
		raise Http404


###############
# New Avatar
###############
@login_required
def avatar_new(request):
	if request.method == 'POST':
		form = NewAvatarForm(request.POST)
		if form.is_valid():
			# use helper to process form and create new avatar
			avatarHelper.newAvatar(form, request.user)
			return HttpResponseRedirect(reverse('game_index'))	
	else:
		form = NewAvatarForm()
	return render_to_response('newAvatar.html', {'form': form})




######################
#   Map              #
######################

###############
# Base Game Map
###############
@login_required
def base_game_map(request):
	# Get the avatar
	try:
		a = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))

	return render_to_response('base_game_map.html')

###############
# Game Map
###############
@login_required	
def game_map(request):
	# Get the avatar
	try:
		avatar = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))
		
	# Get current and nearby map
	map_list = Map.objects.filter(x__gte=(avatar.xLocation-1),x__lte=(avatar.xLocation+1),y__gte=(avatar.yLocation-1),y__lte=(avatar.yLocation+1)).order_by('-y','x')
	
	#Load nearby mappables
	#Filter only the mappables whose xLocation > avatar.xLocation -1, xLocation < a.xLocation + 1, yLocation > a.yLocation-1, yLocation < a.yLocation+1
	mappable_dict = {}
	mappable_dict['Monster'] = Monster.objects.filter(xLocation__gte=(avatar.xLocation-1),xLocation__lte=(avatar.xLocation+1),yLocation__gte=(avatar.yLocation-1),yLocation__lte=(avatar.yLocation+1)).order_by('-yLocation','xLocation')
	mappable_dict['NPC'] = NPC.objects.filter(xLocation__gte=(avatar.xLocation-1),xLocation__lte=(avatar.xLocation+1),yLocation__gte=(avatar.yLocation-1),yLocation__lte=(avatar.yLocation+1)).order_by('-yLocation','xLocation')
	mappable_dict['Avatar'] = Avatar.objects.filter(xLocation__gte=(avatar.xLocation-1),xLocation__lte=(avatar.xLocation+1),yLocation__gte=(avatar.yLocation-1),yLocation__lte=(avatar.yLocation+1)).order_by('-yLocation','xLocation').exclude(name=avatar.name)
	mappable_dict['Equipment'] = Equipment.objects.filter(xLocation__gte=(avatar.xLocation-1),xLocation__lte=(avatar.xLocation+1),yLocation__gte=(avatar.yLocation-1),yLocation__lte=(avatar.yLocation+1)).order_by('-yLocation','xLocation')
	mappable_dict['Item'] = Item.objects.filter(xLocation__gte=(avatar.xLocation-1),xLocation__lte=(avatar.xLocation+1),yLocation__gte=(avatar.yLocation-1),yLocation__lte=(avatar.yLocation+1)).order_by('-yLocation','xLocation')
	
	# render map cells
	map_html = []
	t = loader.get_template('game_map_cell.html')
	i = 0
	moveTable = {0: (-1,1),
				 1: (0,1),
				 2: (1,1),
				 3: (-1,0),
				 4: (0,0),
				 5: (1,0),
				 6: (-1,-1),
				 7: (0,-1),
				 8: (1,-1)}
	#mappable_list formed by selecting only the items surrounding the avatar based on moveTable
	# For each map_cell:
	# Build a list of mappables whose xLocation == avatar.xLocation + moveTable[0] and yLocation == avatar.yLocation + moveTable[1]
	for map_cell in map_list:
		c = Context({	"map":map_cell, 
						"num":i, 
						"movement":str(moveTable[i]),
						"ap":abilities.Move.getAPCost(avatar=avatar, data={'map':map_cell,'deltaX':moveTable[i][0], 'deltaY':moveTable[i][1]}),
						"avatar_list":[a for a in mappable_dict['Avatar'] if ((a.xLocation == avatar.xLocation + int(moveTable[i][0])) & (a.yLocation == avatar.yLocation + int(moveTable[i][1])))],
						"monster_list":[a for a in mappable_dict['Monster'] if ((a.xLocation == avatar.xLocation + int(moveTable[i][0])) & (a.yLocation == avatar.yLocation + int(moveTable[i][1])))],
						"npc_list":[a for a in mappable_dict['NPC'] if ((a.xLocation == avatar.xLocation + int(moveTable[i][0])) & (a.yLocation == avatar.yLocation + int(moveTable[i][1])))]
					})
		map_html.append(t.render(c))
		i = i + 1
		
	# Save avatar to update ap
	avatar.save()
	
	# return response
	return render_to_response('game_map.html', {'map_html':map_html, 
												'map': map_list[4], 
												'avatar':avatar,
												"avatar_list":[a for a in mappable_dict['Avatar'] if ((a.xLocation == avatar.xLocation) & (a.yLocation == avatar.yLocation))],
												"monster_list":[a for a in mappable_dict['Monster'] if ((a.xLocation == avatar.xLocation) & (a.yLocation == avatar.yLocation))],
												"npc_list":[a for a in mappable_dict['NPC'] if ((a.xLocation == avatar.xLocation) & (a.yLocation == avatar.yLocation))],
												"equipment_list":[a for a in mappable_dict['Equipment'] if ((a.xLocation == avatar.xLocation) & (a.yLocation == avatar.yLocation))],
												"item_list":[a for a in mappable_dict['Item'] if ((a.xLocation == avatar.xLocation) & (a.yLocation == avatar.yLocation))]
												})
					

###############
# Messages
###############
@login_required
def messages(request):
	try:
		avatar = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))

	message_list = avatar.message_set.all()
	return render_to_response('messages.html', {'message_list':message_list})


###############
# Mappable Info
###############
info_template_table = {
'Monster'	:'monster_info.html',
'NPC'		:'npc_info.html',
'Avatar'	:'avatar_info.html',
'Equipment'	:'equipment_info.html'}
@login_required
def mappable_info(request, id, mappableType):
	try:
		avatar = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))

	# get info by type
	try: 
		mappable = mapHelper.getMappableObj(mappableType=mappableType, 
											id=id, 
											checkLocation=True, 
											x=avatar.xLocation,
											y = avatar.yLocation) 
	except Exception:
		raise Http404
		
	if mappable is not None:
		if mappableType in info_template_table.keys():
			# load ability list into template
			ability_list = renderTemplate(templateName='ability_list.html',context={'mappable':mappable,'ability_list':avatar.abilitiesOnObject(mappable)})
			return render_to_response(info_template_table[mappableType], {'mappable':mappable, 'ability_list':ability_list})
	
	raise Http404

###############
# Avatar Character
###############
@login_required
def self_avatar_info(request):
	try:
		avatar = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))

	return render_to_response('character.html', {'avatar':avatar,'equip_dict':avatar.getEquipDict()})

###############
# Avatar Equipment
###############
@login_required
def self_avatar_equipment(request):
	try:
		avatar = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))

	equip_dict = avatar.getEquipDict()
	
	return render_to_response('equipment.html', {'mappable':avatar, 'equip_dict':equip_dict})



######################
#   Ability Methods  #
######################

###############
# Perform Ability
###############
@login_required
def perform_ability(request):
	try:
		avatar = getCurrentAvatar(request)
	except Exception:
		return HttpResponseRedirect(reverse('game_index'))
	
	reply = AbilityReply()
	if request.method == 'POST':
		ability = request.POST['ability']
		dataDict = {}
		dataDict.update(request.POST)

		# Convert mappableType and id into target mappable object
		if ('mappableType' in request.POST) and ('id' in request.POST):
			mappableType = request.POST['mappableType']
			targetId = request.POST['id']
			mappable = mapHelper.getMappableObj(mappableType=mappableType, 
												id=targetId, 
												checkLocation=True, 
												x=avatar.xLocation,
												y = avatar.yLocation)
			if mappable is None:
				raise Http404
			
			dataDict['target'] = mappable
		try:
			reply = avatar.performAbilityNamed(abilityName=ability, data=dataDict )
		except Exception, e:
			print "EXCEPTION in Vgame.views.perform_ability: " + str(e)
			return HttpResponseServerError("EXCEPTION in Vgame.views.perform_ability: " + str(e))
	return HttpResponse(reply.outputJSON())



######################
#   Utilities        #
######################

###############
# Render Template
###############
def renderTemplate(templateName, context):
	t = loader.get_template(templateName)
	c = Context(context)
	return t.render(c)

###############
# Get Current Avatar
###############
def getCurrentAvatar(request):
	return Avatar.objects.get(id=request.session['avatar'])



