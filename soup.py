from bs4 import BeautifulSoup

with open("sodexo.htm") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

p = soup.find(string="Tänään")
s = p.find_all_next(class_="meal_name")
print(p)