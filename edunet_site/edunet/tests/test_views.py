'''
Contains all the tests for the views of Edunet.
'''
from django.test import TestCase

class EdunetViewsTestCase(TestCase):
    '''Class to test all the views of Edunet with an example.'''
    fixtures = ['edunet_testdata.json']

    def test_signup(self):
        '''Test the signup view.'''
        response = self.client.get('/edunet/signup/')
        # Successful HTTP GET request returns status code 200
        self.assertEqual(response.status_code, 200)
        # Sign up is built in django feature

    def test_index(self):
        '''Test the index view.'''
        response = self.client.get('/edunet/')
        self.assertEqual(response.status_code, 200)
        # User model is built in django so no need to test

    def test_search_results(self):
        '''Test the search_results view.'''
        # Search query is part of a course title
        response = self.client.get('/edunet/search/?search_query=African+American+History')
        self.assertEqual(response.status_code, 200)
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
        self.assertTrue('departments' in response.context)
        dep_1 = response.context['departments'][0]
        self.assertEqual(dep_1.department_name, 'African American Studies')

    def test_course_list(self):
        '''Test the course_list view.'''
        response = self.client.get('/edunet/african-american-studies/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('department' in response.context)
        self.assertTrue('courses' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        course_list = response.context['courses']
        for course in course_list:
            self.assertEqual(course.course_number[:4], 'AFAM')

    def test_course_detail(self):
        '''Test the course_detail view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 200)
        self.assertTrue('department' in response.context)
        self.assertTrue('course' in response.context)
        self.assertTrue('transcript_numbers' in response.context)
        self.assertEqual(response.context['department'].department_name, 'African American Studies')
        self.assertEqual(response.context['course'].course_name, 'African American History: From Emancipation to the Present') # pylint: disable=line-too-long

    def test_tk_form(self):
        '''Test tk_form view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/form/') # pylint: disable=line-too-long
        # Status Code 302 because view is decorated with login_required
        self.assertEqual(response.status_code, 302)
        # Redirect location
        self.assertEqual(response['Location'], '/accounts/login/?next=/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/form/') # pylint: disable=line-too-long

    def test_tk_tree(self):
        '''Test tk_tree view.'''
        response = self.client.get('/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/1/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/1/') # pylint: disable=line-too-long
        # Ensure a nonexistant tree of knowledge throws a 404
        response = self.client.get('/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/-1/') # pylint: disable=line-too-long
        self.assertEqual(response.status_code, 404)
