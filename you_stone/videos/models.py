from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Video(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="Владелец"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    is_published = models.BooleanField(default=False, verbose_name="Опубликованно")
    total_likes = models.PositiveIntegerField(default=0, verbose_name="Всего лайков")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return F"{self.name} by {self.owner.username}"
    
    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published", "created_at"]),
            models.Index(fields=["owner", "is_published"])
        ]


class VideoFile(models.Model):
    class Quality(models.TextChoices):
        HD = "HD", "HD (720p)"
        FHD = "FHD", "FHD (1080p)"
        UHD = "UHD", "UHD (4K)"
    
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Видео"
    )
    file = models.FileField(upload_to='videos/', verbose_name="Видео файл")
    quality = models.CharField(
        max_length=3,
        choices=Quality.choices,
        verbose_name="Качество"
    )
    def __str__(self):
        return f"{self.video.name} - {self.get_quality_display()}"
    
    class Meta:
        verbose_name = "Видео файл"
        verbose_name_plural = "Видео файлы"
        unique_together = ["video", "quality"]

class Like(models.Model):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Видео"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата лайка")

    def __str__(self):
        return f"{self.user.username} liked {self.video.name}"
    
    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        constraints = [
            models.UniqueConstraint(
                fields=["video", "user"],
                name="unique_video_user_like"
            )
        ]
        indexes = [models.Index(fields=["video", "user"])]
