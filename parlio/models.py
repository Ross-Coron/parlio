from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    bookmarkQuestion = models.ManyToManyField('Question', blank=True, related_name="bookmarkBy")
    watchlistQuestion = models.ManyToManyField('Question', blank=True, related_name="watchlistBy")

class Question(models.Model):
    uniqueId = models.IntegerField()

    def __str__(self):
        return f"{self.uniqueId}"

class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)