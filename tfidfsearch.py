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

# Stem the query
def stem_query(query):
    stemmer = PorterStemmer()
    query_stemmed = stemmer.stem(query)
    return query_stemmed

stemmed_documents = stem_documents()

tfv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")   # queries WITHOUT boolean operators
sparse_matrix_tfv = tfv.fit_transform(stemmed_documents)
sparse_td_matrix_tfv = sparse_matrix_tfv.T.tocsr()

cv = CountVectorizer(lowercase=True, binary=True, token_pattern=r"(?u)\b\w+\b") # queries WITH boolean operators
sparse_matrix_binary = cv.fit_transform(stemmed_documents)
sparse_td_matrix_binary = sparse_matrix_binary.T.tocsr()


terms = cv.get_feature_names_out()

t2i = cv.vocabulary_  # shorter notation: t2i = term-to-index

d = {"AND": "&",            # all tokens in documents are lowercased, so "and" means the token "and" in a document, and capital "AND" means the operator '&'
     "OR": "|",
     "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_query(query): # rewrite every token in the stemmed query
    if "\"" not in query: 
        query = stem_query(query)
    return " ".join(rewrite_token(t) for t in query.split())

def test_query(query):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query))
    print("Matching:", eval(rewrite_query(query))) # Eval runs the string as a Python command
    print()

def rewrite_token(t):
    if (t not in d) and (t not in t2i):     # if the token is not found in the documents
        return 'UNKNOWN'
    else:
        return d.get(t, 'sparse_td_matrix_binary[t2i["{:s}"]].todense()'.format(t)) # Make retrieved rows dense
    


# Perform the queries on the documents and print the contents of the matching documents

def printContents(query):       # for matching approach
    if "\"" not in query:
        query = stem_query(query)
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

    counter = 0      # A counter to make sure that no more than five documents are printed (even if there were more matches)
    for i, doc_idx in enumerate(hits_list):
        if counter < 5:
            print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx][:500]))       # only print the first 500 characters of each document
            counter += 1
    print()

def printContentsRanked(query):     # for ranking approach (tfidf)
    if "\"" not in query:
        query = stem_query(query)

    # Vectorize query string
    query_vec = tfv.transform([query]).tocsc()     # Using TfidfVectorizer on query string

    # Cosine similarity
    hits = np.dot(query_vec, sparse_td_matrix_tfv)

    # Rank hits
    ranked_hits_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)

    # Output result
    print("\nYour query '{:s}' matched the following {:d} documents, ranked highest relevance first:\n".format(query, len(ranked_hits_and_doc_ids)))
    for hits, i in ranked_hits_and_doc_ids:
        print("Score of \"" + query + "\" is {:.4f} in document: {:s}".format(hits, documents[i][15:100]))
        print()

    '''
    hits_list = np.array(hits_matrix)[0]
    hits_and_doc_ids = [ (hits, i) for i, hits in enumerate(hits_list) if hits > 0 ]
    ranked_hits_and_doc_ids = sorted(hits_and_doc_ids, reverse=True)
    '''

# Asking user for a query
def getquery():
    while True:
        query = input("Enter a search word or press enter to end the query.\n"
                      "AND, OR, NOT operators must be written in capitals,"
                      'for example "word1 OR word2".\n')
        if len(query) == 0:
            print("Thank you!") # Ends the program by thanking the user :)
            break
        if ("AND" or "NOT" or "OR") in query:
            printContents(query)        # Use boolean/binary engine (matching approach)
        else:
            printContentsRanked(query)  # Use tfidf engine (ranking approach)


# Runs the program
getquery()