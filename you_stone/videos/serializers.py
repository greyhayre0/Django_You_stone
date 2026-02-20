from rest_framework import serializers
from .models import Video, VideoFile, Like
from django.contrib.auth.models import User

class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ["id", "video", "file", "quality"]
        read_only_fields = ["id"]

class VideoSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source = "owner.username", read_only = True)
    files = VideoFileSerializer(many = True, read_only = True)

    class Meta:
        model = Video
        fields = ["id", "owner", "owner_username", "name", "is_published", "total_likes", "created_at","files"]
        read_only_fields = ["id", "owner", "total_likes", "created_at"]

class LikesSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    likes_sum = serializers.IntegerField()
    class Meta:
        fields = ["id","video", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class VideoIdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id']
