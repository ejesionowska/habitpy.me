from django.db import models
from django.contrib.auth.models import User

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    goal = models.IntegerField()
    unit = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Completion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    completion_count = models.IntegerField()
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit.name} - {self.completion_count}"
