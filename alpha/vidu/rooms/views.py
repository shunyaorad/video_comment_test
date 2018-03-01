from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Room
from .forms import NewRoomForm, NewCommentForm
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
	rooms = Room.objects.filter(owner=request.user)
	return render(request, 'home.html', {'rooms': rooms})


@login_required
def show_room(request, pk):
	room = get_object_or_404(Room, pk=pk)
	if request.method == 'POST':
		url_form = NewRoomForm(request.POST)
		if url_form.is_valid():
			room.name = url_form.cleaned_data['name']
			room.video_url = url_form.cleaned_data['video_url']
			room.save()
	url_form = NewRoomForm(instance=room)
	comment_form = NewCommentForm()
	return render(request, 'room.html', {'room': room, 'url_form': url_form, 'comment_form': comment_form})


@login_required
def new_room(request):
	user = request.user
	if request.method == 'POST':
		form = NewRoomForm(request.POST)
		if form.is_valid():
			room = form.save(commit=False)
			room.owner = user
			room.save()
			return redirect('show_room', pk=room.pk)  # TODO: redirect to the created topic page
	else:
		form = NewRoomForm()
	return render(request, 'new_room.html', {'form': form})
