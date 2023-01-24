# This is the document for the search engine

# Copy relevant code.

from sklearn.feature_extraction.text import CountVectorizer

documents = ["This is a silly example",
             "A better example",
             "Nothing to see here",
             "This is a great and long example"]

cv = CountVectorizer(lowercase=True, binary=True)
sparse_matrix = cv.fit_transform(documents)
dense_matrix = sparse_matrix.todense()
td_matrix = dense_matrix.T   # .T transposes the matrix

terms = cv.get_feature_names_out()

print("First term (with row index 0):", terms[0])
print("Third term (with row index 2):", terms[2])

t2i = cv.vocabulary_  # shorter notation: t2i = term-to-index
print("Query: example")
print(td_matrix[t2i["example"]])

# Operators and/AND, or/OR, not/NOT become &, |, 1 -
# Parentheses are left untouched
# Everything else is interpreted as a term and fed through td_matrix[t2i["..."]]

d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_token(t):
    return d.get(t, 'td_matrix[t2i["{:s}"]]'.format(t)) # Can you figure out what happens here?

def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def test_query(query):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query))
    print("Matching:", eval(rewrite_query(query))) # Eval runs the string as a Python command
    print()


sparse_td_matrix = sparse_matrix.T.tocsr()
print(sparse_td_matrix)

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t)) # Make retrieved rows dense


# Perform the queries on the documents and print the contents of the matching documents

def printContents(query):
    
    hits_matrix = eval(rewrite_query(query))
    print("Matching documents as vector (it is actually a matrix with one single row):", hits_matrix)
    print("The coordinates of the non-zero elements:", hits_matrix.nonzero())    

    hits_list = list(hits_matrix.nonzero()[1])
    print(hits_list)

    for doc_idx in hits_list:
        print("Matching doc:", documents[doc_idx])

    for i, doc_idx in enumerate(hits_list):
        print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx]))


# Asking user for a query. Feel free to change the function name/location etc.

def getquery():
    while True:
        query = input("Enter a search word or press enter to end the query: ")
        if len(query) == 0:
            break
        printContents(query)

# Runs the program
getquery()


