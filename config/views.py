# ==============================================================
# Importing necessary modules and functions
# ==============================================================
import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Habit, Completion
from .forms import HabitForm, CompletionForm
from datetime import datetime, date, timedelta
from django.contrib.auth import login, logout
from .forms import SignUpForm, LoginForm
from django.utils.dateformat import DateFormat
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import AuthenticationForm
from config.auth_backends import EmailOrUsernameModelBackend
from django.contrib import messages



# ==============================================================
# Home view
# ==============================================================
def home(request):
    return render(request, 'home.html')


# ==============================================================
# Habit list view - displays, adds, edits and deletes habits
# ==============================================================
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
                messages.error(request, "You're already working on the maximum number of habits.")
            return redirect('habit_list')

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


# ==============================================================
# Dashboard view - displays habit completions
# ==============================================================
@login_required
def dashboard(request):
    user = request.user
    habits = Habit.objects.filter(user=user)
    selected_habit = habits.first() if habits.exists() else None
    selected_date = date.today()
    selected_month = selected_date.strftime('%Y-%m')
    completions = []

    if request.method == 'POST':
        if request.POST.get('selected_date'):
            selected_date = datetime.strptime(request.POST.get('selected_date'), '%Y-%m-%d').date()
        if request.POST.get('selected_month'):
            selected_month = request.POST.get('selected_month')
        habit_id = request.POST.get('habit_id')
        if habit_id:
            try:
                selected_habit = Habit.objects.get(id=habit_id, user=user)
            except Habit.DoesNotExist:
                selected_habit = None

        if 'completion_count' in request.POST and selected_habit and selected_date:
            try:
                completion_count = int(request.POST.get('completion_count', 0))
            except ValueError:
                completion_count = 0
            completion, created = Completion.objects.update_or_create(
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
    # return redirect('dashboard', selected_habit_id=selected_habit.id, selected_date=selected_date.strftime('%Y-%m-%d'),
    #                selected_month=selected_month)
    return render(request, 'dashboard.html', context)


# ==============================================================
# Export habits data to CSV
# ==============================================================
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


# ==============================================================
# Export habits data to PDF
# ==============================================================
def export_pdf(request):

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


# ==============================================================
# User sign-up view
# ==============================================================
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


# ==============================================================
# User login view
# ==============================================================
#def login_view(request):
#    if request.method == 'POST':
 #       form = LoginForm(data=request.POST)
 #       if form.is_valid():
  #          user = form.get_user()
  #          login(request, user)
  #          return redirect('dashboard')
  #  else:
  #      form = LoginForm()
  #  return render(request, 'login.html', {'form': form})


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = EmailOrUsernameModelBackend().authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='config.auth_backends.EmailOrUsernameModelBackend')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid login credentials')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# ==============================================================
# User logout view
# ==============================================================
def logout_view(request):
    logout(request)
    return redirect('home')


# ==============================================================
# Change password view
# ==============================================================
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change-password.html', {'form': form})