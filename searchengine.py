# This is the document for the search engine

# Import CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import re


# Read the text from the Wikipedia file and divide it into articles
with open("wikipedia_documents.txt", encoding="utf8") as open_file:
    contents = open_file.read()
    documentList = contents.split("</article>")

documents = documentList

             
cv = CountVectorizer(lowercase=True, binary=True, token_pattern=r"(?u)\b\w+\b") #the regex pattern defines which strings count as tokens
sparse_matrix = cv.fit_transform(documents)
dense_matrix = sparse_matrix.todense()
td_matrix = dense_matrix.T   # .T transposes the matrix

terms = cv.get_feature_names_out()

t2i = cv.vocabulary_  # shorter notation: t2i = term-to-index

# Operators and/AND, or/OR, not/NOT become &, |, 1 -
# Parentheses are left untouched
# Everything else is interpreted as a term and fed through td_matrix[t2i["..."]]

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


sparse_td_matrix = sparse_matrix.T.tocsr()
def rewrite_token(t):
    if (t not in d) and (t not in t2i):     # if the token is not found in the documents
        return 'UNKNOWN'
    else:
        return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t)) # Make retrieved rows dense
    
# Perform the queries on the documents and print the contents of the matching documents

def printContents(query):
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
    
    print("There are", len(hits_list), "matching documents")

    counter = 0      # a counter to make sure that no more than five documents are printed (even if there were more matches)
    for i, doc_idx in enumerate(hits_list):
        if counter < 5:
            print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx][:500]))       # only print the first 500 characters of each document
            counter += 1
    print()


# Asking user for a query
def getquery():
    while True:
        query = input("Enter a search word or press enter to end the query.\n"
                      "AND, OR, NOT operators must be written in capitals,"
                      'for example "word1 OR word2".\n')
        if len(query) == 0:
            print("Thank you!") # Ends the program by thanking the user :)
            break
        printContents(query)


# Runs the program
getquery()
