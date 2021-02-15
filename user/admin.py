from .models import User
from django.contrib import admin
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'created_at']


admin.site.register(User)
