from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'age', 'institute', 'nationality')}),
        ('Academic info', {'fields': ('batch', 'student_id', 'university_field', 'phone')}),
        ('Profile', {'fields': ('profile_picture', 'bio', 'current_hsk_level')}),
        ('Progress', {'fields': ('learning_streak', 'last_activity_date', 'points', 'completed_lessons')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
