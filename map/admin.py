from django.contrib import admin
from .models import Site, DataPoint, Comment, UserMark

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    list_display = ['site', 'year', 'lat', 'lng', 'ndvi']
    list_filter = ['site', 'year']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'site', 'year', 'created_at', 'text']
    list_filter = ['site', 'year']

@admin.register(UserMark)
class UserMarkAdmin(admin.ModelAdmin):
    list_display = ['label', 'site', 'lat', 'lng', 'created_at']
