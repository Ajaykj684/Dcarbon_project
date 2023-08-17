from django.db import models


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    

class Destination(models.Model):
    stops = models.JSONField()
    total_distance = models.CharField(max_length=100, null=True, blank=True)
   