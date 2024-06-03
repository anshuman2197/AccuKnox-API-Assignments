from django.contrib import admin
from .models import *
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'username', 'is_staff', 'date_joined')

admin.site.register(CustomUser, CustomUserAdmin)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id','from_user', 'to_user', 'status', 'timestamp')

admin.site.register(FriendRequest, FriendRequestAdmin)