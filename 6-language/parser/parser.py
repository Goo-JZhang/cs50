import nltk
import sys
import re
import string

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> S Conj S | NP VP | VP | 
AdjP -> Adj AdjP | Adv AdjP | Adj 
AdvP -> Adv AdvP | Adv
PP -> P NP
NP -> N | NP PP | Det NP | AdjP NP | NP Conj NP | N NP
VP -> V | AdvP VP | VP AdvP | VP PP | VP NP | VP Conj VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))

def wordStandarize(w):
    ret_w = ''
    true_word = False
    for alb in w:
        if ord(alb)<=ord('z') and ord(alb)>=ord('a'):
            ret_w = ret_w + alb
            true_word = True
        elif ord(alb)<=ord('Z') and ord(alb)>=ord('A'):
            ret_w = ret_w + chr(ord(alb) - ord('A') + ord('a'))
            true_word = True
        else:
            ret_w = ret_w + alb
    if true_word:
        return ret_w
    else:
        return None


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    tk_sentence = nltk.tokenize.word_tokenize(sentence)
    pro_sentence = []
    for word in tk_sentence:
        tmp = wordStandarize(word)
        if tmp is not None:
            pro_sentence.append(tmp)
    return pro_sentence
    
    
def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    ret_tree = []
    if len(tree.leaves()) == 1:
        if tree.label()!='NP':
            return []
        else:
            return tree
    if tree.label()!='NP':
        for subtree in tree:
            ret_tree.extend(np_chunk(subtree))
    else:
        if len(tree.leaves()) <=2:
            ret_tree.append(tree)
        else:
            for subtree in tree:
                ret_tree.extend(np_chunk(subtree))
    return ret_tree


if __name__ == "__main__":
    main()
