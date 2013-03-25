from V.Vgame.models import *

def getMappableObj(mappableType, id, x=0, y=0, checkLocation=False):
	try:
		if (mappableType == Monster.mappableType):
			mappable = Monster.objects.get(id=id)
		elif (mappableType == NPC.mappableType):
			mappable = NPC.objects.get(id=id)
		elif (mappableType == Avatar.mappableType):
			mappable = Avatar.objects.get(id=id)
		elif (mappableType == Equipment.mappableType):
			mappable = Equipment.objects.get(id=id)	
	except Exception:
		mappable = None
		
	if checkLocation:
		if ((mappable.xLocation != x) or (mappable.yLocation != y)):
			mappable = None
	
	return mappable
		
	