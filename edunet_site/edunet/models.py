'''
Contains the models neccesary to run the edunet website.

Models:
    Department
    Course
    Tree_of_Knowledge

'''
from django.db import models
from autoslug import AutoSlugField

class Department(models.Model):
    '''Class model used for the departments within the Yale website.'''
    department_name = models.CharField(max_length=50)
    department_slug = AutoSlugField(
        populate_from='department_name',
        unique=True, editable=True,
    )

    def __str__(self):
        return self.department_name

class Course(models.Model):
    '''Class model used for the courses within the Yale website.'''
    course_name = models.CharField(max_length=150)
    course_number = models.CharField(max_length=25)
    course_season = models.CharField(max_length=25, default='Course Season')
    course_url = models.URLField(max_length=150, default='Course URL')
    course_description = models.TextField(max_length=1000)
    course_slug = AutoSlugField(
        populate_from='course_name',
        unique=True,
        editable=True,
        max_length=150,
    )

    def __str__(self):
        return self.course_name

class TreeOfKnowledge(models.Model):
    '''Class model used for the Tree of Knowledges generested by the course_processor.'''
    course = models.ForeignKey(Course, default=1, on_delete=models.SET_DEFAULT) # pylint: disable=line-too-long
    transcript_num = models.IntegerField()
    tree_of_knowledge = models.TextField()

    def __str__(self):
        return self.tree_of_knowledge
