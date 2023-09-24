from django.shortcuts import render,redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .form import RoomForm, UserForm


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
    
    topics = Topic.objects.all()[0:5]
    rooms_count = rooms.count()
    
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    
    context = {'rooms': rooms,'topics':topics, 'rooms_count':rooms_count, 'room_messages':room_messages}
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

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    
    # room_set allows us to access the rooms of a user
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    
    context = {'user': user, 'rooms': rooms,'room_messages':room_messages, 'topics':topics}
    return render (request, 'base/profile.html', context)

# login_required is a decorator that will redirect the user to the login page if the user is not logged in
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics':topics}
    return render (request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    #intial is a dictionary that contains the initial values for the form   
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        #here instance = room is telling the form that we are updating the room object
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    
    context = {'form':form, 'topics':topics,'room':room}
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


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains = q)
    return render(request, 'base/topics.html', {'topics':topics})

def activityPage(request):
    rooms = Room.objects.all()
    return render(request, 'base/activity.html', {"rooms":rooms})