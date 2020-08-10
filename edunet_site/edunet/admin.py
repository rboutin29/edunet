from django.contrib import admin

from .models import Department, Course, TreeOfKnowledge

class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['department_name']}),
        (None, {'fields': ['department_slug']}),
    ]
    list_display = ('department_name', 'department_slug')
    search_fields = ['department_name']
    prepopulated_fields = {'department_slug': ('department_name',)}

class ChoiceInLine(admin.TabularInline):
    model = TreeOfKnowledge
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Title', {'fields': ['course_name']}),
        ('About', {'fields': ['course_number', 'course_season', 'course_url', 'course_description', 'course_slug']}), # pylint: disable=line-too-long
    ]
    inlines = [ChoiceInLine]
    list_display = (
        'course_name',
        'course_number',
        'course_season',
        'course_url',
        'course_description',
        'course_slug',
    )
    search_fields = ['course_name', 'course_number', 'course_season']
    prepopulated_fields = {'course_slug': ('course_name',)}

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
