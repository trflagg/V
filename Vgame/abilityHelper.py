from V.Vgame import abilities
		
def performAbility(actor, abilityName, data):
	print actor.name + " performing " + abilityName
	if abilityName in dir(abilities):
		return abilities.__dict__[abilityName].perform(actor=actor, data=data)
	else:
		raise AttributeError("No ability class named " + abilityName)