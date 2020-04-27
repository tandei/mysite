from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	aliasname = models.CharField(max_length=20, verbose_name='昵称')

	def __str__(self):
		return '<Profile: %s for %s>' % (self.aliasname, self.user.username)	

def get_aliasname(self):
	if Profile.objects.filter(user=self).exists():
		profile = Profile.objects.get(user=self)
		return profile.aliasname
	else:
		return ''

def get_aliasname_or_username(self):
	if Profile.objects.filter(user=self).exists():
		profile = Profile.objects.get(user=self)
		return profile.aliasname
	else:
		return self.username

def has_aliasname(self):
	return Profile.objects.filter(user=self).exists()

User.get_aliasname = get_aliasname
User.get_aliasname_or_username = get_aliasname_or_username
User.has_aliasname = has_aliasname
