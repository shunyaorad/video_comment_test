from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Room, Comment, Profile, Invitation
from .forms import NewRoomForm, NewCommentForm, InvitationForm
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from dateutil import parser
import pytz
from datetime import timedelta


@login_required
def home(request):
	rooms = request.user.profile.visible_rooms.all()
	return render(request, 'home.html', {'rooms': rooms})


@login_required
def show_room(request, pk):
	room = get_object_or_404(Room, pk=pk)
	url_form = NewRoomForm(instance=room)
	comment_form = NewCommentForm()
	invitation_form = InvitationForm()
	return render(request, 'room.html', {
		'room': room,
		'url_form': url_form,
		'comment_form': comment_form,
		'invitation_form': invitation_form
	})


@login_required
def new_room(request):
	user = request.user
	profile = user.profile
	if request.method == 'POST':
		form = NewRoomForm(request.POST)
		if form.is_valid():
			room = form.save(commit=False)
			room.owner = user
			room.save()
			profile.visible_rooms.add(room)
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
		'room_pk': room.pk
	}
	return response_text


@login_required
def invite(request):
	# TODO: Check if request.POST contains all fields needed
	invitation_form = InvitationForm(request.POST)
	if invitation_form.is_valid():
		room = get_object_or_404(Room, pk=request.POST['room_pk'])
		invited_profile = Profile.objects.filter(username=invitation_form.cleaned_data['username'])[0]
		# create invitation only if the user does not contain this room in his visible rooms
		if not invited_profile.visible_rooms.filter(pk=room.pk).exists() and \
				not Invitation.objects.filter(room=room, invited_profile=invited_profile).exists():
			invitation = Invitation(room=room, invited_profile=invited_profile)
			invitation.save()
		response_text = {"invited_username": invited_profile.username}
	else:
		response_text = {"invited_username": None}
	return HttpResponse(json.dumps(response_text), content_type='application/json')


@login_required
def respond(request):
	# TODO: Check if request.POST contains all fields needed
	profile = request.user.profile
	response = request.POST['response']
	room = get_object_or_404(Room, pk=request.POST['room_pk'])
	if response.lower() == 'accept':
		profile.visible_rooms.add(room)
		response_text = {'response': 'accept'}
	else:
		response_text = {'response': 'decline'}
	Invitation.objects.filter(room=room,
	                          invited_profile=profile).delete()  # TODO: check if there is better way to filter

	return HttpResponse(json.dumps(response_text), content_type='application/json')


@login_required
def post_comment(request):
	"""
	Ajax way to add new post
	"""
	if request.method != 'POST':
		raise Http404
	# TODO: check if request contains valid fields
	print(request.POST)
	form = NewCommentForm(request.POST)
	if form.is_valid():
		print("form is valid")
		comment = form.save(commit=False)
		comment.created_by = request.user
		print("Comment: " + comment.message)
		comment.room = get_object_or_404(Room, pk=request.POST['room_pk'])
		comment.time_stamp = request.POST['time_stamp']
		comment.save()
		response_text = convert_comment_to_dict(comment)
	else:
		print("Invalid form")
		response_text = {'failed': 'Post is invalid'}
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


@login_required
def get_invitations(request):
	"""
	Ajax way to get new comments from database
	:param request:
	:return:
	"""
	# TODO: check valid request.POST
	profile = request.user.profile
	if 'last_update_time' in request.GET and not request.GET['last_update_time'] == '0':
		last_update_time = parser.parse(request.GET['last_update_time'])
		last_update_time = pytz.timezone('US/Eastern').localize(last_update_time)
		# TODO: fix this time hack
		last_update_time += timedelta(0, 1)
		new_invitations = Invitation.objects.filter(
			invited_profile=profile, created_at__gt=last_update_time
		).order_by('created_at')
	else:
		new_invitations = Invitation.objects.filter(invited_profile=profile).order_by('created_at')
	response_text = []
	for invitation in new_invitations:
		parsed_invitation = convert_invitation_to_dict(invitation)
		response_text.append(parsed_invitation)
	return HttpResponse(json.dumps(response_text), content_type='application/json')


def convert_invitation_to_dict(invitation):
	"""
	Convert from post object to json which contains created user info
	"""
	response_text = {
		'name': invitation.room.name,
		'room_pk': invitation.room.pk,
		'owner': invitation.room.owner.username,
		'owner_pk': invitation.room.owner.pk,
		'video_url': invitation.room.video_url,
		'created_at': timezone.localtime(invitation.created_at).strftime("%m/%d/%Y %H:%M:%S")
	}
	return response_text
