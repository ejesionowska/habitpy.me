# =========================================================
# Importing necessary Django form modules
# =========================================================
from django import forms
from .models import Habit, Completion
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


# =========================================================
# Form for creating and updating Habit instances
# =========================================================
class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'goal', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'maxlength': 10}),
            'goal': forms.NumberInput(attrs={'max': 999999}),
            'unit': forms.Select(choices=[
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
        }


# =========================================================
# Form for creating and updating Completion instances
# =========================================================
class CompletionForm(forms.ModelForm):
    class Meta:
        model = Completion
        fields = ['habit', 'completion_count']


# =========================================================
# Form for user sign-up
# =========================================================
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


# =========================================================
# Form for user login
# =========================================================
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
    password = forms.CharField(widget=forms.PasswordInput)