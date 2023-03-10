from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

'''movies = ['The Shawshank Redemption (1994) - IMDb.html',
          'The Good, the Bad and the Ugly (1966) - IMDb.html',
          'The Godfather (1972) - IMDb.html',
          'The Godfather Part II (1974) - IMDb.html',
          'Pulp Fiction (1994) - IMDb.html',
          "Schindler's List (1993) - IMDb.html",
          'The Lord of the Rings_ The Return of the King (2003) - IMDb.html',
          'The Lord of the Rings_ The Fellowship of the Ring (2001) - IMDb.html',
          '12 Angry Men (1957) - IMDb.html',
          'The Dark Knight (2008) - IMDb.html',
          'Forrest Gump (1994) - IMDb.html',
          'Fight Club (1999) - IMDb.html',
          'Taru sormusten herrasta_ Kaksi tornia (2002) - IMDb.html',
          'Inception (2010) - IMDb.html',
          'Imperiumin vastaisku (1980) - IMDb.html',
          'Matrix (1999) - IMDb.html']
'''

def get_urls():
    req = Request(
        url="https://www.imdb.com/chart/top/",
        headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-Us,en;q=0.5'}
    )
    webpage = urlopen(req).read().decode('utf8')
    soup = BeautifulSoup(webpage, 'html.parser')
    urls = []
    rows = soup.tbody.find_all('tr')
    for row in rows:
        urls.append('https://www.imdb.com' + row.a['href'])
    #urls = urls[:8]      # tätä voi muuttaa, jos haluaa testata eri määrällä leffoja tai eri kohdasta rankingia
    return urls

# *********
# FUNCTIONS
# *********

def get_title(movie, soup):
    title_of_a_movie = str(soup.title)          # Title of the movie
    title_of_a_movie = title_of_a_movie[7:-22]  # Make it prettier
    return title_of_a_movie

def get_actors(movie, soup):
    actors = [tag.string for tag in soup.find_all(class_="sc-bfec09a1-1 fUguci")]   # Actors starring in the movie
    return actors

def get_genres(movie, soup):
    genres = [tag.string for tag in soup.find_all(class_="ipc-chip__text")][:-1]    # Genres of the movie
    return genres

def get_summary(movie, soup, webpage):
    #summary = soup.find(class_="sc-6cc92269-2 jWocDE").string   # Summary of the movie
    result = re.search(r'"description":(".*"),"review":', webpage)
    summary = result.group(1)
    return summary

def get_year(movie, soup):
    year = str(soup.title)
    year = year[-20:-16]
    return year





# ************
# MAIN PROGRAM
# ************

def main():

    movies = get_urls()     # get_urls() palauttaa listan urleja
    #for url in urls:
    for movie in movies:
        
        moviedata = {}      # A dictionary where the information of the movie is stored
       # with open('static/movies/' + movie, 'r', encoding='utf-8') as file:         # Open the html file of a movie
        #    soup = BeautifulSoup(file, 'html.parser')       # Parse the html document with bs4
        req = Request(
            url=movie,
            headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-Us,en;q=0.5'}
        )
        webpage = urlopen(req).read().decode('utf8')
        soup = BeautifulSoup(webpage, 'html.parser')

        # Title
        title = get_title(movie, soup)
        moviedata["Title"] = title

        # Year
        year = get_year(movie, soup)
        moviedata["Year"] = year

        # Actors
        actors = get_actors(movie, soup)
        moviedata["Actors"] = actors

        # Genres
        genres = get_genres(movie, soup)
        moviedata["Genres"] = genres

        # Summary
        summary = get_summary(movie, soup, webpage)
        moviedata["Summary"] = title + ">" + summary

        # Append a movie to the data
        data.append(moviedata)
        
    return data
    
   

# The list where all the movies are stored
data = []
#main()
