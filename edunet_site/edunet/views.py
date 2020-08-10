'''
Contains all the views for the edunet website.

CLASSES:
    IndexView(generic.TemplateView)
    SearchResultsView(generic.ListView)
    DepartmentListView(generic.ListView)
    SignUp(generic.CreateView)

FUNCTIONS:
    courseList(request, department_slug)
        returns rendering of a template
    course_detail(request, department_slug, course_slug)
        returns rendering of a template
    tk_form(request, department_slug, course_slug)
        returns rendering of a template
    tk_tree(request, department_slug, course_slug)
        returns rendering of a template

'''
from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from .utils import utils
from .forms import TKForm
from .models import Department, Course, TreeOfKnowledge

class SignUp(generic.CreateView):
    '''Class allows for a user to signup for EduNet.'''
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'edunet/signup.html'

class IndexView(generic.TemplateView):
    '''Class used to display the index page.'''
    template_name = 'edunet/index.html'

class SearchResultsView(generic.ListView): # pylint: disable=too-many-ancestors
    '''Class used to display the page that contains the search results.'''
    template_name = 'edunet/search_results.html'
    model = Course

    def get_queryset(self):
        '''Function takes itself and returns a filtered object list based on the users search.'''
        query = self.request.GET.get('search_query')
        object_list = Course.objects.filter(
            Q(course_name__icontains=query) | Q(course_number__icontains=query)
        )
        return object_list

class DepartmentListView(generic.ListView): # pylint: disable=too-many-ancestors
    '''Class used to display the list ov available departments.'''
    template_name = 'edunet/department.html'
    context_object_name = 'departments'
    model = Department
    slug_url_kwarg = 'department_slug' # slug to reference for URL (value after ':')
    slug_field = 'slug' # match slug used in model

    def get_context_data(self, **kwargs):
        '''Functions takes itself and kwargs and returns all available instances of itself.'''
        context = super().get_context_data(**kwargs)
        return context

def course_list(request, department_slug):
    '''Function used to display a list of courses based on a particular department.'''
    department_object = Department.objects.get(department_slug=department_slug)
    department_symbol = utils.get_department(department_slug)
    objects = Course.objects.filter(Q(course_number__icontains=department_symbol))

    request.session.set_test_cookie() # test cookies

    return render(
        request,
        'edunet/course_list.html',
        {'department': department_object, 'courses': objects},
    )

def course_detail(request, department_slug, course_slug):
    '''Function used to display a template that contains all the details of a course.'''
    department_object = Department.objects.get(department_slug=department_slug)
    course_object = Course.objects.get(course_slug=course_slug)

    # Filter out transcripts from other courses
    matching_courses = TreeOfKnowledge.objects.filter(course__course_name=course_object)
    transcript_numbers = [tree.transcript_num for tree in matching_courses]

    # Testing cookies
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        print('Cookie worked.')
    else:
        print('Cookie did not worked.')

    hit_count = HitCount.objects.get_for_object(course_object)
    hit_count_reponse = HitCountMixin.hit_count(request, hit_count)
    print(hit_count_reponse)

    context = {
        'transcript_numbers': transcript_numbers,
        'course': course_object,
        'department': department_object,
    }

    return render(request, 'edunet/course_detail.html', context)

@login_required
def tk_form(request, department_slug, course_slug):
    '''
    Function used to display a form for a specific course that allows the user to input desired
    constraints for the retrieval of a Tree of Knowledge for that course.
    '''
    department_object = Department.objects.get(department_slug=department_slug)
    course_object = Course.objects.get(course_slug=course_slug)
    error_message = ''
    if request.method == 'GET':
        form = TKForm(request.GET)
        if form.is_valid():
            kpp = form.cleaned_data['np'] # keywords per paragraph
            kpl = form.cleaned_data['nl'] # keywords per lecture
            transcript_num = form.cleaned_data['t'] # transcript number
            if utils.validate_transcript_num(transcript_num, course_object) is True:
                # get tree based on keywords and transcript
                tree = utils.retrieve_tree_of_knowledge(kpp, kpl, transcript_num, course_object)
                return tk_view(request, department_slug, course_slug, tree)
            transcript_total_num = utils.get_transcript_num(course_object)
            error_message = 'The transcript does not exist. There is only ' + str(transcript_total_num) + ' transcripts.' # pylint: disable=line-too-long
    form = TKForm()

    context = {
        'form': form,
        'course': course_object,
        'department': department_object,
        'error_message': error_message,
        }

    return render(request, 'edunet/tk_form.html', context)

@login_required
def tk_view(request, department_slug, course_slug, tree=None, transcript_num=None):
    '''
    Function takes a request, department_slug, course_slug, and tree of knowledge with user
    entered keyword numbers in order to render a template with the specific
    courses Tree of Knowledge.
    '''
    department_object = Department.objects.get(department_slug=department_slug)
    course_object = Course.objects.get(course_slug=course_slug)

    if transcript_num is not None:
        tree = utils.get_tree_of_knowledge(course_object, transcript_num)

    context = {
        'trees': tree,
        'course': course_object,
        'department': department_object
    }

    return render(request, 'edunet/tk.html', context)

@login_required
def course_processor(request, department_slug, course_slug):
    '''
    Takes a request, department slug, and course slug and returns an html page signifying that
    the process was successful.
    '''
    department_object = Department.objects.get(department_slug=department_slug)
    course_object = Course.objects.get(course_slug=course_slug)
    utils.process_courses(course_object)

    context = {
        'department': department_object,
        'course': course_object,
    }

    return render(request, 'edunet/course_processor.html', context)
