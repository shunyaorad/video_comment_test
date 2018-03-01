from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Room
from .forms import NewRoomForm


def home(request):
	rooms = Room.objects.all()
	return render(request, 'home.html', {'rooms': rooms})


def show_room(request, pk):
	room = get_object_or_404(Room, pk=pk)
	return render(request, 'room.html', {'room': room})


def new_room(request):
	user = User.objects.first()  # TODO: get the currently logged in user
	if request.method == 'POST':
		form = NewRoomForm(request.POST)
		if form.is_valid():
			room = form.save(commit=False)
			print(user.username)
			room.owner = user
			room.save()
			return redirect('show_room', pk=room.pk)  # TODO: redirect to the created topic page
	else:
		form = NewRoomForm()
	return render(request, 'new_room.html', {'form': form})
