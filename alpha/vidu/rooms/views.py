from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Room, Comment
from .forms import NewRoomForm, NewCommentForm
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone


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


@login_required
def update_room(request):
	"""
	Ajax way to add new post
	"""
	if request.method != 'POST':
		raise Http404
	# TODO: check if request contains valid fields
	print(request.POST)
	room = get_object_or_404(Room, pk=request.POST['room_pk'])
	form = NewRoomForm(request.POST)
	if form.is_valid():
		room.name = form.cleaned_data['name']
		room.video_url = form.cleaned_data['video_url']
		room.save()
		response_text = convert_room_info_to_dict(room)
	else:
		response_text = {'failed': 'Post is invalid'}
	return HttpResponse(json.dumps(response_text), content_type='application/json')


def convert_room_info_to_dict(room):
	"""
	Convert from post object to json which contains created user info
	"""
	response_text = {
		'name': room.name,
		'video_url': room.video_url,
		'owner': room.owner.username,
		'owner_pk': room.owner.pk,
		'room_pk': room.pk
	}
	return response_text


@login_required
def post_comment(request):
	"""
	Ajax way to add new post
	"""
	if request.method != 'POST':
		raise Http404

	form = NewCommentForm(request.POST)
	post = form.save(commit=False)
	if form.is_valid():
		post.created_by = request.user
		post.save()
		response_text = convert_comment_to_dict(post)
	else:
		response_text = {'failed': 'Post is invalid'}
	return HttpResponse(json.dumps(response_text), content_type='application/json')


def convert_comment_to_dict(comment):
	"""
	Convert from post object to json which contains created user info
	"""
	response_text = {
		'message': comment.message,
		'created_by_pk': comment.created_by.profile.pk,
		'created_by': comment.created_by.username,
		'comment_pk': comment.pk,
		'created_at': timezone.localtime(comment.created_at).strftime("%Y-%m-%d %H:%M:%S"),
		'room_pk': comment.room.pk
	}
	return response_text
