from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()
	full_name = forms.CharField(max_length=255)
	#username = email
	class Meta:
		model = User
		fields = ['email','full_name','password1','password2']

class UserUpdateForm(forms.ModelForm):
        email = forms.EmailField()
        class Meta:
                model = User
                fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['phone_number','image']
