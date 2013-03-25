from django.db import models
from django.contrib.auth.models import User

# User Stuff
##############################
class VUser(models.Model):
	user = models.ForeignKey(User, unique=True)