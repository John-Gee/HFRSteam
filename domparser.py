from bs4 import BeautifulSoup


def load_html(html):
    return BeautifulSoup(html, 'html.parser')


def get_element(document, name, **kwargs):
    return document.find(name, **kwargs)
