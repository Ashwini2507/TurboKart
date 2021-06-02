from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

#class User(AbstractUser):
#	username = None
#	email = models.EmailField(_('email address'), unique=True)

#	USERNAME_FIELD = 'email'
#	REQUIRED_FIELDS = []

#	objects = CustomUserManager()

#	def __str__(self):
#		return self.email

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone_number = models.CharField(max_length = 15, blank = True)
	image = models.ImageField(default = 'profile_pics/default.png', upload_to = 'profile_pics')
	def __str__(self):
		return f'{self.user.username} Profile'
