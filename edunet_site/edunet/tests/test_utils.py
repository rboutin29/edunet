'''
Contains all the tests for the utils of Edunet.
'''
import cv2

from django.test import TestCase

from ..utils import utils
from ..models import Course, TreeOfKnowledge, PuzzleOfKnowledge

class UtilTests(TestCase):
    '''Class to test all the utils of Edunet with an example.'''
    fixtures = ['edunet_testdata.json']

    def test_get_course_number_link_format(self):
        '''Test get_course_number_link_format to return the course number in link format.'''
        course = Course.objects.get(course_number='AFAM 162')
        self.assertEqual(utils.get_course_number_link_format(course), 'afam162')

    def test_get_course_link(self):
        '''Test get_course_link to return a valid link.'''
        link = 'http://openmedia.yale.edu/cgi-bin/open_yale/media_downloader.cgi?file=/courses/spring10/afam162/download/afam162.zip' #pylint: disable=line-too-long 
        course = Course.objects.get(course_number='AFAM 162')
        self.assertEqual(utils.get_course_link(course), link)

    def test_get_tree_dict(self):
        '''Test get_tree_dict to return a specially adapted dictionary for the TreeOfKnowledge.'''
        tok = TreeOfKnowledge.objects.get(transcript_num=1)
        tree_file = "edunet/utils/out/afam162/Tree#transcript01.txt"
        with open(tree_file, 'r') as file:
            tree = file.readlines()
        new_tree_dict = utils.get_tree_dict(tree)
        # tree_dict.tree_of_knowledge returns string so assertEqual dict to string will
        # always be false unless the new dictionary is converted to a string too
        self.assertIn(str(new_tree_dict), tok.tree_of_knowledge)

    def test_get_puzzle_dict(self):
        '''
        Test get_puzzle_dict to return a specially adapted
        dictionary for the PuzzleOfKnowledge.
        '''
        pok = PuzzleOfKnowledge.objects.get(transcript_num=1)
        puzzle_file = "edunet/utils/out/afam162/Puzzle#transcript01.txt"
        with open(puzzle_file, 'r') as file:
            puzzle = file.readlines()
        new_puzzle_dict = utils.get_puzzle_dict(puzzle)
        self.assertIn(str(new_puzzle_dict), pok.puzzle_of_knowledge)

    def test_get_tree_of_knowledge(self):
        '''
        Test get_tree_of_knowledge to return a specially
        adatpted dictionary for the Tree Of Knowledge.
        '''
        tok = TreeOfKnowledge.objects.get(transcript_num=1)
        course = Course.objects.get(course_number='AFAM 162')
        new_tree_dict = utils.get_tree_of_knowledge(course, 1) # get the first transcript
        self.assertIn(str(new_tree_dict), tok.tree_of_knowledge)

    def test_get_puzzle_of_knowledge(self):
        '''
        Test get_puzzle_of_knowledge to return a specially adapted
        for the Puzzle of Knowledge.
        '''
        pok = PuzzleOfKnowledge.objects.get(transcript_num=1)
        course = Course.objects.get(course_number='AFAM 162')
        new_puzzle_dict = utils.get_puzzle_of_knowledge(course, 1)
        self.assertIn(str(new_puzzle_dict), pok.puzzle_of_knowledge)

    def test_validate_transcript_num(self):
        '''Test validate_transcript_num to make sure value is between zero total transcript number.''' # pylint: disable=line-too-long
        course = Course.objects.get(course_name='African American History: From Emancipation to the Present') # pylint: disable=line-too-long
        for i in range(1, utils.get_transcript_num(course)):
            self.assertTrue(utils.validate_transcript_num(i, course))

    def test_retrieve_tree_of_knowledge(self):
        '''
        Test retrieve_tree_of_knowledge to make sure the correct tree is returned with
        proper keywords per lecture, keywords per paragraph, course, and transcript.
        '''
        tok = TreeOfKnowledge.objects.get(transcript_num=1)
        course = Course.objects.get(course_number='AFAM 162')
        new_tree_dict = utils.retrieve_tree_of_knowledge(10, 10, 1, course)
        self.assertIn(str(new_tree_dict), tok.tree_of_knowledge)

    def test_get_transcript_num(self):
        '''Test get_transcript_num to return the correct number of available transcripts.'''
        # Only one course in test data
        total_transcripts = len(TreeOfKnowledge.objects.all())
        course = Course.objects.get(course_number='AFAM 162')
        self.assertEqual(total_transcripts, utils.get_transcript_num(course))

    def test_generate_puzzle(self):
        '''Test generate_puzzle to create an image.'''
        course = Course.objects.get(course_number='AFAM 162')
        puzzle_dict = utils.get_puzzle_of_knowledge(course, 1)
        new_puzzle = utils.generate_puzzle(puzzle_dict)
        puzzle = cv2.imread('edunet/static/edunet/images/puzzle_afam162/Puzzle#transcript01.jpg') # pylint: disable=no-member
        self.assertIn(new_puzzle, puzzle)

    def test_get_lecture_titles(self):
        '''Test get_lecture_titles to return the correct lecture titles.'''
        course = Course.objects.get(course_number='AFAM 162')
        new_lecture_titles = utils.get_lecture_titles(course)
        transcripts = utils.get_transcript_num(course)
        i = 1
        while i <= transcripts:
            # Get tree of knowledge data and make sure title is in it
            tree = TreeOfKnowledge.objects.get(transcript_num=i).tree_of_knowledge
            # convert to strings to check if string is in larger string
            self.assertIn(str(new_lecture_titles[i-1]), tree)
            i += 1

    def test_create_dict_from_two_lists(self):
        '''Functions tests the create_dict_from_two_lists function.'''
        list1 = [1, 2, 3]
        list2 = [1.1, 2.1, 3.1]
        dict1 = utils.create_dict_from_two_list(list1, list2)
        keys = list(dict1.keys())
        self.assertEqual(list1, keys)
        values = list(dict1.values())
        self.assertEqual(list2, values)

    def test_get_puzzle_title(self):
        '''Functions tests the get_puzzle_title function.'''
        pok = PuzzleOfKnowledge.objects.get(transcript_num=1).puzzle_of_knowledge
        title = utils.get_puzzle_title(Course.objects.get(course_number='AFAM 162'), 1)
        self.assertIn(title, pok)
