from django.shortcuts import render,redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .form import RoomForm


# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn Python', 'description': 'This is a room for learning Python', 'members': 3},
#     {'id': 2, 'name': 'Lets learn Django', 'description': 'This is a room for learning Django', 'members': 2},
#     {'id': 3, 'name': 'Lets learn React', 'description': 'This is a room for learning React', 'members': 1},
#     {'id': 4, 'name': 'Lets learn Vue', 'description': 'This is a room for learning Vue', 'members': 1}
# ]

def loginPage(request):
    
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
        
        # authenticate is a function that takes in the request, username and password and 
        # returns the user object if the user exists and the password is correct
        user = authenticate(request, username=username, password=password)    
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is incorrect')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # commit=False means that we are not saving the user to the database yet
            user.username = user.username.lower()
            user.save()
            # login the user after registration
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occured during registration')
    return render(request, 'base/login_register.html', {'form':form})

def home(request):
    # object is a manager that allows us to query the database for all the rooms. 
    # It have other methods like filter, get, create, etc.
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q) |
                                Q(name__icontains = q) |
                                Q(description__icontains = q)
                                )
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    context = {'rooms': rooms,'topics':topics, 'room_count':room_count}
    print(context)
    return render (request, 'base/home.html', context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    
    # messages is a manager that allows us to query the database for all the messages.
    # for many to one relationship, we can access the messages of a room by using room.message_set
    room_messages = room.message_set.all().order_by('-created') 
    
    # for many to many relationship, we can access the participants of a room by using room.participants.all()
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        # add is a method that allows us to add a user to a many to many relationship
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render (request, 'base/room.html', context)

# login_required is a decorator that will redirect the user to the login page if the user is not logged in
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
       form = RoomForm(request.POST)
       if form.is_valid():
           form.save()
           redirect('home')
    context = {'form': form}
    return render (request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    #intial is a dictionary that contains the initial values for the form   
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        #here instance = room is telling the form that we are updating the room object
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form':form}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})