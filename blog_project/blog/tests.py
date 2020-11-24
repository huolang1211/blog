from django.test import TestCase

# Create your tests here.
from bs4 import BeautifulSoup
#
# s= '<div><a>abc</a>d</div>'
# soup = BeautifulSoup(s,'html.parser')
# print(soup.text)


s= '<div><a>abc</a>d</div><script>alert(123)</script>'
soup = BeautifulSoup(s,'html.parser')
for tag in soup.find_all():
    print(tag.name)
    if tag.name == 'script':
        tag.decompose()
print(str(soup))