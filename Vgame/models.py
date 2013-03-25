from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
import math
from V.Vgame import abilities
from V.Vgame import abilityHelper

from datetime import *

######################
#   Map Stuff        #
######################

###############
# Map Type
###############
class MapType(models.Model):
	name = models.CharField(max_length=20)
	ap = models.IntegerField()
	canPlaceMappable = models.BooleanField()
	description = models.CharField(max_length=255)
	def __unicode__(self):
		return self.name

###############
# Map Region
###############
class MapRegion(models.Model):
	name = models.CharField(max_length=20)
	description = models.CharField(max_length=255)
	def __unicode__(self):
		return self.name
		
###############
# Map
###############
class Map(models.Model):
	x = models.IntegerField()
	y = models.IntegerField()
	mapType = models.ForeignKey(MapType)
	mapRegion = models.ForeignKey(MapRegion)
	def __unicode__(self):
		return u'(%s, %s): %s' % (self.x, self.y, self.mapType.name)
	class Admin:
		pass

###############
# Map Data
###############		
class MapData(object):
	def __init__(self,type,region):
		self.type = type
		self.region = region

###############
# Mappable
###############
class Mappable(models.Model):
	mappableType = "Mappable"
	name = models.CharField(max_length=20)
	xLocation = models.IntegerField(null='True')
	yLocation = models.IntegerField(null='True')
	respondsTo = models.CharField(max_length=500,null='True')
	canPerform = models.CharField(max_length=500,null='True')
	created = models.DateTimeField(auto_now_add='True')	
	class Meta:
		abstract = True
	class Admin:
		pass
	
	def __unicode__(self):
		return self.name
		
	def moveTo(self,x,y):
		self.xLocation = x
		self.yLocation = y
	
	def moveBy(self,deltaX,deltaY):
		self.xLocation += deltaX
		self.yLocation += deltaY
		
	def moveNorth(self):
		self.moveBy(0,1)
	def moveSouth(self):
		self.moveBy(0,-1)
	def moveEast(self):
		self.moveBy(1,0)
	def moveWest(self):
		self.moveBy(-1,0)
	
	def sameLocationAs(self, mappable):
		if ((self.xLocation == mappable.xLocation) & (self.yLocation == mappable.yLocation)):
			return True
		else:
			return False
		
	def respondsTo(self, actor):
		return []
	def canPerform(self, target):
		return []
	def abilitiesOnObject(self,target):
		respond = target.respondsTo(self)
		perform = self.canPerform(target)
		return [a for a in respond if a in perform]
	
	def performAbilityNamed(self,abilityName,data={}):
		return abilityHelper.performAbility(actor=self, abilityName=abilityName, data=data)
		
	def getMappableAbilityForObjectDict(self,target):
		return {'mappable': self, 'abilities':target.abilitiesOnObject(self)}

##################
#   Things       #
##################

###############
# Thing
###############
class Thing(Mappable):
	class Meta:
		abstract = True

###############
# Small Thing
###############
class SmallThing(Thing):
	content_type = models.ForeignKey(ContentType, null='True')
	object_id = models.PositiveIntegerField(null='True')
	owner = generic.GenericForeignKey('content_type', 'object_id')
	class Meta:
		abstract = True

###############
# Item
###############	
class Item(SmallThing):
	def respondsTo(self, actor):
		list = SmallThing.respondsTo(self, actor)
		list.append("Take")
		return list

	def targetOf_Take(self, actor, payload, result):
		if (result == True):
			self.save()


EQUIPMENT_SLOT_CHOICES = (
	('Head', 'Head'),
	('OnHand', 'OnHand'),
	('OffHand', 'OffHand'),
	('Body', 'Body'),
	('Foot', 'Foot'),
)
EQUIPMENT_STAT_CHOICES = (
	('Strength', 'Strength'),
	('Toughness', 'Toughness'),
	('Willpower', 'Willpower'),
	('Intuition', 'Intuition'),
)

###############
# Equipment Type
###############
class EquipmentType(models.Model):
	name = models.CharField(max_length = 20)
	slot = models.CharField(max_length = 20, choices=EQUIPMENT_SLOT_CHOICES)
	stat = models.CharField(max_length = 20, choices=EQUIPMENT_STAT_CHOICES)
	description = models.CharField(max_length=255)
	
	class Admin:
		pass
	def __unicode__(self):
		return self.name

###############
# Material
###############
class Material(models.Model):
	name = models.CharField(max_length = 20)
	modifier = models.IntegerField()
	description = models.CharField(max_length=255)
	
	class Admin:
		pass
	def __unicode__(self):
		return self.name

###############
# Equipment
###############
class Equipment(SmallThing):
	mappableType = "Equipment"
	equipmentType = models.ForeignKey(EquipmentType)
	material = models.ForeignKey(Material)
	modifier = models.IntegerField()
	
	def getStat(self):
		return self.equipmentType.stat

	def save(self):
		#Store the name
		self.name = self.getName()
		super(SmallThing, self).save()
	
	def name(self):
		return self.getName()
		
	def getName(self):
		return u'%s %s' % (self.material.name, self.equipmentType.name)	

	def respondsTo(self, actor):
		list = SmallThing.respondsTo(self, actor)
		list.append("Equip")
		return list

###############
# Big Thing
###############
class BigThing(Thing):
	description = models.CharField(max_length=255)
	class Meta:
		abstract = True


###############
# Spell
###############
class Spell(models.Model):
	name = models.CharField(max_length=20)
	description = models.CharField(max_length=255)

######################
#   Characters       #
######################

###############
# Game Character
###############
class GameCharacter(Mappable):
	sex = models.CharField(max_length=20,null=True)
	gold = models.IntegerField(default=0)
	items = generic.GenericRelation(Item)
	MAX_ITEMS = 4
	class Meta:
		abstract = True
		
	def canPerform(self, target):
		list = Mappable.canPerform(self, target)
		list.append("Take")
		return list
		
	def gainGold(self,amount):
		self.checkGold()
		self.gold += amount
	def loseGold(self,amount):
		self.checkGold()
		self.gold -= amount
	def checkGold(self):
		if (self.gold == None):
			self.gold = 0
			
	### Item Methods
	def receiveItem(self, item):
		if(len(self.items.all()) < self.MAX_ITEMS):
			item.owner = self
			item.xLocation = None
			item.yLocation = None
			item.save()
			return True
		else:
			return False
	
	def loseItem(self, item):
		item.owner = None
		item.save()
	
	def dropItem(self, item):
		self.loseItem(item)
		item.moveTo(self.xLocation, self.yLocation)

	def loseAllItems(self):
		for i in self.items.all():
			self.loseItem(i)
			
	def actorFor_Take_pre(self, target,payload):
		return self.receiveItem(target)

	def actorFor_Take_post(self,target,payload,r):
		pass

###############
# NPC
###############
class NPC(GameCharacter):
	mappableType = "NPC"
	line = models.CharField(max_length=100)
	description = models.CharField(max_length=255)
	def respondsTo(self, actor):
		list = GameCharacter.respondsTo(self, actor)
		list.append("Talk")
		return list
	def targetOf_Talk(self,actor,payload):
		print self.line
	class Admin:
		pass

###############
# Stats
###############
class Stats(models.Model):
	strength = models.IntegerField(default=0)
	toughness = models.IntegerField(default=0)
	willPower = models.IntegerField(default=0)
	intuition = models.IntegerField(default=0)
	def __unicode__(self):
		return str(self.id)
	def copyFrom(self, s):
		self.strength = s.strength
		self.toughness = s.toughness
		self.willPower = s.willPower
		self.intuition = s.intuition
	class Admin:
		pass
	class Meta:
		verbose_name_plural = "Stats"

###############
# Stat Progression
###############
class StatProgression(models.Model):
	strength = models.DecimalField(max_digits=4, decimal_places=2)
	toughness = models.DecimalField(max_digits=4, decimal_places=2)
	willPower = models.DecimalField(max_digits=4, decimal_places=2)
	intuition = models.DecimalField(max_digits=4, decimal_places=2)
	def __unicode__(self):
		return str(self.id)
	class Admin:
		pass
	
###############
# Fighter
###############	
class Fighter(GameCharacter):
	#globals
	mappableType = "Fighter"
	
	hp = models.IntegerField(default=0)
	maxHp = models.IntegerField(default=0)
	sp = models.IntegerField(default=0)
	maxSp = models.IntegerField(default=0)
	xp = models.IntegerField(null='True',default=0)
	stats = models.ForeignKey(Stats, null='True')
	updated = models.DateTimeField(auto_now='True')
	equipment = generic.GenericRelation(Equipment)

	class Meta:
		abstract = True
	
	### Number methods
	def checkAmt(self,amount):
		if(amount == None):
			return 0
		else:
			return int(amount)
	def gainHp(self,amount):
		self.hp += self.checkAmt(amount)
		if (self.hp > self.maxHp):
			self.hp = self.maxHp
	def loseHp(self, amount):
		self.hp -= self.checkAmt(amount)
	def resetHp(self):
		self.hp = self.maxHp

	def gainSp(self,amount):
		self.sp += self.checkAmt(amount)
		if (self.sp > self.maxSp):
			self.sp = self.maxSp
	def loseSp(self, amount):
		self.sp -= self.checkAmt(amount)
	def resetSp(self):
		self.sp = self.maxSp

	def gainXp(self,amount):
		self.checkXp()
		self.xp += self.checkAmt(amount)
	def loseXp(self, amount):
		self.checkXp()
		self.xp -= self.checkAmt(amount)
	def checkXp(self):
		if (self.xp == None):
			self.xp = 0
	
	def getAttackPower(self):
		p = self.stats.strength
		for s in self.equipment.all():
			if s.getStat() == "strength":
				p = p + (s.material.modifier * s.modifier)
		return p

	def getDefensePower(self):
		p = self.stats.toughness
		for s in self.equipment.all():
			if s.getStat() == "toughness":
				p = p + (s.material.modifier * s.modifier)
		return p
		
	def respondsTo(self, actor):
		list = GameCharacter.respondsTo(self, actor)
		list.append("Attack")
		return list
	def canPerform(self, target):
		list = GameCharacter.canPerform(self, target)
		list.append("Attack")
		list.append("Equip")
		return list
	
	def die(self):
		print str(self) + " has died"
		self.moveTo(-1,-1)
		#print("RESURECTION!!")
		#self.resetHp()
			
	### Equipment methods
	def equip(self, equipment):
		#Check if you already have something of that type
		#len(get all equ with the same type) < 1)
		if (len(self.equipment.filter(equipmentType__slot__exact=equipment.equipmentType.slot).all()) == 0):
			self.receiveItem(equipment)
			equipment.save()
			return True
		else:
			return False
	
	def dequip(self, equipment):
		self.dropItem(equipment)

	def dequipAll(self):
		for e in self.equipment.all():
			self.dequip(e)

	def getEquipDict(self):
		equip_dict = {}
		for x, y in EQUIPMENT_SLOT_CHOICES:
			equip_dict[x] = self.equipment.filter(equipmentType__slot__exact=x)
		
		return equip_dict

###############
# Monster Type
###############
class MonsterType(models.Model):
	name = models.CharField(max_length=20)
	maxHp = models.IntegerField()
	maxSp = models.IntegerField()
	averageXp = models.IntegerField()
	stats = models.ForeignKey(Stats)
	averageCount = models.PositiveIntegerField()
	amountWaiting = models.PositiveIntegerField(default=0)
	homeMapType = models.ForeignKey(MapType)
	description = models.CharField(max_length=255)
	def __unicode__(self):
		return self.name
	class Admin:
		pass

###############
# Monster
###############	
class Monster(Fighter):
	mappableType = "Monster"
	monsterType = models.ForeignKey(MonsterType)
	agressionLevel = models.PositiveIntegerField(default=0)
	class Admin:
		pass

#########################
#   Avatar Stuff        #
#########################	

###############
# Tribe
###############
class Tribe(models.Model):
	name = models.CharField(max_length=20)
	homeRegion = models.ForeignKey(MapRegion)
	startLocation = models.ForeignKey(Map)
	startingStats = models.ForeignKey(Stats)
	statProgression = models.ForeignKey(StatProgression)
	hpPerLevel = models.DecimalField(max_digits=4, decimal_places=2)
	spPerLevel = models.DecimalField(max_digits=4, decimal_places=2)
	description = models.CharField(max_length=255)
	def __unicode__(self):
		return self.name
	class Admin:
		pass

###############
# Clan
###############	
class Clan(models.Model):
	name = models.CharField(max_length=20)
	tribe = models.ForeignKey(Tribe)
	description = models.CharField(max_length=255)
	def __unicode__(self):
		return self.name
	class Admin:
		pass

###############
# Avatar
###############
class Avatar(Fighter):
	#Constants
	mappableType = "Avatar"
 	MAX_MESSAGES = 20
	ATTACK_AP_COST = 5
	AP_PER_SECOND = 0.1
	XP_PER_LEVEL = 100
	XP_PER_LEVEL_GROWTH_RATE = 2
	LP_PER_LEVEL = 4
	MAX_AVATARS_PER_USER = 4
	
	#Fields
	virtue = models.IntegerField(default=0)
	knowledge = models.IntegerField(default=0)
	fightingAbility = models.IntegerField(default=0)
	speed = models.IntegerField(default=0)
	stamina = models.IntegerField(default=0)
	ap = models.IntegerField(default=0)
	maxAp = models.IntegerField(default=0)
	tribe = models.ForeignKey(Tribe, null='True')
	clan = models.ForeignKey(Clan, null='True')
	level = models.IntegerField(default=0)
	lp = models.IntegerField(default=0)
	user = models.ForeignKey(User, null='True')
	class Admin:
		pass
	
	### Creation Methods
	
		
	###  Movement Methods
	def moveToMap(self, map, apFactor=1):
		# If we can move there
		if not map.mapType.canPlaceMappable:
			return False

		#if avatar has the ap
		totalAp = (map.mapType.ap * apFactor) - self.speed
		if(self.ap >= totalAp):
			self.loseAp(totalAp)
			self.moveTo(map.x, map.y)
			return True
		else:
			return False
	
	### Combat Methods
	def getAttackPower(self):
		base = Fighter.getAttackPower(self)
		return base + self.fightingAbility
	def getDefensePower(self):
		base = Fighter.getDefensePower(self)
		return base + self.fightingAbility
		
	def killedTarget(self, target):
		self.systemMessage("You killed the " + target.name + ".")
		#Grab XP
		self.systemMessage("You gain " + str(target.xp) + " XP.")
		self.gainXp(int(target.xp))
		#Grab gold
		if (target.gold != 0):
			self.systemMessage("You gain " + str(target.gold) + " gold.")
			self.gainGold(int(target.gold))
	
	def die(self):
		self.systemMessage("You Died. HOWEVER... You have been miraculously resurrected by some benevolent force. You find yourself completely healed, and back at your place of birth.  Unfortunately you are completely exhausted and must rest before continuing... Oh, and looters stole your gold.")
		self.ap = 0
		self.gold = 0
		self.resetHp()
		self.resetSp()
		newAvatar.moveTo(newAvatar.tribe.startLocation.x,newAvatar.tribe.startLocation.y)
		self.save()
		
	###  Message Methods
	def clearMessages(self):
		for m in self.message_set.all().iterator():
			m.delete()
	def addMessage(self, message, sender):
		#create new message
		m = Message.objects.create(message=message, sender = sender, avatar=self)
		
		#check for max messages
		if (self.message_set.count() > self.MAX_MESSAGES):
			#delete oldest
			deadMessage = self.message_set.order_by('timestamp','id')[0]
			deadMessage.delete()
	def systemMessage(self,message):
		#add message with 'system' as sender
		self.addMessage(message=message, sender="SYSTEM")
	
	###  Ability Methods
	def respondsTo(self, actor):
		list = Fighter.respondsTo(self, actor)
		list.append("Message")
		return list

	def canPerform(self, target):
		list = Fighter.canPerform(self, target)
		
		#Don't allow PVP
		if (target.mappableType == Avatar.mappableType):
			list.remove("Attack")
		list.append("Message")
		list.append("Talk")
		list.append("Take")
		return list

	###  Leveling Methods
	def gainXp(self, amount):
		Fighter.gainXp(self, amount)
		if ( math.floor(self.xp / self.XP_PER_LEVEL) > (self.level - 1)):
			#Level up!
			self.levelUp()
	
	def gainLp(self, amount):
		self.lp += amount
		self.systemMessage("You just gained " + str(amount) + " lp.  You have a total of " + str(self.lp) + " lp.")
	def loseLp(self,amount):
		self.lp -= amount
	def lpCost(self, aqu):
		#For now, each new aqu level is only 1 lp
		#Can change later to sliding scale
		return 1
	def increaseVirtue(self):
		if self.lp >= self.lpCost(self.virtue):
			self.loseLp(self.lpCost(self.virtue))
			self.virtue += 1
		else:
			self.systemMessage("You need " + str(self.lpCost(self.virtue)) + " lp to increase virtue.")
	def increaseKnowledge(self):
		if self.lp >= self.lpCost(self.knowledge):
			self.loseLp(self.lpCost(self.knowledge))
			self.knowledge += 1
		else:
			self.systemMessage("You need " + str(self.lpCost(self.knowledge)) + " lp to increase knowledge.")
	def increaseFightingAbility(self):
		if self.lp >= self.lpCost(self.fightingAbility):
			self.loseLp(self.lpCost(self.fightingAbility))
			self.fightingAbility += 1
		else:
			self.systemMessage("You need " + str(self.lpCost(self.fightingAbility)) + " lp to increase fightingAbility.")
	def increaseStamina(self):
		if self.lp >= self.lpCost(self.stamina):
			self.loseLp(self.lpCost(self.stamina))
			self.stamina += 1
		else:
			self.systemMessage("You need " + str(self.lpCost(self.stamina)) + " lp to increase stamina.")
	def increaseSpeed(self):
		if self.lp >= self.lpCost(self.speed):
			self.loseLp(self.lpCost(self.speed))
			self.speed += 1
		else:
			self.systemMessage("You need " + str(self.lpCost(self.speed)) + " lp to increase speed.")
	def levelUp(self):
		self.level += 1
		self.systemMessage("You just gained a level! You are now level " + str(self.level))
		#increase stats
		self.stats.strength = math.floor(self.tribe.statProgression.strength * self.level)
		self.stats.toughness = math.floor(self.tribe.statProgression.toughness * self.level)
		self.stats.intuition = math.floor(self.tribe.statProgression.intuition * self.level)
		self.stats.willPower = math.floor(self.tribe.statProgression.willPower * self.level)
		self.maxHp = math.floor(self.tribe.hpPerLevel * self.level)
		self.resetHp()
		self.maxSP = math.floor(self.tribe.spPerLevel * self.level)
		self.resetSp()
		#dish out points
		self.gainLp(Avatar.LP_PER_LEVEL)
	
	###  AP Methods
	def gainAp(self,amount):
		self.ap += amount
		if (self.ap > self.maxAp):
			self.ap = self.maxAp
	def loseAp(self, amount):
		self.ap -= amount
	def resetAp(self):
		self.ap = self.maxAp
	def setAp(self, amount):
		self.ap = amount

	### AP & Save Methods
	def addApForTime(self):
		#Get diff
		diff = datetime.now() - self.updated
		#get seconds
		secs = diff.seconds + (diff.days * 86400)
		#(Ap/Sec + speed) * secs
		self.gainAp(math.floor((Avatar.AP_PER_SECOND) * secs))

	def save(self):
		#Add some ap
		self.addApForTime()
		super(Fighter, self).save()

###############
# Message
###############		
class Message(models.Model):
	message = models.CharField(max_length=500)
	timestamp = models.DateTimeField(auto_now_add='True')
	sender = models.CharField(max_length=20, null='True')
	avatar = models.ForeignKey(Avatar)
	
	class Meta:
		ordering = ['-timestamp','id']
	def __unicode__(self):
		return u'(%s, %s): %s' % (self.timestamp, self.sender, self.message)
		

