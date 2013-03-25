from V.Vgame.models import *
import random

###############
# New Avatar
###############
def newAvatar(form, user=None):
	"""
	Creates a new avatar from a NewAvatarForm.
	Validates the form and returns true if the
	avatar was created, and false otherwise.
	"""
	# Authenticate the form
	if (form.is_valid()):
		
		# Check if user is allowed an avatar
		if (user != None and user.avatar_set.count() >= Avatar.MAX_AVATARS_PER_USER):
			form.general_error = "You may not create any more characters."
			return False

		# create new avatar
		newAvatar = Avatar()
		# set basic stuff
		newAvatar.name = form.cleaned_data['name']
		
		newAvatar.sex = form.cleaned_data['gender']
		newAvatar.tribe = form.cleaned_data['tribe']
	
		clanCount = newAvatar.tribe.clan_set.count()
		clanNum = random.randint(0,clanCount - 1)
		newAvatar.clan = newAvatar.tribe.clan_set.all()[clanNum]
		newAvatar.level = 0
		newAvatar.created = datetime.min
		newAvatar.updated = datetime.min
		# set fighter stuff
		s = Stats.objects.create()
		newAvatar.stats = s
		# set user
		newAvatar.user = user
		newAvatar.save()
		# set location
		newAvatar.moveTo(newAvatar.tribe.startLocation.x,newAvatar.tribe.startLocation.y)
		# set stats & dish out lp
		newAvatar.levelUp()
		newAvatar.stats.save()
		newAvatar.save()
		return True
	
	return False
	