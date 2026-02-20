from django.contrib import admin
from .models import Video, VideoFile, Like


admin.site.register(Video)
admin.site.register(VideoFile)
admin.site.register(Like)