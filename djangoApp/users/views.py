from django.shortcuts import render, redirect
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

def register(request):
	if request.method == "POST":
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			#user = form.save()
			print(form.data)
			username = form.cleaned_data.get('email')
			if User.objects.filter(username = username):
				messages.error(request, f'The email address "{username}" is already registered.')
				return redirect('register')
			email = form.cleaned_data.get('email')
			full_name = form.cleaned_data.get('full_name')
			password = form.cleaned_data.get('password1')
			user = User(username = username, email = email, first_name = full_name)
			user.set_password(password)
			user.save()
			group = Group.objects.get(name='customer')
			user.groups.add(group)
			messages.success(request, f'Successfully created an account for { email }. Log in Now!')
			return redirect ('login')
		else:
			messages.warning(request, f'There was an error!')
	else:
		form = UserRegisterForm()
	return render(request,'users/register.html', {'form':form})

@login_required
def profile(request):
	return render(request, 'users/profile.html')

def profileUpdate(request):
        if request.method == "POST":
#                u_form = UserUpdateForm(request.POST, instance=request.user)
#                p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
                u_form = UserUpdateForm(request.POST, instance=request.user)
                p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

                if u_form.is_valid and p_form.is_valid:
                        u_form.save()
                        p_form.save()
                        messages.success(request, f'Your profile has been updated!')
                        return redirect ('profile')
                else:
                        messages.warning(request, f'There was an error!')

        else:
                u_form = UserUpdateForm(instance=request.user)
                p_form = ProfileUpdateForm()

        context = {
                'u_form':u_form,
                'p_form':p_form
        }
        return render(request, 'users/profileUpdate.html',context)


