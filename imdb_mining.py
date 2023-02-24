
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
          
for movie in movies:
    with open('static/movies/' + movie, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    title = soup.title
    print(title)

    actors = [tag.string for tag in soup.find_all(class_="sc-bfec09a1-1 fUguci")]
    print(actors)

    genres = [tag.string for tag in soup.find_all(class_="ipc-chip__text")][:-1]
    print(genres)
    print()

    summary = soup.find(class_="sc-6cc92269-0 iNItSZ").string
    print(summary)
    print()
