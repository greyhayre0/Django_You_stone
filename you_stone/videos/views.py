from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Sum, Count, Subquery, OuterRef
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Video, Like
from .serializers import VideoSerializer, VideoFileSerializer, LikesSerializer, VideoIdsSerializer
from django.db import transaction


class VideoListView(generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Video.objects.select_related("owner").prefetch_related("files")
        if user.is_staff:
            return queryset.all()
        elif user.is_authenticated:
            return queryset.filter(is_published=True) | queryset.filter(owner=user)
        else:
            return queryset.filter(is_published=True)

class VideoDetailView(generics.RetrieveAPIView):
    serializer_class = VideoSerializer
    def get_queryset(self):
        user = self.request.user
        queryset = Video.objects.select_related("owner").prefetch_related("files")
        if user.is_staff:
            return queryset.all()
        elif user.is_authenticated:
            return queryset.filter(is_published=True) | queryset.filter(owner=user)
        else:
            return queryset.filter(is_published=True)
        
class VideoIdsView(generics.ListAPIView):
    """Список ID всех опубликованных видео (только для staff)"""
    serializer_class = VideoIdsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return Video.objects.none()
        return Video.objects.filter(is_published=True).only('id')


class VideoLikesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        with transaction.atomic():
            video = Video.objects.select_for_update().get(id=video_id)
            like, created = Like.objects.get_or_create(video=video, user=request.user)
            if created:
                video.total_likes += 1
                video.save()
                return Response({"status":"liked"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":"Already liked"}, status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request, video_id):
        video = get_object_or_404(Video, id = video_id, is_published=True)
        with transaction.atomic():
            video = Video.objects.select_for_update().get(id=video_id)
            like = Like.objects.filter(video=video, user=request.user).first()
            if like:
                like.delete()
                video.total_likes -= 1
                video.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error":"Like not found"}, status=status.HTTP_404_NOT_FOUND)


class StatisticsSubqueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"error":"Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        likes_subquery = Video.objects.filter(
            owner = OuterRef("pk"),
            is_published = True
        ).values("owner").annotate(likes_sum=Sum("total_likes")).values("likes_sum")
        user = User.objects.annotate(
            likes_sum = Subquery(likes_subquery)
            ).exclude(likes_sum__isnull=True).order_by("-likes_sum")
        serializer = LikesSerializer(user, many = True)
        return Response(serializer.data)
    
class StatisticsGroupByView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({"error":"Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        stats = Video.objects.filter(
            is_published = True
        ).values("owner__username").annotate(likes_sum=Sum("total_likes")).order_by("-likes_sum")
        
        data = [
            {"username": item["owner__username"], "likes_sum":item["likes_sum"]}
            for item in stats
        ]
        return Response(data) 