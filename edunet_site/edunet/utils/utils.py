'''
Contains utility helper functions for the views.

Functions:
    get_course_link(course)
        returns course URL used to download course
    get_course_number_link_format(course)
        returns course number in a format to be used for links
    get_tree_dict(tree_list):
        returns tree of knowledge dictionary
    get_puzzle_dict(puzzle_list):
        returns puzzle of knowledge dictionary
    get_tree_of_knowledge(course, transcript)
        returns tree of knowledge for a particular course transcript
    get_puzzle_of_knowledge(course, transcript)
        returns puzzle of knowledge for a particualr course transcript
    save_tree_to_database(course, transcript)
        saves a specific tree of knowledge for a course transcript to the administrator interface
        in the form of a dictionary, the tree is also saved in utils/out as a text file. Saves
        puzzle dictionary to admin interface, 6x6 puzzle image to staticimages by course, and
        a text file of the puzzle in utils/out
    get_transcript_num(course):
        helps validate_transcript_num by getting processed transcripts
    validate_transcript_num(value, course):
        doesn't allow a user to enter a transcript that doesn't exist in the retrieve tree of
        knowledge form
    retrieve_tree_of_knowledge(kpp, kpl, transcript, course):
        retrives a tree of knowledge based on user inputted keywords per paragraph,
        keywords per lecture, transcript number, and course
    process_courses(course):
        processes every lecture in a course with 10 keywords per lecture and paragraph, and a puzzle
        dimension of 6x6
    get_lecture_titles(course):
        gets all the lecture titles of the given course and returns them
    create_dict_from_two_list(list1, list2):
        creates a dictionary where list1 is the key set and list2 is the value set.
        Returns the dictionary
    get_puzzle_title(course, transcipt):
        gets the transcripts title for the puzzle when given a specific course and transcript
'''
import os
import glob
import textwrap
import cv2
import numpy as np

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from ..models import TreeOfKnowledge, PuzzleOfKnowledge
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
    tree_dict = {'Lecture Title': '', 'Lecture Keywords': [], 'Paragraphs': {}}
    line_num = 1
    stop_words = set(stopwords.words('english'))
    while line_num < len(tree_list):
        branch = tree_list[line_num]
        if line_num == 1:
            # Update lecture title
            lecture_title_list = branch.split('-', 1)
            lecture_title = lecture_title_list[1].split(':')[0]
            tree_dict.update({'Lecture Title': lecture_title})
        else:
            # Clean branch before updating keywords
            branch = branch.split(':')[1]
            branch = branch.replace("b'", '') # replacing the encodings
            branch = branch.replace("'", '')
            # Remove stop words
            branch = word_tokenize(branch)
            branch_no_stop_words = []
            for word in branch:
                if word not in stop_words:
                    branch_no_stop_words.append(word)
            if line_num == 2:
                # Update lecture keywords
                tree_dict.update({'Lecture Keywords': branch_no_stop_words})
            else:
                # Update paragraph keywords
                branch_filtered = []
                for word in branch_no_stop_words:
                    # No single character words and that the word are comprised of only letters
                    if len(word) != 1 and word.isalpha():
                        branch_filtered.append(word)
                tree_dict['Paragraphs'].update({'Paragraph ' + str(line_num  - 2) + ' Keywords': branch_filtered}) # pylint: disable=line-too-long
        line_num += 1
    return tree_dict

def get_tree_of_knowledge(course, transcript):
    '''
    Function takes course and transcript number and returns
    a list containing the Tree of Knowledge.
    '''
    course_number = get_course_number_link_format(course)
    if transcript < 10:
        transcipt_num = '0' + str(transcript)
    else:
        transcipt_num = str(transcript)
    tree_file = 'edunet/utils/out/' + course_number + "/Tree#transcript" + transcipt_num + '.txt'

    with open(tree_file, 'r') as file:
        tree = file.readlines()
    tree_dict = get_tree_dict(tree)

    return tree_dict

def get_puzzle_dict(puzzle_list):
    '''Gets a list and returns a dictionary specifically adapted for the Puzzle of Knowledge.'''
    puzzle_dict = {'Lecture Title': '', 'Puzzle': {}}
    row_num = 0
    while row_num < len(puzzle_list):
        # key holds keyword info and value holds row number
        if row_num == 0:
            # Update lecture title
            lecture_title_list = puzzle_list[row_num].split('-', 1)
            lecture_title = lecture_title_list[0]
            puzzle_dict.update({'Lecture Title': lecture_title})
        else:
            piece = puzzle_list[row_num].replace('*', '...')
            piece = piece.replace('#', '')
            piece = piece.replace("b'", '')
            piece = piece.replace("'", '')
            piece = piece.replace('up', '')
            piece = piece.replace('down', '')
            piece = piece.replace('\n', '')
            puzzle_dict['Puzzle'].update({piece: row_num})
        row_num += 1
    return puzzle_dict

def get_puzzle_of_knowledge(course, transcipt):
    '''
    Function takes course and transcript number and returns
    an dictionary containing the Puzzle of Knowledge and saves
    an image containing the puzzle of knowledge.
    '''
    course_number = get_course_number_link_format(course)
    if transcipt < 10:
        transcipt_num = '0' + str(transcipt)
    else:
        transcipt_num = str(transcipt)
    puzzle_file = 'edunet/utils/out/' + course_number + "/Puzzle#transcript" + transcipt_num + '.txt' # pylint: disable=line-too-long

    with open(puzzle_file, 'r') as file:
        puzzle = file.readlines()
    puzzle_dict = get_puzzle_dict(puzzle)
    # Generate image and save to static files
    puzzle = generate_puzzle(puzzle_dict)
    puzzle_path = 'edunet/static/edunet/images/puzzle_' + course_number
    if not os.path.isdir(puzzle_path):
        os.mkdir(puzzle_path) # create new directory to save puzzle images
    puzzle_path = puzzle_path + "/Puzzle#transcript" + transcipt_num + '.jpg' # pylint: disable=line-too-long
    print('Saving puzzle image...' + str(cv2.imwrite(puzzle_path, puzzle))) # pylint: disable=no-member
    # Return dictionary of puzzle words for admin
    return puzzle_dict

def save_data_to_database(course, transcript):
    '''
    Takes a course and transcript and saves the Tree of Knowledge and
    Puzzle of Knowledge for the particalar transcript in the database.
    Does not override existing Trees of Knowledge and Puzzles of
    Knowledge for the same transcript.
    '''
    tok = get_tree_of_knowledge(course, transcript)
    pok = get_puzzle_of_knowledge(course, transcript)
    TreeOfKnowledge(course=course, transcript_num=transcript, tree_of_knowledge=tok).save()
    PuzzleOfKnowledge(course=course, transcript_num=transcript, puzzle_of_knowledge=pok).save()

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

def retrieve_tree_of_knowledge(kpp, kpl, transcript, course):
    '''
    Takes keywords for a paragraph, keywords for a lecture, and a transcript number and
    returns that tree of knowledge to the user.
    '''
    tok = get_tree_of_knowledge(course, transcript)
    new_tok = {'Lecture Title': '', 'Lecture Keywords':[], 'Paragraphs': {}}
    new_tok['Lecture Title'] = tok['Lecture Title']
    i = 0
    while i < kpl:
        new_tok['Lecture Keywords'].append(tok['Lecture Keywords'][i])
        i += 1
    i = 0
    while i < len(tok['Paragraphs']):
        # Take total keywords if requested keywords equals or exceeds total keywords
        if kpp >= len(tok['Paragraphs']['Paragraph ' + str(i + 1) + ' Keywords']):
            # paragraph keywords begin on paragraph 2 for tok but redo paragraph numbers for new_tok
            # this is why paragraph numbers have plus 1 for new_tok and plus 2 for tok
            print('keywords wanted equals or exceeds total keywords on paragraph ' + str(i + 1))
            new_tok['Paragraphs'].update({'Paragraph ' + str(i + 1) + ' Keywords': tok['Paragraphs']['Paragraph ' + str(i + 1) + ' Keywords']}) # pylint: disable=line-too-long
        else:
            j = 0
            # Initialize paragraph key to avoid KeyError
            new_tok['Paragraphs'].update({'Paragraph ' + str(i + 1) + ' Keywords': []})
            while j < kpp:
                new_tok['Paragraphs']['Paragraph ' + str(i + 1) + ' Keywords'].append(tok['Paragraphs']['Paragraph ' + str(i + 1) + ' Keywords'][j]) # pylint: disable=line-too-long
                j += 1
        i += 1
    return new_tok

def process_courses(course):
    '''Takes a course and processes and saves all the lectures in it.'''
    link = get_course_link(course)
    kpl = 10
    kpp = 10
    puzz_dim = 6
    course_processor(link, kpl, kpp, puzz_dim)
    transcipt_num = get_transcript_num(course)

    # Handle exception for HSAR
    if course.course_number == 'HSAR 252':
        transcipt_num = 23

    print('Total transcripts: ' + str(transcipt_num))
    i = 1
    while i <= transcipt_num:
        print("Saving lecture " + str(i))
        save_data_to_database(course, i)
        i += 1

def generate_puzzle(puzzle_dict):
    '''Generates an 6x6 puzzle of keywords.'''
    keys = list(puzzle_dict['Puzzle'].keys())
    width = 400
    height = 400

    whiteblankimage = 255 * np.ones(shape=[height, width, 3], dtype=np.uint8)

    i = 0
    while i < len(keys):
        # Give top and bottom border words a different color
        if i in (0, len(keys) - 1):
            # No member warning is from pylint not recognizing cv2 source code in C
            wrapped_text = textwrap.wrap(keys[i], width=40)
            y_pos = i * 60 + 55
            # See if wrapped text needs to be printed, only expect one extra line of wrapped text
            if len(wrapped_text) > 1:
                cv2.putText(whiteblankimage, wrapped_text[0], org=(10, y_pos), # pylint: disable=no-member
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 0, 0), # pylint: disable=no-member
                            thickness=2, lineType=cv2.LINE_AA) # pylint: disable=no-member
                cv2.putText(whiteblankimage, wrapped_text[1], org=(50, y_pos + 25), # pylint: disable=no-member
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 0, 0), # pylint: disable=no-member
                            thickness=2, lineType=cv2.LINE_AA) # pylint: disable=no-member
            else:
                cv2.putText(whiteblankimage, wrapped_text[0], org=(10, y_pos), # pylint: disable=no-member
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 0, 0), # pylint: disable=no-member
                            thickness=2, lineType=cv2.LINE_AA) # pylint: disable=no-member
        else:
            wrapped_text = textwrap.wrap(keys[i], width=40)
            y_pos = i * 60 + 55
            if len(wrapped_text) > 1:
                cv2.putText(whiteblankimage, wrapped_text[0], org=(10, y_pos), # pylint: disable=no-member
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 0, 0), # pylint: disable=no-member
                            thickness=2, lineType=cv2.LINE_AA) # pylint: disable=no-member
                cv2.putText(whiteblankimage, wrapped_text[1], org=(50, y_pos + 25), # pylint: disable=no-member
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 0, 0), # pylint: disable=no-member
                            thickness=2, lineType=cv2.LINE_AA) # pylint: disable=no-member
            else:
                cv2.putText(whiteblankimage, wrapped_text[0], org=(10, y_pos), # pylint: disable=no-member
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 0, 0), # pylint: disable=no-member
                            thickness=2, lineType=cv2.LINE_AA) # pylint: disable=no-member          
        i += 1
    return whiteblankimage

def get_lecture_titles(course):
    '''
    Function takes course and returns
    a list containing the lecture titles.
    '''
    titles = []
    course_number = get_course_number_link_format(course)
    transcript = 1
    while transcript <= get_transcript_num(course):
        if transcript < 10:
            transcipt_num = '0' + str(transcript)
        else:
            transcipt_num = str(transcript)
        tree_file = 'edunet/utils/out/' + course_number + "/Tree#transcript" + transcipt_num + '.txt' # pylint: disable=line-too-long
        with open(tree_file, 'r') as file:
            lines = file.readlines()
        lecture_title_list = lines[1].split('-', 1) # second line contains the titles
        lecture_title = lecture_title_list[1].split(':')[0]
        titles.append(lecture_title)
        transcript += 1
    return titles

def create_dict_from_two_list(list1, list2):
    '''
    Function takes numbers from list1 and puts them as the
    key of the dictionary and takes the titles
    from list2 and puts them as the values. NOTE: These
    lists should be the same length.
    '''
    dictionary = {}
    i = 0
    while i < len(list1):
        if len(list2) == 0:
            # No titles so transcript numbers are keys
            dictionary.update({list1[i]: ''})
        else:
            dictionary.update({list1[i]: list2[i]})
        i += 1
    return dictionary

def get_puzzle_title(course, transcipt):
    '''
    Function takes course and transcript number and returns
    an dictionary containing the Puzzle of Knowledge and saves
    an image containing the puzzle of knowledge.
    '''
    course_number = get_course_number_link_format(course)
    transcipt = int(transcipt)
    if transcipt < 10:
        transcipt_num = '0' + str(transcipt)
    else:
        transcipt_num = str(transcipt)
    puzzle_file = 'edunet/utils/out/' + course_number + "/Puzzle#transcript" + transcipt_num + '.txt' # pylint: disable=line-too-long

    with open(puzzle_file, 'r') as file:
        puzzle = file.readline()
    return puzzle.split('-')[0]
