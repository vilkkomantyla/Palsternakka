import data

data = data.main()


# ************************
# USER INTERFACE FUNCTIONS
# ************************


# Search functions:

def searchActor():
    while True:
        query = input("\nSearch for movies by actor or press enter to exit the program.\n")
        if len(query) == 0:
            print("Thank you!")
            break
        else:
            titles = findResultsActor(query)
            printActorResults(titles, query)

def searchGenre():
    while True:
        query = input("\nSearch for movies by genre or press enter to exit the program.\n")
        if len(query) == 0:
            print("Thank you!")
            break
        else:
            titles = findResultsGenre(query)
            printGenreResults(titles, query)


# Functions to find matching movies:

def findResultsActor(query):
    titles = []
    for movie in data:
        lower_case_actors = [actor.lower() for actor in movie["Actors"]]
        if query.lower() in lower_case_actors:
            titles.append(movie["Title"])
    return titles

def findResultsGenre(query):
    titles = []
    for movie in data:
        lower_case_genres = [genre.lower() for genre in movie["Genres"]]
        if query.lower() in lower_case_genres:
            titles.append(movie["Title"])
    return titles


# Functions to print the results:

def printActorResults(titles, query):
    if len(titles) > 0:
        print(f"\n{query} starres in these movies: \n")
        for title in titles:
            print(title)
        print()
    else:
        print(f"\nNo movies found starring {query}.\n")
    
def printGenreResults(titles, query):
    if len(titles) > 0:
        print(f"\nThese are {query} movies: \n")
        for title in titles:
            print(title)
        print()
    else:
        print(f"\nNo movies found matching this genre.\n")


# Main program:
def main():
    searchmethod = input("Do you want to search for an actor (press a) or genre (press g)?\nPress enter to exit the program.\n")
    if searchmethod.lower() == "a":
        searchActor()
    elif searchmethod.lower() == "g":
        searchGenre()
    else:
        print("Thank you!")


# Run the program:
main()