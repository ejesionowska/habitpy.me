# =================================================
# Importing necessary Django model modules
# =================================================
from django.db import models
from django.contrib.auth.models import User


# =================================================
# Habit model to store user habits
# =================================================
class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the user who owns the habit
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
        return self.name  # String representation of the habit


# =================================================
# Completion model to store habit completions
# =================================================
class Completion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)  # Reference to the habit being completed
    added = models.DateField()  # Date when the completion was added
    completion_count = models.PositiveIntegerField(default=0)  # Number of completions

    def __str__(self):
        return f"{self.habit.name} - {self.added}"


# =================================================
# City model to store city information
# =================================================
#class City(models.Model):
  #  name = models.CharField(max_length=100)
  #  country = models.CharField(max_length=100)

   # def __str__(self):
    #    return f"{self.name}, {self.country}"