'''
Contains all the views for the edunet website.

CLASSES:
    IndexView(generic.TemplateView)
    HelpView(generic.TemplateView)
    SearchResultsView(generic.ListView)
    DepartmentListView(generic.ListView)
    SignUpView(generic.CreateView)
    ContributorView(generic.TemplateView)

FUNCTIONS:
    courseList(request, department_slug)
        returns rendering of a template with a list of courses
        for a particular department
    course_detail(request, department_slug, course_slug)
        returns rendering of a template with course details
    tk_form(request, department_slug, course_slug)
        returns rendering of a template with a form to request a
        specific tree of knowledge
    tk_view(request, department_slug, course_slug)
        returns rendering of a template with tree of knowledge
    pz_view(request, department_slug, course_Slug)
        returns rendering of a template with puzzle of knowledge

'''
from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404

from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from .utils import utils
from .forms import TKForm
from .models import Department, Course, TreeOfKnowledge

class HelpView(generic.TemplateView):
    '''Class used to display the student help page.'''
    template_name = 'edunet/help.html'

class SignUpView(generic.CreateView):
    '''Class allows for a user to signup for EduNet.'''
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'edunet/signup.html'

class IndexView(generic.TemplateView):
    '''Class used to display the index page.'''
    template_name = 'edunet/index.html'

class ContributorView(generic.TemplateView):
    '''Class used to display contributors page.'''
    template_name = 'edunet/contributors.html'

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
    queryset = Department.objects.order_by('department_name')

def course_list(request, department_slug):
    '''Function used to display a list of courses based on a particular department.'''

    # Filter courses if course number contains department abbreviation
    objects_unfiltered = Course.objects.filter(
        Q(course_number__icontains=Department.objects.get(department_slug=department_slug).department_abbreviation) # pylint: disable=line-too-long
    )
    request.session.set_test_cookie() # test cookies
    context = {
        'department': Department.objects.get(department_slug=department_slug),
        'courses': objects_unfiltered.order_by('course_name'),
    }
    return render(request, 'edunet/course_list.html', context)

def course_detail(request, department_slug, course_slug):
    '''Function used to display a template that contains all the details of a course.'''

    # Filter out transcripts from other courses
    matching_courses = TreeOfKnowledge.objects.filter(
        course__course_name=Course.objects.get(course_slug=course_slug)
    )
    transcript_numbers = [tree.transcript_num for tree in matching_courses]
    # declared to pass empty dictionary into context to avoid error
    transcripts = {}
    if len(transcript_numbers) != 0:
        titles = utils.get_lecture_titles(Course.objects.get(course_slug=course_slug))
        transcripts = utils.create_dict_from_two_list(transcript_numbers, titles)

    # Testing cookies
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        print('Cookie worked.')
    else:
        print('Cookie did not work.')

    hit_count = HitCount.objects.get_for_object(Course.objects.get(course_slug=course_slug))
    hit_count_reponse = HitCountMixin.hit_count(request, hit_count)
    print(hit_count_reponse)

    context = {
        'transcripts': transcripts,
        'course': Course.objects.get(course_slug=course_slug),
        'department': Department.objects.get(department_slug=department_slug),
    }
    return render(request, 'edunet/course_detail.html', context)

@login_required
def tk_form(request, department_slug, course_slug):
    '''
    Function used to display a form for a specific course that allows the user to input desired
    constraints for the retrieval of a Tree of Knowledge for that course.
    '''
    error_message = ''
    if request.method == 'GET':
        form = TKForm(request.GET)
        if form.is_valid():
            kpp = form.cleaned_data['np'] # keywords per paragraph
            kpl = form.cleaned_data['nl'] # keywords per lecture
            transcript_num = form.cleaned_data['t'] # transcript number
            if utils.validate_transcript_num(transcript_num, Course.objects.get(course_slug=course_slug)) is True: # pylint: disable=line-too-long
                # get tree based on keywords and transcript
                tree = utils.retrieve_tree_of_knowledge(
                    kpp, kpl, transcript_num, Course.objects.get(course_slug=course_slug)
                )
                return tk_view(request, department_slug, course_slug, tree)
            transcript_total_num = utils.get_transcript_num(Course.objects.get(course_slug=course_slug)) # pylint: disable=line-too-long
            error_message = 'The transcript does not exist. There is only ' + str(transcript_total_num) + ' transcripts.' # pylint: disable=line-too-long
    form = TKForm()
    context = {
        'form': form,
        'course': Course.objects.get(course_slug=course_slug),
        'department': Department.objects.get(department_slug=department_slug),
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
    if transcript_num is not None:
        tree = utils.get_tree_of_knowledge(Course.objects.get(course_slug=course_slug), transcript_num) # pylint: disable=line-too-long
    context = {
        'paragraph_num': len(tree['Paragraphs']),
        'lecture_title': tree['Lecture Title'],
        'lecture_kw': {'Lecture Keywords': tree['Lecture Keywords']},
        'paragraph_kw': {'Paragraphs': tree['Paragraphs']},
        'course': Course.objects.get(course_slug=course_slug),
        'department': Department.objects.get(department_slug=department_slug)
    }
    return render(request, 'edunet/tk.html', context)

@login_required
def pz_view(request, department_slug, course_slug, transcript_num):
    '''
    Function takes a request, department_slug, course_slug, and puzzle of knowledge with user
    entered keyword numbers in order to render a template with the specific
    courses Puzzle of Knowledge.
    '''
    if transcript_num < 10:
        transcript_num = '0' + str(transcript_num)
    puzzle = utils.get_course_number_link_format(Course.objects.get(course_slug=course_slug)) + '_' + str(transcript_num) # pylint: disable=line-too-long
    lecture_title = utils.get_puzzle_title(
        Course.objects.get(course_slug=course_slug), transcript_num
    )
    context = {
        'lecture_title': lecture_title,
        'puzzle': puzzle,
        'course': Course.objects.get(course_slug=course_slug),
        'department': Department.objects.get(department_slug=department_slug)
    }
    return render(request, 'edunet/pz.html', context)

"""
@login_required
def course_processor(request, department_slug, course_slug):
    '''
    Takes a request, department slug, and course slug and returns an html page
    signifying that the process was successful.
    '''
    utils.process_courses(Course.objects.get(course_slug=course_slug))
    context = {
        'department': Department.objects.get(department_slug=department_slug),
        'course': Course.objects.get(course_slug=course_slug),
    }
    return render(request, 'edunet/course_processor.html', context)

# for course detail template
<!--<p><a href="{% url 'edunet:course_processor' department.department_slug course.course_slug %}">Click here to process courses, this may take a minute.</a></p>-->
# for url.py
path('<slug:department_slug>/<slug:course_slug>/course-processor', views.course_processor, name='course_processor'), # pylint: disable=line-too-long
"""

def pdf_view(request):
    '''Return a pdf for the user to view.'''
    try:
        return FileResponse(
            open('edunet/static/edunet/technical-report.pdf', 'rb'), content_type='application/pdf'
        )
    except FileNotFoundError:
        raise Http404()
