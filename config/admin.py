# =================================================
# Importing modules and models
# =================================================
from django.contrib import admin
from .models import Habit, Completion


# =================================================
# Defining admin interface for Habit model
# =================================================
class HabitAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('name', 'goal', 'unit', 'user')
    # Fields to search in the admin search bar
    search_fields = ('name', 'user__username')


# =================================================
# Defining admin interface for Completion model
# =================================================
class CompletionAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('habit', 'added', 'completion_count')
    # Fields to filter by in the admin filter sidebar
    list_filter = ('habit', 'added')
    # Fields to search in the admin search bar
    search_fields = ('habit__name',)


# =================================================
# Registering models with the admin site
# =================================================
admin.site.register(Habit, HabitAdmin)
admin.site.register(Completion, CompletionAdmin)