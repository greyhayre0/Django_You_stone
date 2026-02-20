from django.urls import path
from . import views

urlpatterns = [
    path("", views.VideoListView.as_view(), name="video-list"),
    path("ids/", views.VideoIdsView.as_view(), name="video-ids"),
    path("statistics-subquery/", views.StatisticsSubqueryView.as_view(), name="stats-subquery"),
    path("statistics-group-by/", views.StatisticsGroupByView.as_view(), name="stats-group-by"),

    path("<int:pk>/", views.VideoDetailView.as_view(), name="video-detail"),
    path("<int:video_id>/likes/", views.VideoLikesView.as_view(), name="video-likes"),

]
