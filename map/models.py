from django.db import models
from django.contrib.auth.models import User


class Site(models.Model):
    id = models.CharField(max_length=32, primary_key=True)  # 'wilmington', 'chisinau', 'lozova'
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name


class DataPoint(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='points')
    year = models.IntegerField()
    lat = models.FloatField()
    lng = models.FloatField()
    ndvi = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['site', 'year']),
        ]

    def __str__(self):
        return f'{self.site_id} {self.year} ({self.lat},{self.lng})'


class Comment(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='comments')
    year = models.IntegerField()
    author = models.CharField(max_length=128)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} on {self.site_id}/{self.year}'


class UserMark(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='marks')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=64, blank=True)  # fallback for anonymous
    lat = models.FloatField()
    lng = models.FloatField()
    label = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.label} ({self.site_id})'


class BugReport(models.Model):
    text = models.TextField()
    contact = models.CharField(max_length=256, blank=True)
    site = models.CharField(max_length=64, blank=True)
    url = models.URLField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.site}] {self.text[:60]}'

class Pledge(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pledges')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=128)
    action = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.action[:40]}'
