from django.forms import ModelForm
from .models import Room, User

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['topic', 'name', 'description']
        

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']