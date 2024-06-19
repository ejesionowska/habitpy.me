
from django.contrib import admin
from .models import Habit, Completion

class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal', 'unit', 'user')
    search_fields = ('name', 'user__username')

class CompletionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'added', 'completion_count')
    list_filter = ('habit', 'added')
    search_fields = ('habit__name',)

admin.site.register(Habit, HabitAdmin)
admin.site.register(Completion, CompletionAdmin)
