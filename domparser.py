from bs4 import BeautifulSoup


def load_html(html):
    return BeautifulSoup(html, 'html.parser')


def get_element(document, name, **kwargs):
    return document.find(name, **kwargs)


def get_parent(element, name, **kwargs):
    return element.find_parent(name, **kwargs)


def get_value(element, name, item, **kwargs):
    newelement = get_element(element, name, **kwargs)
    return newelement.get(item)
