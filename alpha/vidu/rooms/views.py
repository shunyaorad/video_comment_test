from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Room


def home(request):
    rooms = Room.objects.all()
    return render(request, 'home.html', {'rooms': rooms})


def show_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'room.html', {'room': room})
