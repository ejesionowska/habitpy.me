from django import forms
from .models import Habit

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




