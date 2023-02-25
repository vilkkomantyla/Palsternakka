import data
from flask import Flask, render_template, request

#Initialize Flask instance
#app = Flask(__name__)

data = data.main()

print(data)





'''
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
    return render_template('index_uusi.html', matches=matches, result_summary=result_summary)
    '''
