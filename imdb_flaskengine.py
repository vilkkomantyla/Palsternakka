import imdb_data
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk import PunktSentenceTokenizer

#Initialize Flask instance
app = Flask(__name__)

data = imdb_data.main()

def stem_summaries():
    summaries = [movie["Summary"] for movie in data]
    stemmer = PorterStemmer()                       # Stemmer
    stemmed_summaries = []                               # Stemmed summaries
    for summary in summaries:                           # Go through every summary
        token_words = word_tokenize(summary)            # Tokenize every word
        stem_words = []                             # One document tokenized
        for word in token_words:                    # Go through every word in tokenized words
            stem_words.append(stemmer.stem(word))   # Append stemmed word into summary
            stem_words.append(" ")                  # White spaces between the words
        stemmed_summaries.append("".join(stem_words))    # Convert list of stemmed words into string and append it to stemmed summaries
    return stemmed_summaries

stemmed_summaries = stem_summaries()

# Stem the keyword query
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

# stemmed tfv object
tfv_stemmed = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_td_matrix_tfv_stemmed = tfv_stemmed.fit_transform(stemmed_summaries).T.tocsr()

# stemmed cv object
cv_stemmed = CountVectorizer(lowercase=True, binary=True, token_pattern=r"(?u)\b\w+\b")
sparse_td_matrix_binary_stemmed = cv_stemmed.fit_transform(stemmed_summaries).T.tocsr()
t2i_cv_stemmed = cv_stemmed.vocabulary_

# Functions to find matching movies:

def findResultsActor(query):
    titles = []
    for movie in data:
        lower_case_actors = [actor.lower() for actor in movie["Actors"]]
        for actor in lower_case_actors:
            if query.lower() in actor:
                titles.append(movie["Title"])
                break
    result_summary = [f"There are {len(titles)} matches"]
    return titles, result_summary

def findResultsGenre(query):
    titles = []
    for movie in data:
        lower_case_genres = [genre.lower() for genre in movie["Genres"]]
        if query.lower() in lower_case_genres:
            titles.append(movie["Title"])
    result_summary = [f"There are {len(titles)} matches"]
    return titles, result_summary

def findResultsYear(query):
    titles = []
    for movie in data:
        if query == movie["Year"]:
            titles.append(movie["Title"])
    result_summary = [f"There are {len(titles)} matches"]
    return titles, result_summary

def findResultsTitle(query):
    titles = []
    for movie in data:
        if query.lower() == movie["Title"].lower():
            titles.append(movie["Title"])
    result_summary = [f"There are {len(titles)} matches"]
    return titles, result_summary

def checkForBooleans(query):
    if ("AND" in query) or ("OR" in query) or ("NOT" in query):
        return booleanSearch(query)
    else:
        return rankingSearch(query)

d = {"AND": "&",            # all tokens in documents are lowercased, so "and" means the token "and" in a document, and capital "AND" means the operator '&'
     "OR": "|",
     "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def rewrite_token(t):
    if t in d:      # if token is AND OR NOT operator
        return d[t]
    t = stem_token(t)
    if t in t2i_cv_stemmed:
        return 'sparse_td_matrix_binary_stemmed[t2i_cv_stemmed["{:s}"]].todense()'.format(t)
    else:
        return 'UNKNOWN'        #  if the token is not found in the docum   ents

def booleanSearch(query):   # for keyword searches with booleans
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
            word_before_AND = re.match(r'("?\w+"?) AND', query)     # Creating a match object of the query and capturing the word before AND
            if rewrite_token(word_before_AND.groups()[0]) == "UNKNOWN":        # if the captured word before AND is UNKNOWN
                hits_list = []                                  # no documents will match (because of AND)
            else:                                               # if we end up in this block, the word after NOT must be unknown, e.g. cat AND NOT someunknownword
                hits_matrix = eval(rewrite_query(word_before_AND.groups()[0]))  # word_before_AND alone defines the matching documents
                hits_list = list(hits_matrix.nonzero()[1])

    matches = []

    result_summary = ["There are " + str(len(hits_list)) + " matching movies"]

    for i, summary_idx in enumerate(hits_list):
        movie_title = data[summary_idx]["Title"]
        summary = data[summary_idx]["Summary"]
        summary = summary[summary.find(">")+1:]
        matches.append("Matching movie #{:d}:".format(i))
        matches.append(movie_title)
        matches.append(summary)
    return matches, result_summary


def rankingSearch(query):   # for keyword searches without booleans
    stemmed_query = stem_query(query)   

    # Vectorize query string
    query_vec = tfv_stemmed.transform([stemmed_query]).tocsc()      # Using TfidfVectorizer on stemmed query string
    # Cosine similarity
    hits = np.dot(query_vec, sparse_td_matrix_tfv_stemmed)

    try:
        ranked_hits_and_summary_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)

        result_summary = ["Your query '{:s}' matched {:d} movies:".format(query, len(ranked_hits_and_summary_ids))]
        matches = []
        for hits, i in ranked_hits_and_summary_ids:
            movie_title = data[i]["Title"]
            summary = data[i]["Summary"]
            summary = summary[summary.find(">")+1:]
            score = "{:.4f}".format(hits)
            matches.append(movie_title)
            matches.append(summary)
            matches.append(f"Relevance ranking: {score}")
            # matches.append("Score of \"" + query + "\" is {:.4f} in movie {:s}: {:s}".format(hits, movie_title, summary))
            
    except IndexError:      # only unknown words in query
        result_summary = None
        matches = ["No matching documents"]
    
    return matches, result_summary

@app.route('/search')
def search():
    query = request.args.get('query')
    matches = []
    result_summary = ""
    if query:
        if request.args.get('engine') == "keyword":
            matches, result_summary = checkForBooleans(query)        
        elif request.args.get('engine') == "genre":
            matches, result_summary = findResultsGenre(query)
        elif request.args.get('engine') == "actor":
            matches, result_summary = findResultsActor(query)
        elif request.args.get('engine') == "year":
            matches, result_summary = findResultsYear(query)
        elif request.args.get('engine') == "title":
            matches, result_summary = findResultsTitle(query)
    return render_template('index_uusi.html', matches=matches, result_summary=result_summary)

