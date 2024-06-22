
from django.db import models
from django.contrib.auth.models import User

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    goal = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, choices=[
        ('seconds', 'Seconds'),
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('repetitions', 'Repetitions'),
        ('steps', 'Steps'),
        ('meters', 'Meters'),
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles'),
        ('other', 'Other')

    ])

    def __str__(self):
        return self.name

class Completion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    added = models.DateField()
    completion_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.habit.name} - {self.added}"


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.country}"