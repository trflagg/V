from django import forms
from django.http import Http404
from django.template import Context, Template,loader
from V.Vgame.abilityReply import AbilityReply
import V.Vgame.models
import random
import math

class Ability:
	@staticmethod
	def getAPCost(actor, data):
		return 0

######################
#   Move             #
######################
class Move(Ability):
	@staticmethod
	def perform(actor, data):
		checkDataForKeys(data, ('deltaX','deltaY'))
		deltaX = int(data['deltaX'][0])
		deltaY = int(data['deltaY'][0])
		reply = AbilityReply()
		
		possibleMap = V.Vgame.models.Map.objects.select_related().get(x=(actor.xLocation+deltaX),y=(actor.yLocation+deltaY))
		data['map'] = possibleMap
		
		# If we have the ap
		if actor.ap >= Move.getAPCost(avatar=actor, data=data):
			# And we can move there
			if possibleMap.mapType.canPlaceMappable:
				#Remove the ap
				actor.loseAp(Move.getAPCost(avatar=actor, data=data))
				#Move
				actor.moveTo(possibleMap.x, possibleMap.y)
				#Save
				actor.save()
				reply.setReply('map')
				reply.setReply('character')
				reply.setReply('info')
			else:
				if actor.mappableType == 'Avatar':
					actor.systemMessage(message='You cannot move there.')
					reply.setReply('messages')
		else:
			if actor.mappableType == 'Avatar':
				actor.systemMessage(message='You do not have enough ap to move.')
				reply.setReply('messages')
		
		return reply
				
	@staticmethod
	def getAPCost(avatar, data):
		checkDataForKeys(data, ('map','deltaX','deltaY'))
		possibleMap = data['map']
		deltaX = data['deltaX']
		deltaY = data['deltaY']
				
		# Check for diagonalMovement
		if ((deltaX != 0) & (deltaY != 0)):
			#diagonal = 1.5*ap
			factor = 1.5
		else:
			factor = 1
		
		amt = max(1, (possibleMap.mapType.ap * factor) - avatar.speed)
		return amt

######################
#   Attack           #
######################	
class Attack(Ability):
	@staticmethod
	def perform(actor, data):
		checkDataForKeys(data, ['target'])
		target = data['target']
		reply = AbilityReply()
		hit = False
		dead = False
		
		if actor.mappableType == 'Avatar':
			apCost = Attack.getAPCost(avatar=actor, data=data)
			if (actor.ap < apCost):
				actor.systemMessage("You do not have enough ap to Attack")
				reply.setReply('messages')
				return reply
			else:
				actor.loseAp(apCost)
		
		#Calculate Hit
		hitClass = actor.getAttackPower() - target.getDefensePower()
		hitTable = 	{	0: .6,
			1: .7,	-1:.5,
			2: .8,	-2:.4,
			3: .9,	-3:.3	}
		if (hitClass <= -4):
			randTarget = .2
		elif (hitClass >= 4):
			randTarget = .95
		else:
			randTarget = hitTable[hitClass]
		
		if (random.random() <= randTarget):
			#Hit!
			#Calculate Damage
			#Attack Power between .5 and 2.0
			damageRand = random.uniform(.5, 2)
			damage =  int(max(math.ceil(actor.getAttackPower() * damageRand), 1))
			hit = True
			target.loseHp(damage)
			#Check for death
			if(target.hp <= 0):
				#die
				if actor.mappableType == 'Avatar':
					reply.setAll()
					actor.killedTarget(target)
				target.die()
				dead = True
		
		# Check if actor is Avatar
		if actor.mappableType == 'Avatar':
			# add messages
			if hit:
				msg = 'You hit the ' + target.name + ' and did ' + str(damage) + ' points of damage.'
				actor.systemMessage(message=msg)
				#reply with message,map,avatar,ability, and monster info
				reply.setReply('messages')
				reply.setReply('map')
				reply.setReply('character')
				reply.setReply('info')
			else:
				msg = 'You missed the ' + target.name + '.'
				actor.systemMessage(message=msg)
				reply.setReply('messages')
		
		# Check if target is Avatar
		elif target.mappableType == 'Avatar':
			if hit:
				msg = 'You were hit by the ' + actor.name + ' and took ' + str(damage) + ' points of damage.'
				target.systemMessage(message=msg)
				reply.setReply('character')
				reply.setReply('messages')
			else:
				msg = 'The ' + actor.name + ' attacked you but missed.'
				target.systemMessage(message=msg)
				reply.setReply('messages')
					
		#Check for Monster Retribution
		if (target.mappableType == "Monster") and (actor.mappableType != "Monster") and (not dead):
			# agression 0 = Don't Attack
			# agression 1 = Only Attack if Hit
			if target.agressionLevel == 1:
				if hit:
					d2 = data.copy()
					d2['target'] = actor
					reply.mergeReply(target.performAbilityNamed(abilityName='Attack', data=d2))
			# agression 2 = Always Attack
			if target.agressionLevel == 2:
				d2 = data.copy()
				d2['target'] = actor
				reply.mergeReply(target.performAbilityNamed(abilityName='Attack', data=d2))
		
		#save 'em
		actor.save()
		target.save()
		
		return reply
	
	@staticmethod
	def getAPCost(avatar, data):
		#Base - (half of speed)
		return max(V.Vgame.models.Avatar.ATTACK_AP_COST - math.ceil(avatar.speed / 2), 1)

######################
#   Message          #
######################	
class Message(Ability):
	
	class form(forms.Form):
		message = forms.CharField(max_length = 256)
	
	@staticmethod
	def perform(actor, data):	
		checkDataForKeys(data, ['target'])
		target = data['target']
		reply = AbilityReply()
		# Check for message
		if 'message' in data.keys():
			message = ''.join(data['message'])
			target.addMessage(message=str(message), sender=actor.name)
		# No message
		else:
			# Send back form
			reply.setAbilityText(renderAbilityForm({'form':Message.form(), 'ability':"Message", 
													'mappableId':target.id, 'mappableType':target.mappableType}))
		return reply

######################
#   Equip            #
######################
class Equip(Ability):
	
	@staticmethod
	def perform(actor, data):
		checkDataForKeys(data, ['target'])
		target = data['target']
		reply = AbilityReply()
		
		# Check for Equip
		if actor.equip(target):
			target.save()
			if actor.mappableType == 'Avatar':
				actor.systemMessage('You equipped the ' + str(target))
				reply.setReply('messages')
				reply.setReply('equipment')
				reply.setReply('character')
		else:
			if actor.mappableType == 'Avatar':
				actor.systemMessage('You cannot equip the ' + str(target))
				reply.setReply('messages')
		
		return reply

######################
#   Take             #
######################
class Take(Ability):
	name = 'Take'
	
	@staticmethod
	def perform(actor, data):
		checkDataForKeys(data, ['target'])
		target = data['target']
		reply = AbilityReply()
		
		#Check it's an item
		if target.mappableType != 'Item':
			if actor.mappableType == 'Avatar':
				actor.systemMessage('You cannot take that.')
				reply.setReply('messages')
				return reply
				
		#Call take method, check result
		if actor.receiveItem(target):
			target.save()
			if actor.mappableType == 'Avatar':
				actor.systemMessage('You took the ' + str(target))
				reply.setReply('messages')
				reply.setReply('equipment')
				reply.setReply('character')
		else:
			if actor.mappableType == 'Avatar':
				actor.systemMessage('You cannot take the ' + str(target))
				reply.setReply('messages')
		
		return reply
	
######################
#   Spell            #
######################
class Spell(Ability):
	name = 'Spell'
		
	class form(forms.Form):
		spell = forms.ChoiceField(choices=[('fire','fire'),('heal','heal')])
	
	@staticmethod	
	def perform(actor, data):		
		target = kwargs['target']
		actor = kwargs['actor']
		spell = kwargs['spell']
		print str(actor) + " performing the spell " + str(spell) + " on " + str(target)
		return 1

#######################
#   Utility Functions #
#######################
def renderAbilityForm(context):
	t = loader.get_template('ability_form.html')
	c = Context(context)
	return t.render(c)

def checkDataForKeys(data,keyList):
	# if keylist is not an improper subset of data, raise hell!
	for k in keyList:
		if k not in data.keys():
			raise AttributeError("Ability is missing key " + k)