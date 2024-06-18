import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Habit
from .models import Completion
from .forms import HabitForm
from django.contrib.auth.decorators import login_required
from datetime import datetime


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
                return render(request, 'habits.html', {'habits': habits, 'message': 'Pracujesz już nad maksymalną ilością nawyków.'})
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
    completions = Completion.objects.filter(habit__user=user, added=selected_date)

    if request.method == 'POST':
        selected_date = datetime.strptime(request.POST.get('selected_date'), '%Y-%m-%d').date()
        habit_id = request.POST.get('habit_id')
        selected_habit = Habit.objects.get(id=habit_id)
        completions = Completion.objects.filter(habit=selected_habit, added__month=selected_date.month,
                                                added__year=selected_date.year)

    context = {
        'habits': habits,
        'selected_habit': selected_habit,
        'selected_date': selected_date,
        'completions': completions,
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
    # Import necessary libraries
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