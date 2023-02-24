from urllib import request
from bs4 import BeautifulSoup

url = "https://www.imdb.com/title/tt0111161/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=1a264172-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=XF6SD0GJKAJ44EHCE8F9&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_1"
#url = "https://yle.fi/"

html = request.urlopen(url).read().decode('utf8')

soup = BeautifulSoup(html, 'html.parser')

print(soup.title)
