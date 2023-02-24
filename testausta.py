from bs4 import BeautifulSoup

movies = ['The Shawshank Redemption (1994) - IMDb.html',
          'The Good, the Bad and the Ugly (1966) - IMDb.html',
          'The Godfather (1972) - IMDb.html',
          'The Godfather Part II (1974) - IMDb.html',
          'Pulp Fiction (1994) - IMDb.html',
          "Schindler's List (1993) - IMDb.html",
          'The Lord of the Rings_ The Return of the King (2003) - IMDb.html',
          'The Lord of the Rings_ The Fellowship of the Ring (2001) - IMDb.html',
          '12 Angry Men (1957) - IMDb.html',
          'The Dark Knight (2008) - IMDb.html']

# A list where all the dictionaries are stored
data = []

for movie in movies:
    # A dictionary where the information of the movie is stored
    moviedata = {}

    # Open the html file of a movie
    with open('static/movies/' + movie, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Title of the movie
    title_of_a_movie = str(soup.title)
    # Make it prettier
    title_of_a_movie = title_of_a_movie[7:-22]

    # Add the title to the dictionary
    moviedata["Title"] = title_of_a_movie

    # Actors starring in the movie
    actors = [tag.string for tag in soup.find_all(class_="sc-bfec09a1-1 fUguci")]
    # Add the actors to the dictionary
    moviedata["Actors"] = actors

    # Genres of the movie
    genres = [tag.string for tag in soup.find_all(class_="ipc-chip__text")][:-1]
    # Add the genres to the dictionary
    moviedata["Genres"] = genres

    # Summary of the movie
    summary = soup.find(class_="sc-6cc92269-0 iNItSZ").string
    # Add the summary to the dictionary
    moviedata["Summary"] = summary

    data.append(moviedata)

print(data[3])