from datetime import datetime

from bs4 import BeautifulSoup
import nltk as nl
import networkx as nx
import os
import wget
import zipfile
import shutil
import glob

def course_processor(link, keywords_paragraph, keywords_lecture, transcript=None):

    wnl = nl.WordNetLemmatizer()

    class Lecture:

        def __init__(self, path, name):
            self.name = name
            self.path = path
            self.graph = nx.DiGraph()

        def nlp_pipeline(self):
            """Passes a document through html parsing, and nlp pipeline and returns a list of nouns"""
            # file_in = open(self.path)
            file_in = open(self.path, encoding='utf-8')
            soup = BeautifulSoup(file_in, "html.parser")  # parse html
            soup_paragraphs = soup.find_all('p')  # retrieve all paragraphs
            list_of_nouns = []  # the resulting list of nouns

            # each paragraph is parsed through nlp pipeline
            for paragraph in soup_paragraphs[:-3]:  # the last three vector are null respective [end,of,transcript]
                text = paragraph.getText()

                # Tokenization
                tokens = nl.word_tokenize(text, language="english")
                for t in tokens:
                    if t.isalpha() == 0:
                        tokens.remove(t)

                # POS tagginng filtering for NOUNS
                text_pos = nl.pos_tag(tokens)
                tokens_pos = []
                for tp in text_pos:
                    if tp[1][0:2] == "NN" or tp[0] == ".":
                        try:
                            tokens_pos.append(tp[0])
                        except:
                            tokens_pos(tp[0])

                # lemmatization
                lemmas = []
                for s in tokens_pos:
                    try:
                        lemmas.append(wnl.lemmatize(s))
                    except:
                        lemmas.append(s)

                # lower casing
                paragraph_nouns = [w.lower() for w in lemmas]  # list of nouns per paragraph
                list_of_nouns.append(paragraph_nouns)

            return list_of_nouns  # return the list of nouns per document

        def text_to_graph(self, list_of_words):
            if list_of_words != []:
                self.graph.add_node(list_of_words[0])
                for i in range(1, len(list_of_words)):
                    self.graph.add_node(list_of_words[i])
                    self.graph.add_edge(list_of_words[i - 1], list_of_words[i], weight=1)
                if self.graph.has_node("."):
                    self.graph.remove_node(".")


    class TreeOfKnowledge(Lecture):

        def __init__(self, paragraph_dimension, lecture_dimension, name, path):
            self.name = name
            self.path = path
            self.paragraph_dimension = paragraph_dimension
            self.lecture_dimension = lecture_dimension
            self.lecture_keywords = []
            self.lecture_keywords_per_paragraph = {}
            self.graph = nx.DiGraph()

        def add_lecture_keywords(self, keywords):
            self.lecture_keywords.extend(keywords)

        def add_lecture_keywords_per_paragraph(self, paragraph, keywords):
            self.lecture_keywords_per_paragraph[paragraph] = keywords

        def analysis(self):
            lecture_words = []
            words = self.nlp_pipeline()
            paragraph_counter = 0
            for w in words:
                paragraph_counter += 1
                lecture_words.extend(w)
                self.text_to_graph(w)
                ranked_words = nx.pagerank(self.graph)
                self.graph = nx.DiGraph()
                paragraph_keywords = sorted(ranked_words, key=ranked_words.get, reverse=True)[:self.paragraph_dimension]
                self.add_lecture_keywords_per_paragraph(paragraph_counter, paragraph_keywords)
            self.text_to_graph(lecture_words)
            ranked_words = nx.pagerank(self.graph)
            lecture_keywords = sorted(ranked_words, key=ranked_words.get, reverse=True)[:self.lecture_dimension]
            self.add_lecture_keywords(lecture_keywords)

        def write_to_file(self, file):
            f = open(file, "w")
            f.write("\n" + self.name + ":")
            for k in self.lecture_keywords:
                f.write(str(k) + " ")
            for paragraph in self.lecture_keywords_per_paragraph.keys():
                f.write("\n--------" + str(paragraph) + " paragraph: ")
                for k in self.lecture_keywords_per_paragraph[paragraph]:
                    f.write(str(k.encode('utf-8', errors='ignore')) + " ")
            f.close()


    class PuzzleOfKnowledge(Lecture):

        def __init__(self, name, path, puzzle_dimension):
            self.name = name
            self.path = path
            self.puzzle_dimension = puzzle_dimension
            self.graph = nx.DiGraph()

        def snail_road(self):
            # Input nr of lines in a lines x linex matrix
            # Output an ordered vector with the snail path of the matrix
            # each element of the vector is a dictionary where key is repsents the line and value represents the column

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
                x = range(tmp + 1, lines)
                x.reverse()
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
            # check the puzzle table for pieces around the current piece of puzzle and determines the piece that
            # fits best

            # check the pieces of puzzle around the current piece
            neigbors = []
            contor = 0
            # east
            g = self.graph.to_undirected()
            if c < self.puzzle_dimension - 1 and self.puzzle[l][c + 1] != "*":
                neigbors.extend(g.adjacency_list()[g.nodes().index(self.puzzle[l][c + 1])])
                contor += 1
            # west
            if c > 0 and self.puzzle[l][c - 1] != "*":
                neigbors.extend(g.adjacency_list()[g.nodes().index(self.puzzle[l][c - 1])])
                contor += 1
            # north
            if l > 0 and self.puzzle[l - 1][c] != "*":
                neigbors.extend(g.adjacency_list()[g.nodes().index(self.puzzle[l - 1][c])])
                contor += 1
            # south
            if l < self.puzzle_dimension - 1 and self.puzzle[l + 1][c] != "*":
                neigbors.extend(g.adjacency_list()[g.nodes().index(self.puzzle[l + 1][c])])
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

            self.puzzle = [["*" for i in range(self.puzzle_dimension)] for j in range(self.puzzle_dimension)]
            # get all the paragraphs together in one text
            tmp_vector = self.nlp_pipeline()
            list_of_words = []
            for i in tmp_vector:
                list_of_words.extend(i)
            self.text_to_graph(list_of_words)  # the graph of words
            road = self.snail_road()  # the snail road inside the matrix
            page = nx.pagerank(self.graph)
            keywords = sorted(page, key=page.get, reverse=True)
            added_keywords = []  # keywords already added in the puzzle
            for location in road:
                line = location.keys()[0]
                column = location.values()[0]
                name = self.check(keywords, added_keywords, line, column)
                if name != "*":
                    keywords.remove(name)
                    added_keywords.extend(name)
                self.puzzle[line][column] = name

        def write_to_file(self, file):
            f = open(file, "a")
            f.write(str(self.puzzle_dimension) + "\n")
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

                    f.write(text + "#")
                    for s in specification:
                        f.write(s + "#")
                    f.write(" ")
                f.write("\n")


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
        if DEBUG == True:
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
        if os.path.exists(log_file) == False:
            try:
                logfile = open(log_file, "w")
                logfile.write("Log file created")
                logfile.close()
            except:
                print("Can NOT create the log file: {}".format(log_file))

        # input dir operations
        if os.path.exists(input_dir) == True:
            log("Input directory created: {}".format(input_dir), log_file)
        else:
            try:
                os.makedirs(input_dir)
            except OSError as e:
                log("Can NOT create input directory: {}".format(e), log_file)
                return False

        # output dir operations
        if os.path.exists(output_dir) == True:
            log("Output directory created: {}".format(output_dir), log_file)
        else:
            try:
                os.makedirs(output_dir)
            except OSError as e:
                log("Can NOT create output directory: {}".format(e), log_file)
                return False

        return True


    def get_course():
        global course_dir

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
                log("Zip archive of the course {} already existed at {}, removed it".format(course_name, downloaded_file),
                    log_file)
            except:
                log("Can not remove previous zip file {}, please do it manually".format(downloaded_file))

        try:
            wget.download(link, out=downloaded_file)
            if os.path.exists(downloaded_file):
                log("Downloaded the course at link: {}, at {}".format(link, downloaded_file), log_file)
            else:
                log("Can NOT download the course at link: {}".format(link), log_file)
                return False
        except:
            log("Can NOT download the course at link: {}".format(link), log_file)
            return False

        # unzip file and create course directory
        course_dir = os.path.join(input_dir, course_name)
        if os.path.exists(course_dir) and os.path.isdir(course_dir):
            shutil.rmtree(course_dir)
            log("Course directory {} already exists at {}, removed it.".format(course_name, course_dir), log_file)

        with zipfile.ZipFile(downloaded_file, "r") as zip_ref:
            zip_ref.extractall(course_dir)
            if os.path.exists(course_dir) == False or os.path.isdir(course_dir) == False:
                log("Can NOT unzip {} at {}".format(downloaded_file, course_dir), log_file)
                return False, None
            else:
                log("Unzipped {} at {}".format(downloaded_file, course_dir), log_file)

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
        transcripts_path = os.path.join(input_dir, course_name, transcripts_dir_path, transcript_file_pattern)
        transcripts = glob.glob(transcripts_path, recursive=True)
        if len(transcripts) > 0:
            log("Found transcripts {}".format(transcripts), log_file)
        else:
            log("Can NOT find any transcript as per specification {}".format(transcripts_path), log_file)

        #remove duplicates
        non_duplicate_transcripts = []
        for ti in range(len(transcripts)):
            duplicate_found = False
            tj_start = ti + 1
            for tj in range(tj_start, len(transcripts)):
                if os.path.basename(transcripts[ti]) == os.path.basename(transcripts[tj]):
                    duplicate_found = True
                    break
            if duplicate_found == False:
                non_duplicate_transcripts.append(transcripts[ti])

        log("After duplicate removal, the following transcripts remain {}".format(non_duplicate_transcripts), log_file)
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
                    log("Can not create lecture output directory {}".format(course_output_path), log_file)
                    return False

            tree_name = "Tree#" + transcript_name + ".txt"
            tree_output_path = os.path.join(course_output_path, tree_name)
            lz = TreeOfKnowledge(keywords_paragraph, keywords_lecture, transcript_name, transcript)
            lz.analysis()
            lz.write_to_file(tree_output_path)

            '''
            puzzle_name = "Puzzle#" + transcript_name + ".txt"
            puzzle_output_path = os.path.join(course_output_path, puzzle_name)
            lz = PuzzleOfKnowledge(transcript_name, transcript, args.puzzle_dimension)
            lz.create_puzzle()
            lz.write_to_file(puzzle_output_path)
            '''

        return True


    if initial_operations():
        log("Initial operations finished with success", log_file)
        course_acquired, course_name = get_course()
        if course_acquired == True:
            transcripts = get_transcript_file(course_name)
            if len(transcripts) > 0:
                processing_success = process_transcripts(transcripts, course_name)
                if processing_success == True:
                    log("Processing successful", log_file)
                else:
                    log("Processing NOT successful", log_file)
    else:
        log("Initial operations could not be done, exiting.", log_file)
