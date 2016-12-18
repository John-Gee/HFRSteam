import bs4


def load_html(html):
    return bs4.BeautifulSoup(html, 'html.parser')


def get_element(document, name, **kwargs):
    return document.find(name, **kwargs)


def get_elements(document, name, **kwargs):
    return document.find_all(name, **kwargs)


def get_parent(element, name, **kwargs):
    return element.find_parent(name, **kwargs)


def get_value(element, name, item, **kwargs):
    newelement = get_element(element, name, **kwargs)
    if (newelement):
        return newelement.get(item)
    return None


def get_values(element, name, item, **kwargs):
    elements = get_elements(element, name, **kwargs)
    values = []
    for newelement in elements:
        values.append(newelement.get(item))
    return values


def get_text(element, name, **kwargs):
    newelement = get_element(element, name, **kwargs)
    if (newelement):
        return newelement.get_text()
    return None

def get_next_siblings_text(element, name):
    texts = []
    for sibling in element.next_siblings:
        if(isinstance(sibling, bs4.Tag)):
            if(sibling.name != name):
                break
            texts.append(sibling.get_text())
    return texts
