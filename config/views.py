#views.py

import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Habit, Completion
from .forms import HabitForm, CompletionForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, LoginForm
from django.utils.dateformat import DateFormat
from django.http import JsonResponse
from .models import City
from datetime import date

def home(request):
    return render(request, 'home.html')

@login_required
def habit_list(request):
    user = request.user
    habits = Habit.objects.filter(user=user)

    if request.method == 'POST':
        if 'add_habit' in request.POST:
            if habits.count() < 6:
                form = HabitForm(request.POST)
                if form.is_valid():
                    habit = form.save(commit=False)
                    habit.user = user
                    habit.save()
                    return redirect('habit_list')
            else:
                return render(request, 'habits.html', {'habits': habits, 'message': "You're already working on the maximum number of habits."})
        elif 'edit_habit' in request.POST:
            habit_id = request.POST.get('habit_id')
            habit = Habit.objects.get(id=habit_id)
            form = HabitForm(request.POST, instance=habit)
            if form.is_valid():
                form.save()
                return redirect('habit_list')
        elif 'delete_habit' in request.POST:
            habit_id = request.POST.get('habit_id')
            Habit.objects.get(id=habit_id).delete()
            return redirect('habit_list')

    form = HabitForm()
    return render(request, 'habits.html', {'habits': habits, 'form': form})

@login_required
def dashboard(request):
    user = request.user
    habits = Habit.objects.filter(user=user)
    selected_habit = habits.first() if habits.exists() else None
    selected_date = datetime.now().date()
    selected_month = selected_date.strftime('%Y-%m')
    completions = []

    if request.method == 'POST':
        if 'selected_date' in request.POST and request.POST.get('selected_date'):
            selected_date_str = request.POST.get('selected_date')
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = datetime.now().date()
        if 'selected_month' in request.POST and request.POST.get('selected_month'):
            selected_month = request.POST.get('selected_month')
        if 'habit_id' in request.POST and request.POST.get('habit_id'):
            habit_id = request.POST.get('habit_id')
            try:
                selected_habit = Habit.objects.get(id=habit_id, user=user)
            except Habit.DoesNotExist:
                selected_habit = None

        if 'completion_count' in request.POST and selected_habit and selected_date:
            try:
                completion_count = int(request.POST.get('completion_count', 0))
            except ValueError:
                completion_count = 0
            Completion.objects.update_or_create(
                habit=selected_habit, added=selected_date,
                defaults={'completion_count': completion_count}
            )

    if selected_habit:
        selected_month_date = datetime.strptime(selected_month, '%Y-%m').date()
        completions_qs = Completion.objects.filter(
            habit=selected_habit,
            added__year=selected_month_date.year,
            added__month=selected_month_date.month
        )
        completions_dict = {completion.added.day: completion.completion_count for completion in completions_qs}
        days_in_month = (selected_month_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        completions = [{'day': day, 'count': completions_dict.get(day, 0)} for day in range(1, days_in_month.day + 1)]

    selected_date_formatted = DateFormat(selected_date).format('F j, Y')
    completion_form = CompletionForm(initial={'habit': selected_habit})

    context = {
        'habits': habits,
        'selected_habit': selected_habit,
        'selected_date': selected_date,
        'selected_date_formatted': selected_date_formatted,
        'selected_month': selected_month,
        'completions': completions,
        'completion_form': completion_form,
    }

    return render(request, 'dashboard.html', context)



def export_csv(request):
    user = request.user
    habits = Habit.objects.filter(user=user)
    completions = Completion.objects.filter(habit__user=user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="habits.csv"'

    writer = csv.writer(response)
    writer.writerow(['Habit', 'Date', 'Completion Count'])

    for completion in completions:
        writer.writerow([completion.habit.name, completion.added, completion.completion_count])

    return response

def export_pdf(request):
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="habits.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40
    p.drawString(100, y, "Habit Tracker Data")
    y -= 40

    user = request.user
    habits = Habit.objects.filter(user=user)
    completions = Completion.objects.filter(habit__user=user)

    for completion in completions:
        habit_info = f"Habit: {completion.habit.name}, Date: {completion.added}, Completion Count: {completion.completion_count}"
        p.drawString(30, y, habit_info)
        y -= 20
        if y < 40:
            p.showPage()
            y = height - 40

    p.save()
    return response

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

cities = ["Warszawa", "Kraków", "Łódź", "Wrocław", "Poznań", "Gdańsk", "Szczecin", "Bydgoszcz", "Lublin", "Białystok", "Rzeszów", "Kalisz", "Katowice"]

def autocomplete(request):
    if 'term' in request.GET:
        qs = cities
        q = request.GET.get('term')
        qs = [city for city in cities if city.lower().startswith(q.lower())]
        return JsonResponse(qs, safe=False)
    return JsonResponse([], safe=False)

def home(request):
    return render(request, 'home.html')
