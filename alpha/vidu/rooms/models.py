# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator


class Room(models.Model):
	name = models.CharField(max_length=30)
	video_url = models.CharField(max_length=100)
	owner = models.ForeignKey(User, related_name='rooms', on_delete=models.CASCADE)
	last_commented = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "Owner: " + self.owner.username + " Name: " + str(self.name) + " URL: " + str(self.video_url)


class Comment(models.Model):
	message = models.TextField(max_length=500)
	room = models.ForeignKey(Room, related_name='comments', on_delete=models.CASCADE)
	created_by = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)  # TODO: change to appropriate field
	time_stamp = models.TextField(max_length=400)

	def __str__(self):
		truncated_message = Truncator(self.message)
		return truncated_message.chars(30) + " TS: " + str(self.time_stamp)


class Profile(models.Model):
	profile_photo = models.FileField(upload_to="images", null=True, blank=True)
	content_type = models.CharField(max_length=50, null=True, blank=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	last_name = models.CharField(max_length=20)
	first_name = models.CharField(max_length=20)
	username = models.CharField(max_length=20)
	email = models.CharField(blank=True, max_length=32)
	update_time = models.DateTimeField(null=True)

	def __unicode__(self):
		return 'Entry(id=' + str(self.id) + ')'

	def __str__(self):
		return "Username: " + self.username + ", " + "email: " + self.email
