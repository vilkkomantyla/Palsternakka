from bs4 import BeautifulSoup

with open("sodexo.htm") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

