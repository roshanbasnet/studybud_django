from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message, User

#To register the model with the admin site, we need to import the model and call
# admin.site.register() with the model class as the argument.
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(User) 