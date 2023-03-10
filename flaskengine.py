# This is a search engine that utilizes Flask.

# Import CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk import PunktSentenceTokenizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, render_template, request
#Initialize Flask instance
app = Flask(__name__)


# Read the text from the Wikipedia file and divide it into articles
with open("static/wikipedia_documents.txt", encoding="utf8") as open_file:
    contents = open_file.read()
    documentList = contents.split("</article>")

documents = documentList

# Stem the documents
def stem_documents():
    stemmer = PorterStemmer()                       # Stemmer
    stemmed_docs = []                               # Stemmed documents
    for doc in documents:                           # Go through every document
        token_words = word_tokenize(doc)            # Tokenize every word
        stem_words = []                             # One document tokenized
        for word in token_words:                    # Go through every word in tokenized words
            stem_words.append(stemmer.stem(word))   # Append stemmed word into document
            stem_words.append(" ")                  # White spaces between the words
        stemmed_docs.append("".join(stem_words))    # Convert document (list) into string and append it to stemmed documents
    return stemmed_docs

stemmed_documents = stem_documents()

# Stem the query
def stem_query(query):    # works with multi word queries
    stemmer = PorterStemmer()
    token_words = word_tokenize(query)
    stem_words = []
    for token in token_words:
        stem_words.append(stemmer.stem(token))
    stemmed_query = (" ".join(stem_words))
    return stemmed_query

# Stem one token
def stem_token(token):
    stemmer = PorterStemmer()
    token_stemmed = stemmer.stem(token)
    return token_stemmed


# not stemmed / normal cv object
cv = CountVectorizer(lowercase=True, binary=True, token_pattern=r"(?u)\b\w+\b")
sparse_td_matrix_binary = cv.fit_transform(documents).T.tocsr()
t2i_cv = cv.vocabulary_

# stemmed cv object
cv_stemmed = CountVectorizer(lowercase=True, binary=True, token_pattern=r"(?u)\b\w+\b")
sparse_td_matrix_binary_stemmed = cv_stemmed.fit_transform(stemmed_documents).T.tocsr()
t2i_cv_stemmed = cv_stemmed.vocabulary_

# not stemmed / normal tfv object
tfv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_td_matrix_tfv = tfv.fit_transform(documents).T.tocsr()
#t2i_tfv = tfv.vocabulary_

# stemmed tfv object
tfv_stemmed = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_td_matrix_tfv_stemmed = tfv_stemmed.fit_transform(stemmed_documents).T.tocsr()
#t2i_tfv_stemmed = tfv_stemmed.vocabulary_


d = {"AND": "&",            # all tokens in documents are lowercased, so "and" means the token "and" in a document, and capital "AND" means the operator '&'
     "OR": "|",
     "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def test_query(query):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query))
    print("Matching:", eval(rewrite_query(query))) # Eval runs the string as a Python command
    print()

def rewrite_token(t):
    if t in d:      # if token is AND OR NOT operator
        return d[t]

    if "\"" in t:   # word surrounded by quotes / exact match wanted
        t = t[1:-1] # remove surrounding quotes
        if t in t2i_cv:
            return 'sparse_td_matrix_binary[t2i_cv["{:s}"]].todense()'.format(t)
        else:
            return 'UNKNOWN'        #  if the token is not found in the documents
    else:       # no quotes, look at the stemmed vocabulary
        t = stem_token(t)
        if t in t2i_cv_stemmed:
            return 'sparse_td_matrix_binary_stemmed[t2i_cv_stemmed["{:s}"]].todense()'.format(t)
        else:
            return 'UNKNOWN'        #  if the token is not found in the documents
    


# Perform the queries on the documents and print the contents of the matching documents

def printContents(query):       # for matching approach
    if 'UNKNOWN' not in rewrite_query(query):         # if everything is normal and all the words of the query are found in the documents
        hits_matrix = eval(rewrite_query(query))
        hits_list = list(hits_matrix.nonzero()[1])
    else:                                             # if there is at least one unknown word in the query        
        # In the next block UNKNOWN words in the query do not affect the final search results because the words are separated by OR.
        # If there is at least one word in the query that is NOT unknown, the known words will determine the matching documents       
        if re.match(r'\w+( OR \w+)+$', query):          # the query consists of tokens separated by OR, e.g. "word1 OR word2 OR word3"
            known_words = []                #this list will contain all the KNOWN words in user's query
            for token in query.split(' OR '):       
                if rewrite_query(token) != 'UNKNOWN':       # if the word is found in the documents, 
                    known_words.append(token)                   # it will be appended to the list of KNOWN words
            stripped_query = " | ".join(rewrite_token(t) for t in known_words)       # the new query will be stripped of unknown words
            if len(known_words) == 0:    # if all the words in the query are unknown...
                hits_list = []              # there won't be any matches
            else:
                hits_matrix = eval(stripped_query)      # here the known words in the query will be evaluated as usual
                hits_list = list(hits_matrix.nonzero()[1])
        elif re.match(r'NOT \w+$', query):      # will match queries like "NOT word"
            print(query)
            hits_list = []
            for i in range(100):
                hits_list.append(i)
        elif re.match(r'\w+( AND \w+)*$', query):    # the query consists of tokens separated by AND  (this block will also handle the case of only one unknown word!)
            hits_list = []      # AND operator requires that all words be known so there can never be matches if one word is unknown
        elif re.match(r'"?\w+"? AND NOT "?\w+"?$', query):  # e.g. cat AND NOT dog, but at least one of the words is UNKNOWN
            print("matched")
            word_before_AND = re.match(r'("?\w+"?) AND', query)     # Creating a match object of the query and capturing the word before AND
            #print(word_before_AND.groups()[0])
            if rewrite_token(word_before_AND.groups()[0]) == "UNKNOWN":        # if the captured word before AND is UNKNOWN
                hits_list = []                                  # no documents will match (because of AND)
            else:                                               # if we end up in this block, the word after NOT must be unknown, e.g. cat AND NOT someunknownword
                hits_matrix = eval(rewrite_query(word_before_AND.groups()[0]))  # word_before_AND alone defines the matching documents
                hits_list = list(hits_matrix.nonzero()[1])

    matches = []

    result_summary = ["There are " + str(len(hits_list)) + " matching documents"]

    counter = 0      # A counter to make sure that no more than five documents are printed (even if there were more matches)
    for i, doc_idx in enumerate(hits_list):
        if counter < 5:
            matches.append("Matching doc #{:d}: {:s}".format(i, documents[doc_idx][:500]))       # only print the first 500 characters of each document
            counter += 1
    print()
    return matches, result_summary

def printContentsRanked(query):     # For ranking approach (tfidf)
    if "\"" not in query:           # Choose the stemming method
        stemmed_query = stem_query(query)   

        # Vectorize query string
        query_vec = tfv_stemmed.transform([stemmed_query]).tocsc()      # Using TfidfVectorizer on stemmed query string
        # Cosine similarity
        hits = np.dot(query_vec, sparse_td_matrix_tfv_stemmed)
        stemmed = True
    else:
        # Vectorize query string
        query_vec = tfv.transform([query]).tocsc()          # Use original/unstemmed query
        # Cosine similarity
        hits = np.dot(query_vec, sparse_td_matrix_tfv)
        # Remove the surrounding quotes
        query = query[1:-1]
        stemmed = False
        
    # Rank hits and print results
    try:
        ranked_hits_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
        
        matches = []

        # Output result

        plt.figure()    # creating empty bar chart
        plt.title('Most relevant documents')
        names = []      # will contain article names to be shown in the bar chart
        values = []     # will contain corresponding tfidf-scores to be shown in the bar chart
        
        result_summary = ["Your query '{:s}' matched {:d} documents.\n".format(query, len(ranked_hits_and_doc_ids)),
                          "Printing the first ten documents, ranked highest relevance first:"]
        count = 0
        for hits, i in ranked_hits_and_doc_ids:
            if count < 10:
                if stemmed:
                    for token in word_tokenize(documents[i].lower()):
                        if stem_token(token) == stemmed_query.lower():
                            part = documents[i].lower().find(token)
                            break
                else:
                    part = re.search(r"\W" + query.lower() + r"\W", documents[i].lower()).start()
                name_start= documents[i].find("\"")
                name_end = documents[i].find(">")
                article_name = documents[i][name_start:name_end]
                matches.append("Score of \"" + query + "\" is {:.4f} in document {:s}: ... {:s} ... ".format(hits, article_name, documents[i][part-50:part+50]))
                names.append(article_name)
                values.append(hits)
            count += 1
            
        plt.bar(names[:5], values[:5])  # creating bar chart with article names and corresponding tfidf scores
        plt.savefig('static/bar_chart.png')
        
    except IndexError:      # only unknown words in query
        result_summary = None
        matches = ["No matching documents"]
    return matches, result_summary


@app.route('/')
def hello_world():
   return "Hello, World!"

@app.route('/search')
def search():
    query = request.args.get('query')
    matches = []
    result_summary = ""
    if query:
        if request.args.get('engine') == "boolean":
            matches, result_summary = printContents(query)        # Use boolean/binary engine (matching approach)
        elif request.args.get('engine') == "ranking":
            matches, result_summary = printContentsRanked(query)  # Use tfidf engine (ranking approach)

    #Render index.html with matches variable
    return render_template('index.html', matches=matches, result_summary=result_summary)

