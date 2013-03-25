from V.Vgame.models import *
import V.minlis.models
import datetime
import random

def minuteTask():
	moveWanderingMonsters()
	
def moveWanderingMonsters():
	#Move wandering monsters
	wanderingList = Monster.objects.filter(agressionLevel__exact=0).all()
	for monster in wanderingList:
		#Get all surrounding maps that have the monster's home type
		#TODO: Remove this code redundancy (also used in map view)
		map_list = Map.objects.filter(x__gte=(monster.xLocation-1),x__lte=(monster.xLocation+1),y__gte=(monster.yLocation-1),y__lte=(monster.yLocation+1),mapType__exact=monster.monsterType.homeMapType).all()
		
		#pick one at random 
		mNum = random.randint(0,len(map_list) - 1)
		#And go there
		monster.moveTo(x=map_list[mNum].x, y=map_list[mNum].y)
		print str(monster) + " wandered to (" + str(monster.xLocation) + ", " + str(monster.yLocation) + ")"
		
		#Save monster
		monster.save()
		
def generateMonsters():
	#Check how many monsters there are based on type
	#TODO: Later change this to check by mapType or quest, or something like that
	typeList = MonsterType.objects.all()
	for t in typeList:
		currentCount = Monster.objects.filter(monsterType__exact=t).count() + t.amountWaiting
		print t.name + ": " + str(currentCount) + "/ average of " + str(t.averageCount)
		
		#If we're under, figure out how many to make
		if currentCount < t.averageCount:
			#Right now, random number between enough to get to average, and double that
			mNum = t.averageCount - currentCount
			makeAmount = random.randint(mNum, mNum * 2)
			#make one a minute
			scheduledTime = datetime.datetime.now()
			for i in range(makeAmount):
				V.minlis.models.EvalEventRequest.objects.create(scheduledTime=scheduledTime, evalString = "monsterHelper.autoMakeRandomMonsterOfType('" + str(t.name) + "')")
				print "Creating a new " + str(t.name) + " at " + str(scheduledTime)
				scheduledTime = scheduledTime + datetime.timedelta(minutes=1)
			
			t.amountWaiting = t.amountWaiting + makeAmount
			t.save()

#called by eventRequest of generateMonsters
def autoMakeRandomMonsterOfType(typeName):
	#create the monster
	makeRandomMonsterOfType(typeName)
	#remove from number waiting
	mType = MonsterType.objects.get(name__exact=typeName)
	mType.amountWaiting = mType.amountWaiting - 1
	mType.save()
	
def makeRandomMonsterOfType(typeName):
	#print "Making new " + str(typeName)
	
	#Get map cells with home mapType
	monsterType = MonsterType.objects.get(name__exact=typeName)
	cells = Map.objects.filter(mapType__exact=monsterType.homeMapType).all()
	#Get random map cell out of the list
	cellNum = random.randint(0,cells.count()-1)
	startingMap = cells[cellNum]
	
	#Set things based on type
	newMonster = Monster(
				xLocation = startingMap.x,
				yLocation = startingMap.y,
				name = monsterType.name,
				monsterType = monsterType,
				stats = monsterType.stats,
				maxHp = monsterType.maxHp,
				maxSp = monsterType.maxSp)
				
	#xp +/- 10% of average
	#TODO: Make give higher xp monsters an Hp and Sp boost
	tenPercent = round(monsterType.averageXp * .1)
	newMonster.xp = random.randint(monsterType.averageXp - tenPercent, monsterType.averageXp + tenPercent)
	
	#Give'em full health
	newMonster.resetHp()
	newMonster.resetSp()
	
	#Save
	newMonster.save()
	return newMonster
		
	