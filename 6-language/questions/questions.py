import nltk
import sys
import os
import numpy as np

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    corpus = os.listdir(directory)
    files = dict()
    for data in corpus:
        if data[-4:] == '.txt':
            files[data] = open(f"{directory}{os.sep}{data}").read()
    #print(files)
    return files
            
def standarize_word(s):
    true_word = False
    ret_s = ""
    for w in s:
        if ord(w)>=ord("A") and ord(w)<=ord("Z"):
            ret_s = ret_s + chr(ord(w) - ord("A") + ord("a"))
            true_word = True
        elif ord(w)>=ord("a") and ord(w)<=ord("z"):
            ret_s = ret_s + w
            true_word = True
        else:
            ret_s = ret_s + w
    if true_word:
        return ret_s
    else:
        return None
            

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tk = nltk.tokenize.word_tokenize(document)
    ret = []
    for word in tk:
        s = standarize_word(word)
        if s is not None:
            ret.append(s)
    return ret


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    Ntotal = len(documents)
    idfs = dict()
    for doc in documents:
        word_check = set(documents[doc])
        for w in word_check:
            if w not in idfs:
                idfs[w] = 0
            idfs[w] +=1
    for w in idfs:
        idfs[w] = Ntotal/idfs[w]
        idfs[w] = np.log(idfs[w])
    return idfs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = dict()
    for f in files:
        Ntot = len(f)
        tf_idfs[f] = 0
        for w in set(query):
            if w in idfs:
                tf_idfs[f] += (files[f].count(w)/Ntot)*idfs[w]
    tf_idfs = sorted(tf_idfs.items(), key = lambda x: x[1], reverse = True)
    tf_idfs = [x[0] for x in tf_idfs[:n]]
    #print(tf_idfs)
    return tf_idfs
        


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    ret_sentences = dict()
    for s in sentences:
        ret_sentences[s] = 0
        for w in set(sentences[s]):
            if w in set(query):
                ret_sentences[s] += idfs[w]
        #print(s, ret_sentences[s])
        tmp = 0
        for w in set(query):
            tmp += sentences[s].count(w)
        tmp = tmp/len(sentences[s])
        ret_sentences[s] = (ret_sentences[s], tmp)
    #print(ret_sentences.items())
    ret_sentences = sorted(ret_sentences.items(), key = lambda x: x[1], reverse = True)
    #print(ret_sentences[:10])
    ret_sentences = [x[0] for x in ret_sentences[:n]]
    #print(ret_sentences)
    return ret_sentences

if __name__ == "__main__":
    main()
