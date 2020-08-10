'''
Contains all the tests for the utils of Edunet.
'''
from django.test import TestCase

from ..utils import utils
from ..models import Department, Course, TreeOfKnowledge

class UtilTests(TestCase):
    '''Class to test all the utils of Edunet with an example.'''
    fixtures = ['edunet_testdata.json']

    def test_get_department(self):
        '''Test get_department to return a proper department abbrievation or a correct failure message.''' # pylint: disable=line-too-long
        department = Department.objects.get(department_slug='african-american-studies')
        self.assertEqual(utils.get_department(department.department_slug), 'AFAM')
        self.assertEqual(utils.get_department('null'), 'No department abbreviation found.')

    def test_get_course_number_link_format(self):
        '''Test get_course_number_link_format to return the course number in link format.'''
        course = Course.objects.get(course_name='African American History: From Emancipation to the Present') # pylint: disable=line-too-long
        self.assertEqual(utils.get_course_number_link_format(course), 'afam162')

    def test_get_course_link(self):
        '''Test get_course_link to return a valid link.'''
        link = 'http://openmedia.yale.edu/cgi-bin/open_yale/media_downloader.cgi?file=/courses/spring10/afam162/download/afam162.zip' #pylint: disable=line-too-long 
        course = Course.objects.get(course_name='African American History: From Emancipation to the Present') # pylint: disable=line-too-long
        self.assertEqual(utils.get_course_link(course), link)

    def test_get_tree_dict(self):
        '''Test get_tree_dict to return a specially adapted dictionary for the TreeOfKnowledge.'''
        tree_dict = TreeOfKnowledge.objects.get(pk=23, course=1, transcript_num=1)
        tree_file = "edunet/utils/out/afam162/Tree#transcript01.txt"
        with open(tree_file, 'r') as file:
            tree = file.readlines()
        new_tree_dict = utils.get_tree_dict(tree)
        # tree_dict.tree_of_knowledge returns string so can assertEqual dict to string
        self.assertIn(str(new_tree_dict), tree_dict.tree_of_knowledge)

    def test_get_tree_of_knowledge(self):
        '''Test get_tree_of_knowledge to return a specially adatpted dictionary for the TreeOfKnowledge.''' # pylint: disable=line-too-long
        tree_dict = TreeOfKnowledge.objects.get(pk=23, course=1, transcript_num=1)
        course = Course.objects.get(course_name='African American History: From Emancipation to the Present') # pylint: disable=line-too-long
        transcript = 1
        new_tree_dict = utils.get_tree_of_knowledge(course, transcript)
        self.assertIn(str(new_tree_dict), tree_dict.tree_of_knowledge)

    def test_validate_transcript_num(self):
        '''Test validate_transcript_num to make sure value is between zero total transcript number.''' # pylint: disable=line-too-long
        course = Course.objects.get(course_name='African American History: From Emancipation to the Present') # pylint: disable=line-too-long
        for i in range(1, utils.get_transcript_num(course)):
            self.assertTrue(utils.validate_transcript_num(i, course))
