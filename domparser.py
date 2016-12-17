from bs4 import BeautifulSoup


def load_html(html):
    return BeautifulSoup(html, 'html.parser')


def get_element(document, ID=None, nodetype=None):
    if (ID == None):
        if (nodetype == None):
            return None
        else:
            return _doc.find(nodetype)
    if (nodetype == None):
        return document.find(id=ID)
    return document.find(nodetype, id=ID)
