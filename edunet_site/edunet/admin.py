'''
File used to diplay the model in the admin side of the site.
'''
from django.contrib import admin

from .models import Department, Course, TreeOfKnowledge

class DepartmentAdmin(admin.ModelAdmin):
    '''Class to define how the admin displays the Department model.'''
    ordering = ['department_name']
    fieldsets = [
        (None, {'fields': ['department_name']}),
        (None, {'fields': ['department_abbreviation']}),
        (None, {'fields': ['department_slug']}),
    ]
    list_display = ('department_name', 'department_abbreviation', 'department_slug')
    search_fields = ['department_name', 'department_abbreviation']
    prepopulated_fields = {'department_slug': ('department_name',)}

class ChoiceInLine(admin.TabularInline):
    '''Class to define how the Tree of Knowledge is displayed with reference to its course.'''
    model = TreeOfKnowledge
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    '''Class to define how the admin displays the Course model.'''
    ordering = ['course_name']
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
