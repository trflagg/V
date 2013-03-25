#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Taylor Flagg on 2008-03-31.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import unittest
from V.Vgame.models import *
from V.Vgame import avatarHelper
from V.Vgame import monsterHelper
from V.Vgame.forms import NewAvatarForm
from V.Vsite.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase as djangoTestCase
import time

class AvatarTestCase(unittest.TestCase):
	def testAvatarMovement(self):
		self.avatar = Avatar.objects.get(name='Test')
		self.avatar.moveTo(3,3)
		self.assertEqual(self.avatar.xLocation,3,"xLocation = 3 by moveTo")
		self.assertEqual(self.avatar.yLocation,3,"yLocation = 3 by moveTo")
		
		self.avatar.moveBy(1,-1)
		self.assertEqual(self.avatar.xLocation,4,"xLocation = 4 by moveTo")
		self.assertEqual(self.avatar.yLocation,2,"yLocation = 2 by moveTo")
		
		self.avatar.moveNorth()
		self.avatar.moveSouth()
		self.assertEqual(self.avatar.xLocation,4,"xLocation = 4 by moveNorth, moveSouth")
		
		self.avatar.moveEast()
		self.avatar.moveWest()
		self.assertEqual(self.avatar.yLocation,2,"yLocation = 2 by moveEast, moveWest")

	def testMessageCreation(self):
		avatar = Avatar.objects.get(name='Test')
		for i in range(0,avatar.MAX_MESSAGES + 5):
			avatar.addMessage(message=str(i),sender="system")
		#test only MAX_MESSAGES remain
		self.assertEqual(avatar.message_set.count(), avatar.MAX_MESSAGES, "Only allowed MAX_MESSAGES")
		#test only oldest remain
		self.assertEqual(avatar.message_set.order_by('timestamp','-id')[0].message, str(avatar.MAX_MESSAGES + 5 - 1), "Only oldest remain")
		#test creation by the system
		avatar.systemMessage(message="System Message")
		self.assertEqual(avatar.message_set.order_by('timestamp','-id')[0].message, "System Message", "System Message Sent")
		
	def testMessageAbility(self):
		avatar = Avatar.objects.get(name='Test')
		avatar2 = Avatar.objects.get(name='TestFighter')
		
		#test Message ability
		avatar2.clearMessages()
		avatar.performAbilityNamed(abilityName='Message',data={'target':avatar2,
										'message':'Ability test'})
		self.assertEqual(avatar2.message_set.count(), 1, "Message Ability creates message")
		self.assertEqual(avatar2.message_set.get().message, "Ability test", "Correct message sent")
		self.assertEqual(avatar2.message_set.get().sender, avatar.name, "Sender set to actor's name")
		#test clearMessage
		avatar2.clearMessages()
		self.assertEqual(avatar2.message_set.count(), 0, "clearMessages set message_set.count() to 0")
		
	def testAp(self):
		avatar = Avatar.objects.get(name='Test')
		#test reset and loss of ap
		avatar.save()
		avatar.resetAp()
		avatar.loseAp(20)
		self.assertEqual(avatar.ap, avatar.maxAp - 20, "Reset and Lose Ap")
		avatar.save()
		#test ap regeneration
		time.sleep(60)
		avatar.save()
		self.assert_(avatar.ap > (avatar.maxAp - 20))
		time.sleep(60)
		self.assert_(avatar.ap <= avatar.maxAp, "Can't gain past maximum")
		#test movement reduces ap
		avatar.resetAp()
		m = Map.objects.get(x=avatar.xLocation + 1, y=avatar.yLocation)
		avatar.moveToMap(m)
		self.assert_(avatar.ap < avatar.maxAp)
		avatar.ap = 0
		result = avatar.moveToMap(m)
		self.assertEqual(avatar.ap, 0)
		self.assertEqual(result, False)
	
	def testLevelUp(self):
		avatar = Avatar.objects.get(name='Test')
		originallevel = avatar.level
		originallp = avatar.lp
		#test gaining enough XP grants level and lp
		avatar.gainXp(Avatar.XP_PER_LEVEL + 10)
		self.assert_(avatar.level > originallevel)
		self.assertEqual(avatar.lp, originallp + Avatar.LP_PER_LEVEL)
		#test gaining aqcu, up virtue lp times
		for x in range(0,avatar.lp):
			originalVirtue = avatar.virtue
			avatar.increaseVirtue()
			self.assertEqual(originalVirtue,avatar.virtue - 1)
		#test gaining aqcu without lp
		originalSpeed = avatar.speed
		avatar.increaseSpeed()
		self.assertEqual(originalSpeed, avatar.speed)

class MonsterTestCase(unittest.TestCase):
	def testMonsterCreate(self):
		trollCount = Monster.objects.filter(monsterType__name__exact='Troll').count()
		#Create random Troll
		newMonster = monsterHelper.makeRandomMonsterOfType('Troll')
		
		#Check if created
		newCount = Monster.objects.filter(monsterType__name__exact='Troll').count()
		self.assertEqual(trollCount + 1, newCount)

class ItemTestCase(unittest.TestCase):
	def testItems(self):
		avatar = Avatar.objects.get(name='Test')
		item1 = Item.objects.get(id=1)
		item2 = Item.objects.get(id=2)
		#Test item ownership
		item1.owner = avatar
		item1.save()
		self.assertEqual(len(avatar.items.all()), 1)
		
		#Test receiving item
		avatar.receiveItem(item2)
		self.assertEqual(len(avatar.items.all()), 2)
		self.assertEqual(item2.owner, avatar)
		
		#Test losing item
		avatar.loseItem(item2)
		self.assertEqual(len(avatar.items.all()), 1)
		self.assertNotEqual(item2.owner, avatar)

		#Test dropping item
		avatar.dropItem(item1)
		self.assertEqual(len(avatar.items.all()), 0)
		self.assertNotEqual(item1.owner, avatar)
		self.assertEqual(item1.xLocation, avatar.xLocation)
		self.assertEqual(item1.yLocation, avatar.yLocation)
		
		#Test receiving too many items
		for c in range(1,Avatar.MAX_ITEMS + 2):
			i = Item.objects.get(id=c)
			avatar.receiveItem(i)
		self.assertEqual(len(avatar.items.all()), Avatar.MAX_ITEMS)
		
		#Test losing all items
		avatar.loseAllItems()
		self.assertEqual(len(avatar.items.all()), 0)		
		
	def testEquipmentEquip(self):
		avatar = Avatar.objects.get(name='Test')
		oldAttack = avatar.getAttackPower()
		oldDefense = avatar.getDefensePower()
		helmet = Equipment.objects.get(id=1)
		sword = Equipment.objects.get(id=2)
		staff = Equipment.objects.get(id=3)
		# Test setting owner
		helmet.owner = avatar
		helmet.save()
		self.assertEqual(len(avatar.equipment.all()), 1)		

		# Test equip method
		r = avatar.equip(sword)
		self.assertTrue(r)
		self.assertEqual(len(avatar.equipment.all()), 2)
		self.assertEqual(sword.owner, avatar)
		
		#Test equip increases power
		self.assert_(avatar.getAttackPower > oldAttack)
		self.assert_(avatar.getDefensePower > oldDefense)

		# Test dequip method
		avatar.dequip(helmet)
		self.assertEqual(len(avatar.equipment.all()), 1)
		self.assertNotEqual(helmet.owner, avatar)
		# Test equipping 2 onHand slots
		r = avatar.equip(staff)
		self.assertFalse(r)
		self.assertEqual(len(avatar.equipment.all()), 1)
		self.assertNotEqual(staff.owner, avatar)
		
		# Test dequipping all
		avatar.dequipAll()
		self.assertEqual(len(avatar.equipment.all()), 0)
		
class InteractionTestCase(unittest.TestCase):

	def testTake(self):
		avatar = Avatar.objects.get(name='Test')
		item = Item.objects.get(id=1)

		#Test take ability adds to items
		avatar.performAbilityNamed(abilityName='Take',data={'target':item})
		self.assertEqual(len(avatar.items.all()), 1)
		self.assertEqual(item.owner, avatar)

		avatar.loseAllItems()
		
	def testEquip(self):
		avatar = Avatar.objects.get(name='Test')
		sword = Equipment.objects.get(id=2)

		#Test the equip ability
		avatar.performAbilityNamed(abilityName='Equip',data={'target':sword})
		self.assertEqual(len(avatar.equipment.all()), 1)
		self.assertEqual(sword.owner, avatar)

		avatar.dequipAll()

	def testAttack(self):
		avatar = Avatar.objects.get(name='Test')
		monster = Monster.objects.get(name='Troll')
		monster2 = Monster.objects.get(name='Lesser Demon')
		
		#test attack & reduction of AP
		avatar.resetAp()
		originalap = avatar.ap
		avatar.performAbilityNamed(abilityName='Attack',data={'target':monster})
		self.assert_(avatar.ap < originalap)
		monster.performAbilityNamed(abilityName='Attack',data={'target':monster})

class AvatarFormTestCase(unittest.TestCase):
	def testNewAvatarForm(self):
		# Test empty name
		f = NewAvatarForm({'name':'',
						   'gender':'male',
						   'tribe':'3'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'name')
		
		# Test empty gender
		f = NewAvatarForm({'name':'noExist',
						   'gender':'',
						   'tribe':'3'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'gender')
		
		# Test empty tribe
		f = NewAvatarForm({'name':'noExist',
						   'gender':'male',
						   'tribe':''})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'tribe')
		
		# Test name that already exists
		f = NewAvatarForm({'name':'Test',
						   'gender':'male',
						   'tribe':'3'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'name')
		
		# Test valid form
		f = NewAvatarForm({'name':'noExist',
						   'gender':'male',
						   'tribe':'3'})
		self.assertTrue(f.is_valid())
	
	def checkErrorOnField(self,form, fieldName):
		self.assertTrue(len(form[fieldName].errors) > 0)
		
class AvatarHelperTestCase(unittest.TestCase):
	def getUser(self):
		return User.objects.get(id=2)
		
	def testAvatarHelperNewAvatar(self):
		# Test no duplicate
		f = NewAvatarForm({'name':'Test',
						   'gender':'male',
						   'tribe':'2'})
		self.assertFalse(avatarHelper.newAvatar(f, self.getUser()))
		
		# Test successful creation
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 0)
		f = NewAvatarForm({'name':'noExist',
						   'gender':'male',
						   'tribe':'2'})
		self.assertTrue(avatarHelper.newAvatar(f, self.getUser()))
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 1)
		
		# Test the creation
		self.assertEqual('noExist',Avatar.objects.get(name='noExist').name, "Created Avatar w/ 'NoExist' name")
		a = Avatar.objects.get(name='noExist')
		self.assertEqual('male', a.sex, "Sex correct")
		self.assertEqual(Tribe.objects.get(id=2).name, a.tribe.name, "Tribe correct")
		self.assertEqual(a.tribe.name, a.clan.tribe.name, "Clan set correctly")
		self.assertEqual(a.xLocation, a.tribe.startLocation.x, "Location set correctly")
		self.assertEqual(a.level, 1, "Level 1")
		self.assertEqual(a.lp, Avatar.LP_PER_LEVEL, "Gained LP")

		# Try to create another and go over the limit
		self.assertEqual(self.getUser().avatar_set.count(), Avatar.MAX_AVATARS_PER_USER)
		f = NewAvatarForm({'name':'noExist2',
						   'gender':'male',
						   'tribe':'2'})
		self.assertFalse(avatarHelper.newAvatar(f, self.getUser()))
		self.assertNotEqual(f.general_error, "")
		self.assertEqual(Avatar.objects.filter(name__exact='noExist2').count(), 0)

class AvatarViewTestCase(djangoTestCase):
	def testAvatarIndexView(self):
		# Test Login Required
		response = self.client.get('/v/')
		self.assertEqual(response.status_code, 302)
		response = self.client.post('/v/')
		self.assertEqual(response.status_code, 302)

		# Login
		self.assertTrue(self.client.login(username='test', password='test'))

		# Test getting a page successfully
		response = self.client.get('/v/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'index.html')
		self.assertEqual(response.context[0]['general_error'], "")
		response = self.client.post('/v/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context[0]['general_error'], "")

		# Test avatar doesn't exist
		response = self.client.post('/v/', {'selected_avatar':'-1'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'index.html')
		self.assertNotEqual(response.context[0]['general_error'], "")

		# Test avatar belongs to another user
		response = self.client.post('/v/', {'selected_avatar':'4'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'index.html')
		self.assertNotEqual(response.context[0]['general_error'], "")

		# Test successful avatar selection
		response = self.client.post('/v/', {'selected_avatar':'1'})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(self.client.session['avatar'], 1)

	def testAvatarIndexRedirect(self):
		# Login as user with no avatars
		self.assertTrue(self.client.login(username='NoAvatars', password='test'))	

		# Test redirect
		response = self.client.get('/v/')
		self.assertEqual(response.status_code, 302)

	def testAvatarNewView(self):
		# Test Login Required
		response = self.client.get('/v/new/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 0)
		response = self.client.post('/v/new/', {'name':'noExist',
						   	    'gender':'male',
						   	    'tribe':'2'})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 0)
		
		# Login
		self.assertTrue(self.client.login(username='test',password='test'))
		# Test getting a page returns correct template w/ empty form
		response = self.client.get('/v/new/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newAvatar.html')
		
		# Test invalid tribe
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 0)
		response = self.client.post('/v/new/', {'name':'noExist',
						   	    'gender':'male',
						   	    'tribe':'-1'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newAvatar.html')		
		self.checkErrorOnField(response.context[0]['form'], 'tribe')
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 0)

		# Test successful new Avatar created
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 0)
		response = self.client.post('/v/new/', {'name':'noExist',
						   	    'gender':'male',
						   	    'tribe':'2'})
		self.assertEqual(Avatar.objects.filter(name__exact='noExist').count(), 1)

	def checkErrorOnField(self,form, fieldName):
		self.assertTrue(len(form[fieldName].errors) > 0)

class GameViewTestCase(djangoTestCase):
	def testGameMapView(self):
		# Test login required
		avatar = self.loginAndAvatarForURL(reverse('game_map'))

		# Move avatar to hard-coded location
		avatar.moveTo(4,4)
		avatar.save()

		# Test successful retrieval
		response = self.client.get('/v/map/map/')
		self.assertEqual(response.status_code, 200)
		#self.assertEqual(response.template.name, 'game_map.html')

		# Test context
		#self.assertEqual(response.context['avatar'].name, Avatar.objects.get(id=1).name)
		
		# Move monster, avatar, NPC, and equipment to location
		monster = Monster.objects.get(id=1)
		monster.moveTo(avatar.xLocation, avatar.yLocation)
		monster.save()
		avatar2 = Avatar.objects.get(id=2)
		avatar2.moveTo(avatar.xLocation, avatar.yLocation)
		avatar2.save()
		npc = NPC.objects.get(id=1)
		npc.moveTo(avatar.xLocation, avatar.yLocation)
		npc.save()
		equipment = Equipment.objects.get(id=1)
		equipment.moveTo(avatar.xLocation, avatar.yLocation)
		equipment.save()

		# Get map
		response = self.client.get('/v/map/map/')
		self.assertEqual(response.status_code, 200)
		
		# Check context
		#self.assertEqual(len(response.context['mappable_dict']['Monster']), 1)
		#self.assertEqual(len(response.context['mappable_dict']['NPC']), 1)
		#self.assertEqual(len(response.context['mappable_dict']['Avatar']), 1)
		#self.assertEqual(len(response.context['mappable_dict']['Equipment']), 1)
		
	def testBaseGameMapView(self):
		# Test login required		
		avatar = self.loginAndAvatarForURL(reverse('base_game_map'))

		originalX = avatar.xLocation
		originalY = avatar.yLocation

		# Load page successfully
		response = self.client.get(reverse('base_game_map'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'base_game_map.html')
		response = self.client.post(reverse('base_game_map'))
		self.assertEqual(response.status_code, 200)
		
		# Make sure avatar didn't move
		avatar = Avatar.objects.get(id=self.client.session['avatar'])
		self.assertEqual(originalX, avatar.xLocation)
		self.assertEqual(originalY, avatar.yLocation)
		
		# Test movement
		#TODO: Base this on reverse()
		response = self.client.post(reverse('perform_ability'),{'ability':'Move','deltaX':'-1','deltaY':'1'})
		avatar = Avatar.objects.get(id=self.client.session['avatar'])
		self.assertEqual(originalX - 1, avatar.xLocation)
		self.assertEqual(originalY + 1, avatar.yLocation)

		originalX = avatar.xLocation
		originalY = avatar.yLocation

		# Test failure of movement if no ap
		avatar.setAp(0)
		avatar.save()
		response = self.client.post(reverse('perform_ability'),{'ability':'Move','deltaX':'-1','deltaY':'1'})
		avatar = Avatar.objects.get(id=self.client.session['avatar'])
		self.assertEqual(originalX, avatar.xLocation)
		self.assertEqual(originalY, avatar.yLocation)

	def testMessageView(self):
		# Test login
		avatar = self.loginAndAvatarForURL(reverse('messages'))

		# Test view returns messages
		response = self.client.get(reverse('messages'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['message_list'][1], avatar.message_set.all()[1])

	def testSelfInfoViews(self):
		# Test login
		self.loginAndAvatarForURL(reverse('self_avatar_info'))
		
	def testMappableInfo(self):
		# Move npc to location
		npc = NPC.objects.get(id=1)
		avatar = Avatar.objects.get(id=1)
		npc.moveTo(avatar.xLocation,avatar.yLocation)
		npc.save()
		# Get info
		url = '/v/map/info/'+NPC.mappableType+'/1/'
		avatar = self.loginAndAvatarForURL(url)
		
		# Test npc
		response = self.client.get(url)
		#self.assertEqual(response.template.name, 'npc_info.html')
		
		# Test monster and location required
		monster = Monster.objects.get(id=1)
		monster.moveTo(avatar.xLocation, avatar.yLocation + 1)
		monster.save()
		url = '/v/map/info/'+Monster.mappableType+'/1/'
		noException = True
		#try:
		#	self.client.get(url)
		#except Exception:
		#	noException = False
		#self.assertFalse(noException)
		response = self.client.get(url)
		self.assertEqual(response.template.name, '404.html')
		self.assertEqual(response.status_code, 404)
		
		monster.moveTo(avatar.xLocation, avatar.yLocation)
		monster.save()
		response = self.client.get(url)
		#self.assertEqual(response.template.name, 'monster_info.html')
	
#   def testAbilityList(self):
#   	#login and set avatar
#   	self.client.login(username='test', password='test')
#   	self.client.post(reverse('game_index'), {'selected_avatar':'1'})
#   	
#   	# Move troll & Avatar2 to location
#   	monster = Monster.objects.get(id=1)
#   	avatar2 = Avatar.objects.get(id=2)
#   	avatar = Avatar.objects.get(id=1)
#   	monster.moveTo(avatar.xLocation, avatar.yLocation)
#   	monster.save()
#   	avatar2.moveTo(avatar.xLocation, avatar.yLocation)
#   	avatar2.save()
#
#   	response = self.client.get("/v/map/ability/Monster/1/")
#   	self.assertEqual(response.status_code, 200)
#   	

	def testPerformAbility(self):
		#login and set avatar
		self.client.login(username='test', password='test')
		self.client.post(reverse('game_index'), {'selected_avatar':'1'})
		
		# Move troll to location
		monster = Monster.objects.get(id=1)
		avatar = Avatar.objects.get(id=1)
		monster.moveTo(avatar.xLocation, avatar.yLocation)
		monster.save()

		response = self.client.post(reverse('perform_ability'), {'mappableType':Monster.mappableType, 
																'id':'1', 
																'ability':'Attack'})
		self.assertEqual(response.status_code, 200)
		
		# Move troll away
		monster.moveTo(avatar.xLocation + 1, avatar.yLocation)
		monster.save()
		noException = True
		response = self.client.post(reverse('perform_ability'), {'mappableType':Monster.mappableType, 
																'id':'1', 
																'ability':'Attack'})
		
		
	def loginAndAvatarForURL(self, url):
		# Test login required
		response = self.client.get(url)
		self.assertEqual(response.status_code, 302)
		response = self.client.post(url)
		self.assertEqual(response.status_code, 302)

		# Login
		self.assertTrue(self.client.login(username='test', password='test'))

		# Test avatar requried
		response = self.client.get(url)
		self.assertEqual(response.status_code, 302)
		response = self.client.post(url)
		self.assertEqual(response.status_code, 302)

		# Set avatar
		response = self.client.post(reverse('game_index'), {'selected_avatar':'1'})
		
		# Test success
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		return Avatar.objects.get(id=self.client.session['avatar'])	

if __name__ == '__main__':
	unittest.main()
