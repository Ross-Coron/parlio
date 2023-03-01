from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    bookmarkQuestion = models.ManyToManyField('Question', blank=True, related_name="bookmarkBy")
    watchlistQuestion = models.ManyToManyField('Question', blank=True, related_name="watchlistBy")

class Question(models.Model):
    uniqueId = models.IntegerField()