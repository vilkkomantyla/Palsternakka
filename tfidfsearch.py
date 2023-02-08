# This is the document for the search engine utilizing tf-idf (or boolean engine in case of boolean operators in the query)

# Import CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk import PunktSentenceTokenizer


# Read the text from the Wikipedia file and divide it into articles
with open("wikipedia_documents.txt", encoding="utf8") as open_file:
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

    print()
    print("There are", len(hits_list), "matching documents:")
    print()

    counter = 0      # A counter to make sure that no more than five documents are printed (even if there were more matches)
    for i, doc_idx in enumerate(hits_list):
        if counter < 5:
            print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx][:100]))       # only print the first 100 characters of each document
            print()
            counter += 1
    print()

def printContentsRanked(query):     # For ranking approach (tfidf)
    if "\"" not in query:           # Choose the stemming method
        stemmed_query = stem_query(query)   

        # Vectorize query string
        query_vec = tfv_stemmed.transform([stemmed_query]).tocsc()      # Using TfidfVectorizer on stemmed query string
        # Cosine similarity
        hits = np.dot(query_vec, sparse_td_matrix_tfv_stemmed)
    else:
        # Vectorize query string
        query_vec = tfv.transform([query]).tocsc()          # Use original/unstemmed query
        # Cosine similarity
        hits = np.dot(query_vec, sparse_td_matrix_tfv)
        
    # Rank hits and print results
    try:
        ranked_hits_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)

        # Output result
        print("\nYour query '{:s}' matched {:d} documents.\n".format(query, len(ranked_hits_and_doc_ids)))
        print("Printing the first ten documents, ranked highest relevance first:")
        print()

        count = 0
        for hits, i in ranked_hits_and_doc_ids:
            if count < 10:
            # part = documents[i].find(query)
            # print("Score of \"" + query + "\" is {:.4f} in document: {:s}".format(hits, documents[i][part-20:part+20]))
                print("Score of \"" + query + "\" is {:.4f} in document: {:s}".format(hits, documents[i][15:100]))
                print()
            count += 1

    except IndexError:      # only unknown words in query
         print("No matching documents\n")


# Asking user for a query
def getquery():
    while True:
        query = input("Enter a search word or press enter to end the query.\n"
                      "AND, OR, NOT operators must be written in capitals,"
                      'for example "word1 OR word2".\n'
                      "Using quotation will return exact matches, otherwise stemming will be used\n")
        if len(query) == 0:
            print("Thank you!") # Ends the program by thanking the user :)
            break
        if ("AND" in query) or ("OR" in query) or ("NOT" in query):
            printContents(query)        # Use boolean/binary engine (matching approach)
        else:
            printContentsRanked(query)  # Use tfidf engine (ranking approach)


# Runs the program
getquery()
