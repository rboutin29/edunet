'''
Contains utility helper functions for the views.

Functions:
    get_course_link(course)
        returns course URL used to download course
    get_course_number_link_format(course)
        returns course number in a format to be used for links
    get_tree_dict(tree_list):
        returns tree of knowledge dictionary
    get_tree_of_knowledge(course, transcript)
        returns tree of knowledge for a particular course transcript
    save_tree_to_database(course, transcript)
        saves a specific tree of knowledge for a course transcript to the administrator database
        in the form of a dictionary, the tree is also saved in a folder as a text file
    get_transcript_num(course):
        helps validate_transcript_num by getting processed transcripts
    validate_transcript_num(value, course):
        doesn't allow a user to enter a transcript that doesn't exist in the retrieve tree of
        knowledge form
    build_tree_of_knowledge_dictionary(new_tok, metadata, lst):
        helps retrieve_tree_of_knowledge by building a new dictionary with desired keywords
        per paragraph and lecture to be displayed
    retrieve_tree_of_knowledge(kpp, kpl, transcript, course):
        retrives a tree of knowledge based on user inputted keywords per paragraph,
        keywords per lecture, transcript number, and course
    process_courses(course):
        processes every lecture in a course with 10 keywords per lecture and paragraph
'''
import os
import glob

from ..models import TreeOfKnowledge
from .course_processor import course_processor

def get_course_number_link_format(course):
    '''Function takes course and returns the course number in a format suitable for a link.'''
    # Handle exception for Chemistry I
    if course.course_number == 'CHEM 125a':
        course_number = 'chem125'
    else:
        course_number_upper = course.course_number.replace(' ', '') # remove spaces
        course_number = course_number_upper.lower() # lowercase number for link
    return course_number

def get_course_link(course):
    '''Function takes course and returns the link to get the course form the Yale website.'''
    start_of_link = 'http://openmedia.yale.edu/cgi-bin/open_yale/media_downloader.cgi?file=/courses/' # pylint: disable=line-too-long

    semester = course.course_season.split() # semester is first part of the string
    year = course.course_season[-2:] # last two digits of the string is the year, i.e. '08'
    course_season = (semester[0] + year).lower() # lower case season for the link
    course_number = get_course_number_link_format(course)

    # Handle exception for Financial Theory 2011 zip file link
    if course.course_number == 'ECON 252' and course.course_season == 'Spring 2011':
        course_number2 = 'econ252_11'
        link = start_of_link + course_season + '/' + course_number + '/download/' + course_number2 + '.zip' # pylint: disable=line-too-long
    else:
        # Build link
        link = start_of_link + course_season + '/' + course_number + '/download/' + course_number + '.zip' # pylint: disable=line-too-long

    return link

def get_tree_dict(tree_list):
    '''Gets a list and returns a dictionary specifically adapted for the Tree of Knowledge.'''
    tree_dict = {}
    paragraph_num = 1
    while paragraph_num < len(tree_list):
        if paragraph_num == 1:
            # Value holds transcript number and key holds keywords for the transcript
            tree_dict.update({tree_list[paragraph_num]: 'transcript'})
        # Value holds paragraph number and key holds keywords per paragraph
        tree_dict.update({tree_list[paragraph_num]: str(paragraph_num)})
        paragraph_num += 1
    return tree_dict

def get_tree_of_knowledge(course, transcipt):
    '''
    Function takes course and transcript number and returns
    a list containing the Tree of Knowledge.
    '''
    course_number = get_course_number_link_format(course)
    if transcipt < 10:
        transcipt_num = '0' + str(transcipt)
    else:
        transcipt_num = str(transcipt)
    tree_file = 'edunet/utils/out/' + course_number + "/Tree#transcript" + transcipt_num + '.txt'

    with open(tree_file, 'r') as file:
        tree = file.readlines()
    tree_dict = get_tree_dict(tree)

    return tree_dict

def save_tree_to_database(course, transcript):
    '''
    Takes a course and transcript and saves the Tree of Knowledge for
    the particalar transcript in the database. Does not override existing
    Trees of Knowledge for the same transcript.
    '''
    tok = get_tree_of_knowledge(course, transcript)
    TreeOfKnowledge(course=course, transcript_num=transcript, tree_of_knowledge=tok).save()

def get_transcript_num(course):
    '''Takes a course and returns the number of available transcripts to be processed.'''
    course_dir_path = 'edunet\\utils\\in'
    transcripts_dir_path = "**\\transcripts"
    course_number = get_course_number_link_format(course)
    course_transcripts_path = os.path.join(course_dir_path, course_number, transcripts_dir_path)
    # The first index of the list is the path we need
    course_transcripts_path_list = glob.glob(course_transcripts_path, recursive=True)
    # Don't add hidden files such as .DS_Store
    course_transcripts = glob.glob(os.path.join(course_transcripts_path_list[0], '*'))
    return len(course_transcripts)

def validate_transcript_num(value, course):
    '''Takes a course and transcript number and validates that the specific transcript exists.'''
    transcript_num = get_transcript_num(course)
    return 0 < value < transcript_num

def build_tree_of_knowledge_dictionary(new_tok, metadata, lst):
    '''
    Takes empty dictionary, metadata about transcript or paragraph and a list of keywords and
    returns dictionary with key that contains the metadata and keyword list.
    '''
    keyword_string = ''
    for word in lst:
        keyword_string = keyword_string + ' ' + word
    key_string = metadata + ':' + keyword_string
    key = {key_string: 'Not Used.'} # django prints dictionary keys to html templates
    new_tok.update(key)
    return new_tok

def retrieve_tree_of_knowledge(kpp, kpl, transcript, course):
    '''
    Takes keywords for a paragraph, keywords for a lecture, and a transcript number and
    returns that tree of knowledge to the user.
    '''
    tok = get_tree_of_knowledge(course, transcript)
    keys = list(tok.keys())
    new_tok = {}

    i = 0
    while i < len(keys):
        updated_keyword_list = [] # reset updated keyword list
        metadata, keywords = keys[i].split(':') # split paragraph number from paragraph keywords
        keyword_list = keywords.split() # split paragraph keywords into a list
        j = 0
        if i == 0:
            while j < kpl:
                # get all the lecture keywords that the user wants
                updated_keyword_list.append(keyword_list[j])
                j += 1
            build_tree_of_knowledge_dictionary(new_tok, metadata, updated_keyword_list)
        else:
            while j < kpp:
                # get all the paragraph keywords that the user wants
                updated_keyword_list.append(keyword_list[j])
                j += 1
            build_tree_of_knowledge_dictionary(new_tok, metadata, updated_keyword_list)
        i += 1
    return new_tok

def process_courses(course):
    '''Takes a course and processes and saves all the lectures in it.'''
    link = get_course_link(course)
    kpl = 10
    kpp = 10
    course_processor(link, kpl, kpp)
    transcipt_num = get_transcript_num(course)
    print('Total transcripts: ' + str(transcipt_num))
    i = 1
    while i <= transcipt_num:
        print("Saving lecture " + str(i))
        save_tree_to_database(course, i)
        i += 1
