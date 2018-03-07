from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.signing import BadSignature
from .models import Room, Comment, Connection
from django.contrib.auth.models import User
from .forms import NewRoomForm, NewCommentForm, InvitationForm
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from dateutil import parser
import pytz
from datetime import timedelta


@login_required
def home(request):
	return render(request, 'home.html')


@login_required
def show_room(request, pk):
	room = get_object_or_404(Room, pk=pk)
	user = request.user
	connection_set = user.connections.filter(room=room)
	if len(connection_set) == 0 or connection_set.first().visible is False:
		raise Http404
	url_form = NewRoomForm(instance=room)
	comment_form = NewCommentForm()
	invitation_form = InvitationForm()
	shareable_link = "http://localhost:8000" + room.get_absolute_url()
	return render(request, 'room.html', {
		'room': room,
		'url_form': url_form,
		'comment_form': comment_form,
		'invitation_form': invitation_form,
		'shareable_link': shareable_link
	})


def show_shared_room(request, signed_pk):
	try:
		pk = Room.signer.unsign(signed_pk)
		room = Room.objects.get(pk=pk)
		url_form = NewRoomForm(instance=room)
		comment_form = NewCommentForm()
		invitation_form = InvitationForm()
		return render(request, 'room.html', {
			'room': room,
			'url_form': url_form,
			'comment_form': comment_form,
			'invitation_form': invitation_form
		})
	except (BadSignature, Room.DoesNotExist):
		raise Http404('No Order matches the given query.')


@login_required
def new_room(request):
	user = request.user
	if request.method == 'POST':
		form = NewRoomForm(request.POST)
		if form.is_valid():
			room = form.save(commit=False)
			room.owner = user
			room.save()
			connection = Connection(room=room, user=user, visible=True)
			connection.save()
			return redirect('show_room', pk=room.pk)
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
		'room_pk': room.pk,
		'created_at': timezone.localtime(room.created_at).strftime("%m/%d/%Y %H:%M:%S"),
	}
	return response_text


@login_required
def invite(request):
	# TODO: Check if request.POST contains all fields needed
	invitation_form = InvitationForm(request.POST)
	if invitation_form.is_valid():
		room = get_object_or_404(Room, pk=request.POST['room_pk'])
		invited_user = User.objects.filter(username=invitation_form.cleaned_data['username']).first()
		# create invitation only if the user does not contain this room in his visible rooms
		if not invited_user.connections.filter(room=room).exists():
			connection = Connection(room=room, user=invited_user, visible=False)
			connection.save()
		response_text = {"invited_username": invited_user.username}
	else:
		response_text = {"invited_username": None}
	return HttpResponse(json.dumps(response_text), content_type='application/json')


@login_required
def get_connections(request):
	"""
	Ajax way to get new rooms from database
	:param request:
	:return:
	"""
	# TODO: check valid request.POST
	user = request.user
	if 'last_connection_update_time' in request.GET and not request.GET['last_connection_update_time'] == '0':
		last_update_time = parser.parse(request.GET['last_connection_update_time'])
		last_update_time = pytz.timezone('US/Eastern').localize(last_update_time)
		# TODO: fix this time hack
		last_update_time += timedelta(0, 1)
		new_connections = user.connections.filter(created_at__gt=last_update_time).order_by(
			'created_at')
	else:
		new_connections = user.connections.order_by('created_at')
	response_text = []
	for connection in new_connections:
		parsed_room = convert_connection_to_room_dict(connection)
		response_text.append(parsed_room)
	return HttpResponse(json.dumps(response_text), content_type='application/json')


def convert_connection_to_room_dict(connection):
	"""
	Convert from post object to json which contains created user info
	"""
	response_text = convert_room_info_to_dict(connection.room)
	response_text['visible'] = connection.visible
	response_text['created_at'] = timezone.localtime(connection.created_at).strftime("%m/%d/%Y %H:%M:%S")

	return response_text


@login_required
def respond(request):
	# TODO: Check if request.POST contains all fields needed
	user = request.user
	response = request.POST['response']
	room = get_object_or_404(Room, pk=request.POST['room_pk'])
	connection = user.connections.filter(room=room).first()
	if response.lower() == 'accept':
		print("accepted!")
		connection.visible = True
		connection.created_at = timezone.now()
		connection.save()
		response_text = {'response': 'accept'}
	else:
		connection.delete()
		response_text = {'response': 'decline'}

	return HttpResponse(json.dumps(response_text), content_type='application/json')


@login_required
def delete_room(request):
	# TODO: Check if request.POST contains all fields needed
	user = request.user
	room = get_object_or_404(Room, pk=request.POST['room_pk'])
	if room.owner == user:  # if the owner of the room deletes, delete the room
		room.delete()
		response_text = {'response': 'deleted room from database'}
	else:  # if not the owner of the room, delete the connection to the room
		user.connections.filter(room=room).first().delete()
		response_text = {'response': 'deleted from visible_rooms'}

	return HttpResponse(json.dumps(response_text), content_type='application/json')


@login_required
def post_comment(request):
	"""
	Ajax way to add new post
	"""
	if request.method != 'POST':
		raise Http404
	# TODO: check if request contains valid fields
	form = NewCommentForm(request.POST)
	if form.is_valid():
		comment = form.save(commit=False)
		comment.created_by = request.user
		comment.room = get_object_or_404(Room, pk=request.POST['room_pk'])
		comment.time_stamp = request.POST['time_stamp']
		comment.save()
		response_text = convert_comment_to_dict(comment)
	else:
		response_text = {'failed': 'Post is invalid'}
	return HttpResponse(json.dumps(response_text), content_type='application/json')


@login_required
def get_comment(request):
	"""
	Ajax way to get new comments from database
	:param request:
	:return:
	"""
	if 'roomPK' not in request.GET:
		return HttpResponse(json.dumps({}), content_type='application/json')
	room = get_object_or_404(Room, pk=request.GET['roomPK'])
	if 'last_comment_update_time' in request.GET and not request.GET['last_comment_update_time'] == '0':
		last_update_time = parser.parse(request.GET['last_comment_update_time'])
		last_update_time = pytz.timezone('US/Eastern').localize(last_update_time)
		# TODO: fix this time hack
		last_update_time += timedelta(0, 1)
		new_comments = Comment.objects.filter(room=room, created_at__gt=last_update_time)
	else:
		new_comments = Comment.objects.filter(room=room)
	response_text = []
	for comment in new_comments:
		parsed_comment = convert_comment_to_dict(comment)
		response_text.append(parsed_comment)
	return HttpResponse(json.dumps(response_text), content_type='application/json')


def convert_comment_to_dict(comment):
	"""
	Convert from post object to json which contains created user info
	"""
	response_text = {
		'message': comment.message,
		'time_stamp': comment.time_stamp,
		'created_by_pk': comment.created_by.pk,
		'created_by': comment.created_by.username,
		'comment_pk': comment.pk,
		'created_at': timezone.localtime(comment.created_at).strftime("%m/%d/%Y %H:%M:%S"),
		'room_pk': comment.room.pk
	}
	return response_text
