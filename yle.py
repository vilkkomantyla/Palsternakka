'''This program should print out news headlines from yle.fi'''

from urllib import request
#from bs4 import BeautifulSoup      #didn't know how to use this in the case of yle.fi
import re

url = "https://yle.fi/"
html = request.urlopen(url).read().decode('utf8')
html = html.replace('\xad', '') #removing soft-hyphen markers from the source code

matches = re.findall(r'"text":(".*?")', html) # finding all headlines

how_many_headlines = int(input("How many headlines do you wish to see? "))
print(matches[0:how_many_headlines])
# Unfortunately many of the headlines are tags e.g. "Kulttuuri", "Urheilu".
# Didn't know how to get them out



#soup = BeautifulSoup(html, "html.parser")

    
