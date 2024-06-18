from django import forms
from .models import Habit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'goal', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'maxlength': 10}),
            'goal': forms.NumberInput(attrs={'max': 999999}),
            'unit': forms.Select(choices=[
                ('sekundy', 'Sekundy'),
                ('minuty', 'Minuty'),
                ('godziny', 'Godziny'),
                ('powtórzenia', 'Powtórzenia'),
                ('metry', 'Metry'),
                ('kilometry', 'Kilometry'),
                ('mile', 'Mile'),
                ('inne', 'Inne')
            ])
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
    password = forms.CharField(widget=forms.PasswordInput)

