'''
Contains all the tests for the views of Edunet.
'''
from django.test import TestCase, Client

from .. import views

class EdunetViewsTestCase(TestCase):
    '''Class to test all the views of Edunet with an example.'''
    fixtures = ['edunet_testdata.json']

    def test_signup(self):
        '''Test the signup view.'''
        response = self.client.get('/edunet/signup/')
        # Successful HTTP GET request returns status code 200
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/signup.html')
        self.assertEqual(
            response.resolver_match.func.__name__, views.SignUpView.as_view().__name__
        )
        # Sign up is built in django feature

    def test_index(self):
        '''Test the index view.'''
        response = self.client.get('/edunet/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/index.html')
        self.assertEqual(
            response.resolver_match.func.__name__, views.IndexView.as_view().__name__
        )
        # User model is built in django so no need to test

    def test_search_results(self):
        '''Test the search_results view.'''
        # Initiate GET response with a search query
        response = self.client.get('/edunet/search/', {'search_query': 'AFAM'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/search_results.html')
        self.assertEqual(
            response.resolver_match.func.__name__, views.SearchResultsView.as_view().__name__
        )
        course_list = response.context['object_list']
        # Search query must be within each course name
        for course in course_list:
            self.assertIn('African American History', course.course_name)
        # Test when search query is a course number
        response = self.client.get('/edunet/search/?search_query=AFAM')
        self.assertEqual(response.status_code, 200)
        course_list = response.context['object_list']
        for course in course_list:
            self.assertIn('AFAM', course.course_number[:4])

    def test_department(self):
        '''Test the department list view.'''
        response = self.client.get('/edunet/departments/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/department.html')
        self.assertEqual(
            response.resolver_match.func.__name__, views.DepartmentListView.as_view().__name__
        )
        self.assertTrue('departments' in response.context)
        dep_1 = response.context['departments'][0]
        self.assertEqual(dep_1.department_name, 'African American Studies')

    def test_help(self):
        '''Test the help view.'''
        response = self.client.get('/edunet/help/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/help.html')
        self.assertEqual(
            response.resolver_match.func.__name__, views.HelpView.as_view().__name__
        )
        # Only text in this template, no context

    def test_course_list(self):
        '''Test the course_list view.'''
        response = self.client.get('/edunet/african-american-studies/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/course_list.html')
        self.assertTrue('department' in response.context)
        self.assertTrue('courses' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        course_list = response.context['courses']
        for course in course_list:
            self.assertEqual(course.course_number[:4], 'AFAM')

    def test_course_detail(self):
        '''Test the course_detail view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/course_detail.html')
        self.assertTrue('titles' in response.context)
        self.assertTrue('department' in response.context)
        self.assertTrue('course' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        self.assertEqual(response.context['course'].course_name, 'African American History: From Emancipation to the Present') # pylint: disable=line-too-long

    def test_tk_form(self):
        '''Test tk_form view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/tree-form/') # pylint: disable=line-too-long
        # Status Code 302 because view is decorated with login_required
        self.assertEqual(response.status_code, 302)
        # Redirect location
        self.assertEqual(response['Location'], '/accounts/login/?next=/edunet/african-american-studies/african-american-history-emancipation-present/tree-form/') # pylint: disable=line-too-long
        # Access view by logging in
        response = self.client.get(
            '/edunet/african-american-studies/african-american-history-emancipation-present/tree-form/', # pylint: disable=line-too-long
            follow=True,
        )
        # Assert login page is found
        self.assertEqual(response.status_code, 200)
        # Create user and login to check credentials of tk_form
        user = Client()
        self.assertTrue(user.login(username='rianl', password='rianl'))
        response = user.get('/edunet/african-american-studies/african-american-history-emancipation-present/tree-form/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/tk_form.html')
        self.assertTrue('form' in response.context)
        self.assertTrue('error_message' in response.context)
        self.assertTrue('course' in response.context)
        self.assertTrue('department' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        self.assertEqual(response.context['course'].course_number, 'AFAM 162')

    def test_tk_view(self):
        '''Test tk_tree view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/1-tree/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/edunet/african-american-studies/african-american-history-emancipation-present/1-tree/') # pylint: disable=line-too-long
        # Ensure a nonexistant tree of knowledge throws a 404
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/-1-tree/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            '/edunet/african-american-studies/african-american-history-emancipation-present/1-tree/', # pylint: disable=line-too-long
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = Client()
        self.assertTrue(user.login(username='rianl', password='rianl'))
        response = user.get('/edunet/african-american-studies/african-american-history-emancipation-present/1-tree/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/tk.html')
        self.assertTrue('lecture_title' in response.context)
        self.assertTrue('paragraph_num' in response.context)
        self.assertTrue('lecture_kw' in response.context)
        self.assertTrue('paragraph_kw' in response.context)
        self.assertTrue('course' in response.context)
        self.assertTrue('department' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        self.assertEqual(response.context['course'].course_number, 'AFAM 162')

    def test_pz_view(self):
        '''Test pk_tree view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/1-puzzle/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/edunet/african-american-studies/african-american-history-emancipation-present/1-puzzle/') # pylint: disable=line-too-long
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/-1-puzzle/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            '/edunet/african-american-studies/african-american-history-emancipation-present/1-puzzle/', # pylint: disable=line-too-long
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = Client()
        self.assertTrue(user.login(username='rianl', password='rianl'))
        response = user.get('/edunet/african-american-studies/african-american-history-emancipation-present/1-puzzle/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.templates[0].name, 'edunet/pz.html')
        self.assertTrue('lecture_title' in response.context)
        self.assertTrue('puzzle' in response.context)
        self.assertTrue('course' in response.context)
        self.assertTrue('department' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        self.assertEqual(response.context['course'].course_number, 'AFAM 162')

    def test_course_processor(self):
        '''Test course_processor.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-emancipation-present/course-processor/') # pylint: disable=line-too-long
        # Can only be accessed through a login required page so theres a 404
        # error unless the user is logged in
        self.assertEqual(response.status_code, 404)
