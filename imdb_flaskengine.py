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

# stemmed tfv object
tfv_stemmed = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_td_matrix_tfv_stemmed = tfv_stemmed.fit_transform(stemmed_summaries).T.tocsr()

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

def checkForBooleans(query):
    if ("AND" in query) or ("OR" in query) or ("NOT" in query):
        return booleanSearch(query)
    else:
        return rankingSearch(query)

def booleanSearch(query):   # for keyword searches with booleans
    return ["joopa"], ["joo"]

def rankingSearch(query):   # for keyword searches without booleans
    stemmed_query = stem_query(query)   

    # Vectorize query string
    query_vec = tfv_stemmed.transform([stemmed_query]).tocsc()      # Using TfidfVectorizer on stemmed query string
    # Cosine similarity
    hits = np.dot(query_vec, sparse_td_matrix_tfv_stemmed)

    try:
        ranked_hits_and_summary_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)

        result_summary = ["Your query '{:s}' matched {:d} documents.".format(query, len(ranked_hits_and_summary_ids))]
        matches = []
        for hits, i in ranked_hits_and_summary_ids:
            movie_title = data[i]["Title"]
            summary = data[i]["Summary"]
            matches.append("Score of \"" + query + "\" is {:.4f} in movie {:s}:\n{:s}".format(hits, movie_title, summary))
            
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
    return render_template('index_uusi.html', matches=matches, result_summary=result_summary)

