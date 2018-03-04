from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect

from .forms import SignUpForm
from rooms.models import Profile


def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			profile = Profile(
				email=form.cleaned_data['email'],
				username=form.cleaned_data['username']
			)
			profile.user = user
			profile.save()
			auth_login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form': form})
