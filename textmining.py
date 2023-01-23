import requests

URL = "https://www.sodexo.fi/ravintolat/helsingin-yliopisto-paarakennus"
response = requests.get(URL)
open("sodexo.htm", "wb").write(response.content)