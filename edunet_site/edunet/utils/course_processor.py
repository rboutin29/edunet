'''
File used to process courses and create text files that contain the Tree and Puzzle of knowledge.
'''
__author__ = 'becheru'
__author__ = 'boutin'

import os
import shutil
import zipfile
import glob

from datetime import datetime

from bs4 import BeautifulSoup
import nltk as nl
import networkx as nx

import wget

def course_processor(link, keywords_paragraph, keywords_lecture, puzz_dim, transcript=None):
    '''
    Function used that processes courses to create text files that contains the Tree and
    Puzzle of Knowledge. Duplicate Trees are replaced while puzzles are continously added
    to the existing files even if the dimensions are the same.
    '''

    wnl = nl.WordNetLemmatizer()

    class Lecture:
        '''Class used to parse the course lectures.'''
        def __init__(self, path, name):
            self.name = name
            self.path = path
            self.graph = nx.DiGraph()

        def nlp_pipeline(self):
            """Passes document through html parsing and nlp pipeline and returns a list of nouns."""
            file_in = open(self.path, encoding='utf-8')
            soup = BeautifulSoup(file_in, "html.parser")  # parse html
            soup_paragraphs = soup.find_all('p')  # retrieve all paragraphs
            try:
                # not all transcripts have titles
                soup_lecture_title = soup.find('h3').getText() # assuming first and only h3 tag is the title
                # clean up the title
                lecture_title_list = soup_lecture_title.split('-', 1)
                lecture_title = lecture_title_list[1].split('[')[0]
                lecture_title = lecture_title.strip()
            except AttributeError:
                lecture_title = ''
            list_of_nouns = []  # the resulting list of nouns

            # each paragraph is parsed through nlp pipeline
            for paragraph in soup_paragraphs[:-3]:  # the last three vector are null respective [end,of,transcript] pylint: disable=line-too-long
                text = paragraph.getText()

                # Tokenization
                tokens = nl.word_tokenize(text, language="english")
                for token in tokens:
                    if token.isalpha() == 0:
                        tokens.remove(token)

                # POS tagginng filtering for NOUNS
                text_pos = nl.pos_tag(tokens)
                tokens_pos = []
                for token_pos in text_pos:
                    if token_pos[1][0:2] == "NN" or token_pos[0] == ".":
                        try:
                            tokens_pos.append(token_pos[0])
                        except:
                            tokens_pos(token_pos[0])

                # lemmatization
                lemmas = []
                for s in tokens_pos:
                    try:
                        lemmas.append(wnl.lemmatize(s))
                    except:
                        lemmas.append(s)

                # lower casing
                paragraph_nouns = [word.lower() for word in lemmas]  # list of nouns per paragraph
                list_of_nouns.append(paragraph_nouns)

            return list_of_nouns, lecture_title  # return the list of nouns per document and the title of the document

        def text_to_graph(self, list_of_words):
            '''Function used to add text to a graph in order to determine relevancy.'''
            if list_of_words != []:
                self.graph.add_node(list_of_words[0])
                for i in range(1, len(list_of_words)):
                    self.graph.add_node(list_of_words[i])
                    self.graph.add_edge(list_of_words[i - 1], list_of_words[i], weight=1)
                if self.graph.has_node("."):
                    self.graph.remove_node(".")


    class TreeOfKnowledge(Lecture):
        '''Class used to create the Tree of Knowledge.'''
        def __init__(self, paragraph_dimension, lecture_dimension, name, path, title=None):
            self.name = name
            self.path = path
            self.lecture_title = title
            self.paragraph_dimension = paragraph_dimension
            self.lecture_dimension = lecture_dimension
            self.lecture_keywords = []
            self.lecture_keywords_per_paragraph = {}
            self.graph = nx.DiGraph()

        def add_lecture_keywords(self, keywords):
            '''Function to add lecture keywords to Tree of Knowledge.'''
            self.lecture_keywords.extend(keywords)

        def add_lecture_keywords_per_paragraph(self, paragraph, keywords):
            '''Function to add paragraph keywords to Tree of Knowledge.'''
            self.lecture_keywords_per_paragraph[paragraph] = keywords

        def analysis(self):
            '''Function used to analyze text and then create the Tree of Knowledge.'''
            lecture_words = []
            words, self.lecture_title = self.nlp_pipeline()
            paragraph_counter = 0
            for word in words:
                paragraph_counter += 1
                lecture_words.extend(word)
                self.text_to_graph(word)
                ranked_words = nx.pagerank(self.graph)
                self.graph = nx.DiGraph()
                paragraph_keywords = sorted(ranked_words, key=ranked_words.get, reverse=True)[:self.paragraph_dimension] # pylint: disable=line-too-long
                self.add_lecture_keywords_per_paragraph(paragraph_counter, paragraph_keywords)
            self.text_to_graph(lecture_words)
            ranked_words = nx.pagerank(self.graph)
            lecture_keywords = sorted(ranked_words, key=ranked_words.get, reverse=True)[:self.lecture_dimension] # pylint: disable=line-too-long
            self.add_lecture_keywords(lecture_keywords)

        def write_to_file(self, file_path):
            '''Function writes Tree of Knowledge to file.'''
            file = open(file_path, "w")
            file.write("\n" + self.name + '-' + self.lecture_title + ":")
            file.write("\n--------Lecture: ")
            for k in self.lecture_keywords:
                file.write(str(k.encode('utf-8', errors='ignore')) + " ")
            for paragraph in self.lecture_keywords_per_paragraph.keys():
                file.write("\n--------" + str(paragraph) + " paragraph: ")
                for k in self.lecture_keywords_per_paragraph[paragraph]:
                    file.write(str(k.encode('utf-8', errors='ignore')) + " ")
            file.close()


    class PuzzleOfKnowledge(Lecture):
        '''Class used to create the Puzzle of Knowledge.'''
        def __init__(self, name, path, puzzle_dimension, title=None):
            self.name = name
            self.path = path
            self.lecture_title = title
            self.puzzle_dimension = puzzle_dimension
            self.graph = nx.DiGraph()

        def snail_road(self):
            '''
            Creates snail path of matrix that is used to create Puzzle of Knowledge
            because path is in order of word relevancy.
            '''
            # Input nr of lines in a lines x linex matrix
            # Output an ordered vector with the snail path of the matrix
            # each element of the vector is a dictionary where key is repsents
            # the line and value represents the column

            lines = self.puzzle_dimension
            stop = lines / 2
            snail = []
            tmp = 0
            while lines > stop:
                x = range(tmp, lines - 1)
                for i in x:
                    snail.append({tmp: i})
                for i in x:
                    snail.append({i: lines - 1})
                x = reversed(range(tmp + 1, lines))
                for i in x:
                    snail.append({lines - 1: i})
                for i in x:
                    snail.append({i: tmp})
                lines -= 1
                tmp = tmp + 1
            if self.puzzle_dimension % 2 == 1:
                snail.append({stop: stop})
            snail.reverse()
            return snail

        def check(self, k, a, l, c):
            '''Function to check neighbors of the current puzzle piece.'''
            # check the puzzle table for pieces around the current piece of puzzle
            # and determines the piece that fits best

            # check the pieces of puzzle around the current piece
            neigbors = []
            contor = 0
            # Allow for odd puzzles by converted all floats to integers
            c = int(c)
            l = int(l)
            # east
            graph = self.graph.to_undirected()
            if c < self.puzzle_dimension - 1 and self.puzzle[l][c + 1] != "*":
                neigbors.extend(graph.adjacency_list()[graph.nodes().index(self.puzzle[l][c + 1])])
                contor += 1
            # west
            if c > 0 and self.puzzle[l][c - 1] != "*":
                neigbors.extend(graph.adjacency_list()[graph.nodes().index(self.puzzle[l][c - 1])])
                contor += 1
            # north
            if l > 0 and self.puzzle[l - 1][c] != "*":
                neigbors.extend(graph.adjacency_list()[graph.nodes().index(self.puzzle[l - 1][c])])
                contor += 1
            # south
            if l < self.puzzle_dimension - 1 and self.puzzle[l + 1][c] != "*":
                neigbors.extend(graph.adjacency_list()[graph.nodes().index(self.puzzle[l + 1][c])])
                contor += 1

            possible_nodes = []
            if contor == 0:
                # there are no pieces of puzzle around
                return k[0]
            elif contor == 1:
                # there is nust one piece of puzzle around
                possible_nodes.extend(neigbors)
            else:
                # there are multiple pieces of puzzle around
                set_of_neighbors = set(neigbors)
                for node in set_of_neighbors:
                    if neigbors.count(node) == contor:
                        possible_nodes.append(node)

            # remove from the possible pieces of puzzle the ones already present in the puzzle
            for node in a:
                if node in possible_nodes:
                    possible_nodes.remove(node)

            if possible_nodes == []:
                # no solution could be found
                return "*"
            else:
                # there are multiple solutions of a puzzle piece
                # we choose the one with the highest page_rank
                tmp = "*"
                min = 100000
                for node in possible_nodes:
                    if node in k and k.index(node) < min:
                        min = k.index(node)
                        tmp = node
                return tmp

        def create_puzzle(self):
            '''Function used to create puzzle file from all of the pieces.'''
            self.puzzle = [["*" for i in range(self.puzzle_dimension)] for j in range(self.puzzle_dimension)] # pylint: disable=line-too-long
            # get all the paragraphs together in one text
            tmp_vector, self.lecture_title = self.nlp_pipeline()
            list_of_words = []
            for i in tmp_vector:
                list_of_words.extend(i)
            self.text_to_graph(list_of_words)  # the graph of words
            road = self.snail_road()  # the snail road inside the matrix
            page = nx.pagerank(self.graph)
            keywords = sorted(page, key=page.get, reverse=True)
            added_keywords = []  # keywords already added in the puzzle
            for location in road:
                line = int(list(location.keys())[0])
                column = int(list(location.values())[0])
                name = self.check(keywords, added_keywords, line, column)
                if name != "*":
                    keywords.remove(name)
                    added_keywords.extend(name)
                self.puzzle[line][column] = name

        def write_to_file(self, file_path):
            '''Function that writes puzzle to a file.'''
            file = open(file_path, "a")
            file.write(self.lecture_title + '-' + str(self.puzzle_dimension) + ":\n")
            for i in range(self.puzzle_dimension):
                for j in range(self.puzzle_dimension):
                    text = self.puzzle[i][j]
                    specification = []
                    # west
                    if j > 0:
                        if self.puzzle[i][j - 1] != "*":
                            if self.graph.has_edge(self.puzzle[i][j], self.puzzle[i][j - 1]):
                                if self.graph.has_edge(self.puzzle[i][j - 1], self.puzzle[i][j]):
                                    self.graph.remove_edge(self.puzzle[i][j - 1], self.puzzle[i][j])
                                specification.append("up")
                            else:
                                specification.append("down")
                        else:
                            specification.append("up")
                    else:
                        specification.append("")
                    # south
                    if i < self.puzzle_dimension - 1:
                        if self.puzzle[i + 1][j] != "*":
                            if self.graph.has_edge(self.puzzle[i][j], self.puzzle[i + 1][j]):
                                if self.graph.has_edge(self.puzzle[i + 1][j], self.puzzle[i][j]):
                                    self.graph.remove_edge(self.puzzle[i + 1][j], self.puzzle[i][j])
                                specification.append("up")
                            else:
                                specification.append("down")
                        else:
                            specification.append("up")
                    else:
                        specification.append("")
                    # east
                    if j < self.puzzle_dimension - 1:
                        if self.puzzle[i][j + 1] != "*":
                            if self.graph.has_edge(self.puzzle[i][j], self.puzzle[i][j + 1]):
                                if self.graph.has_edge(self.puzzle[i][j + 1], self.puzzle[i][j]):
                                    self.graph.remove_edge(self.puzzle[i][j + 1], self.puzzle[i][j])
                                specification.append("up")
                            else:
                                specification.append("down")
                        else:
                            specification.append("up")
                    else:
                        specification.append("")
                    # north
                    if i > 0:
                        if self.puzzle[i - 1][j] != "*":
                            if self.graph.has_edge(self.puzzle[i][j], self.puzzle[i - 1][j]):
                                if self.graph.has_edge(self.puzzle[i - 1][j], self.puzzle[i][j]):
                                    self.graph.remove_edge(self.puzzle[i - 1][j], self.puzzle[i][j])
                                specification.append("up")
                            else:
                                specification.append("down")
                        else:
                            specification.append("up")
                    else:
                        specification.append("")
                    file.write(str(text.encode('utf-8', errors='ignore')) + "#")
                    for spec in specification:
                        file.write(spec + "#")
                    file.write(" ")
                file.write("\n")


    DEBUG = True
    input_dir_name = "in"
    output_dir_name = "out"
    log_file_name = "CourseInterpreter.log"
    wrk_dir = os.getcwd() + '\\edunet\\utils'
    print(wrk_dir)
    input_dir = os.path.join(wrk_dir, input_dir_name)
    output_dir = os.path.join(wrk_dir, output_dir_name)
    log_file = os.path.join(wrk_dir, log_file_name)


    def log(log_message, log_file):
        timeinfo = str(datetime.now())
        message = timeinfo + " : " + log_message
        if DEBUG is True:
            print(message)
        if os.path.exists(log_file) and os.path.isfile(log_file):
            try:
                logfile = open(log_file, "a+")
                logfile.write(message)
                logfile.close()
            except:
                print("Can NOT write in log file: {}".format(log_file))


    def initial_operations():
        # log operations
        if os.path.exists(log_file) is False:
            try:
                logfile = open(log_file, "w")
                logfile.write("Log file created")
                logfile.close()
            except:
                print("Can NOT create the log file: {}".format(log_file))

        # input dir operations
        if os.path.exists(input_dir) is True:
            log("Input directory created: {}".format(input_dir), log_file)
        else:
            try:
                os.makedirs(input_dir)
            except OSError as error:
                log("Can NOT create input directory: {}".format(error), log_file)
                return False

        # output dir operations
        if os.path.exists(output_dir) is True:
            log("Output directory created: {}".format(output_dir), log_file)
        else:
            try:
                os.makedirs(output_dir)
            except OSError as error:
                log("Can NOT create output directory: {}".format(error), log_file)
                return False

        return True


    def get_course():
        global COURSE_DIR

        #check the url to be from yale
        link_splitted = link.split("/")
        if "openmedia.yale.edu" not in link:
            log("Only courses from openmedia.yale.edu are supported, exiting", log_file)
            return False

        course_name = link_splitted[-3]
        course_zip_name = link_splitted[-1]

        downloaded_file = os.path.join(input_dir, course_zip_name)
        if os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
                log("Zip archive of the course {} already existed at {}, removed it".format(course_name, downloaded_file), log_file) # pylint: disable=line-too-long
            except:
                log("Can not remove previous zip file {}, please do it manually".format(downloaded_file), log_file) # pylint: disable=line-too-long

        try:
            wget.download(link, out=downloaded_file)
            if os.path.exists(downloaded_file):
                log("Downloaded the course at link: {}, at {}".format(link, downloaded_file), log_file) # pylint: disable=line-too-long
            else:
                log("Can NOT download the course at link: {}".format(link), log_file)
                return False
        except:
            log("Can NOT download the course at link: {}".format(link), log_file)
            return False

        # unzip file and create course directory
        COURSE_DIR = os.path.join(input_dir, course_name)
        if os.path.exists(COURSE_DIR) and os.path.isdir(COURSE_DIR):
            shutil.rmtree(COURSE_DIR)
            log("Course directory {} already exists at {}, removed it.".format(course_name, COURSE_DIR), log_file) # pylint: disable=line-too-long

        with zipfile.ZipFile(downloaded_file, "r") as zip_ref:
            zip_ref.extractall(COURSE_DIR)
            if os.path.exists(COURSE_DIR) is False or os.path.isdir(COURSE_DIR) is False:
                log("Can NOT unzip {} at {}".format(downloaded_file, COURSE_DIR), log_file)
                return False, None
            else:
                log("Unzipped {} at {}".format(downloaded_file, COURSE_DIR), log_file)

        try:
            os.remove(downloaded_file)
            log("Removed downloaded ziped course {}".format(downloaded_file), log_file)
        except:
            log("Can NOT remove downloaded zip course {}".format(downloaded_file), log_file)
            return False, None

        return True, course_name


    def get_transcript_file(course_name):
        # Check the course structure
        #transcripts_dir_path = "**/transcripts"
        transcripts_dir_path = "**\\transcripts"
        if transcript:
            if transcript < 10:
                transcript_file_pattern = "transcript0{}.html".format(transcript)
            else:
                transcript_file_pattern = "transcript{}.html".format(transcript)
        else:
            transcript_file_pattern = "*.html"
        transcripts_path = os.path.join(input_dir, course_name, transcripts_dir_path, transcript_file_pattern) # pylint: disable=line-too-long
        transcripts = glob.glob(transcripts_path, recursive=True)
        if len(transcripts) > 0:
            log("Found transcripts {}".format(transcripts), log_file)
        else:
            log("Can NOT find any transcript as per specification {}".format(transcripts_path), log_file) # pylint: disable=line-too-long

        #remove duplicates
        non_duplicate_transcripts = []
        for ti in range(len(transcripts)):
            duplicate_found = False
            tj_start = ti + 1
            for tj in range(tj_start, len(transcripts)):
                if os.path.basename(transcripts[ti]) == os.path.basename(transcripts[tj]):
                    duplicate_found = True
                    break
            if duplicate_found is False:
                non_duplicate_transcripts.append(transcripts[ti])

        log("After duplicate removal, the following transcripts remain {}".format(non_duplicate_transcripts), log_file) # pylint: disable=line-too-long
        return non_duplicate_transcripts


    def process_transcripts(transcripts, course_name):
        for transcript in transcripts:
            # transcript_name = transcript.split("/")[-1][:-5] # for mac
            transcript_name = transcript.split("\\")[-1][:-5] # for windows
            log("Processing lecture {}".format(transcript_name), log_file)

            course_output_path = os.path.join(output_dir, course_name)
            if os.path.exists(course_output_path) is False:
                try:
                    os.makedirs(course_output_path)
                except:
                    log("Can not create lecture output directory {}".format(course_output_path), log_file) # pylint: disable=line-too-long
                    return False

            tree_name = "Tree#" + transcript_name + ".txt"
            tree_output_path = os.path.join(course_output_path, tree_name)
            lz = TreeOfKnowledge(keywords_paragraph, keywords_lecture, transcript_name, transcript)
            lz.analysis()
            lz.write_to_file(tree_output_path)

            puzzle_name = "Puzzle#" + transcript_name + ".txt"
            puzzle_output_path = os.path.join(course_output_path, puzzle_name)
            lz = PuzzleOfKnowledge(transcript_name, transcript, puzz_dim)
            lz.create_puzzle()
            lz.write_to_file(puzzle_output_path)

        return True


    if initial_operations():
        log("Initial operations finished with success", log_file)
        course_acquired, course_name = get_course()
        if course_acquired is True:
            transcripts = get_transcript_file(course_name)
            if len(transcripts) > 0:
                processing_success = process_transcripts(transcripts, course_name)
                if processing_success is True:
                    log("Processing successful", log_file)
                else:
                    log("Processing NOT successful", log_file)
    else:
        log("Initial operations could not be done, exiting.", log_file)
