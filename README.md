# Palsternakka

Palsternakka is a search engine for the top 250 movies on IMDb.com. The user can search for title, genre, actors, year or by keywords.

### About

This project was created by Silva Hilosuo, Ville-Veikko Mäntylä and Aino Vanhakartano as a part of an NLP applications course at Helsinki University.

### Table of contents

 + Installation
 + Usage
 + Troubleshooting
 + Additional Information


### Installation

This program requires certain modules to run smoothly. The required modules for this programme are included in the requirements.txt file.
This file can be used to make sure all required modules are installed and up to date, by running a command on the terminal's command line.

1. Firstly, clone this repository.

2. Open a terminal and navigate to the directory of this project, Palsternakka. Once there, write the following code.

```
pip install -r requirements.txt
```
This installs all of the modules listed in our Python requirements file into the environment being used.
   
### Usage

1.  Activate your virtual environment.

This project is run in a virtual environment. \
To activate it, write the following code for **Mac**:

```
. demoenv/bin/activate
```

For **Windows**, write:

```
demoenv/Scripts/activate
```

2. Run flask

By running flask we activate the HTTP server for us to use our search engine.
In the terminal command line, type:

```
flask run
```

**NOTE!** Due to the large size of the data used in our search engine, it might take up to 5-10 minutes for the server to load.

3. Navigate to `http://127.0.0.1:8000/search` on your browser. Like before, this will take a few minutes to load.

4. In the search bar, write your query. Choose type of search accordingly - either "keywords", "genre", "year" or "actor". If you wish to search for multiple keywords,
you can write the queries using **AND**, **OR**, **AND NOT** operators written in ALLCAPS. Note here that if you wish to exclude something from your search it has to be written **AND NOT** instead of just "NOT".
When searching for a single keyword, the results are ranked from most to least relevant. Here, also a bar chart of your five best results will show. When searching for multiple words, or searching for
actor, genre or year, the results are not ranked by relevance but shown in a descending order from best to worst rated.

The search is case insensitive which means you can write in lowercase or uppercase letters, except for the boolean operators **AND**, **OR**, **AND NOT**.

### Troubleshooting

- If you search for something not in our system, the search will return "No matching documents". If your search doesn't return any text, make sure you have chosen one of the search methods
of "actor", "year", "genre", "keyword", and "title".

- For now, our search engine only prints a bar chart when you search for keyword with a one word query. It will show that same chart until a new keyword query of a single word is made. So notice that
for example a search for genre or a search for keyword using boolean operators will unfortunately not generate a corresponding bar chart.

- When searching for year, make sure to type the whole year, for example "1998" instead of "98".

    

### Additional Information

This project was created during the course *Building NLP applications* in [Helsinki University](https://www.helsinki.fi/fi).\
The movie database is from [IMDb.com](https://www.imdb.com). \
The main modules used in this project:
+ [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
+ [NLTK](https://www.nltk.org)
+ [Scikit-learn](https://scikit-learn.org/stable/)
+ [NumPy](https://numpy.org)
+ [Matplotlib](https://matplotlib.org)
+ [Flask](https://flask.palletsprojects.com/en/2.2.x/)

    


