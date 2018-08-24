import bs4
import html5_parser


def load_html(html):
    return html5_parser.parse(html, treebuilder='soup')


def get_element(document, name, **kwargs):
    return document.find(name, **kwargs)


def get_elements(document, name, **kwargs):
    return document.find_all(name, **kwargs)


def get_parent(element, name, **kwargs):
    return element.find_parent(name, **kwargs)


def get_value(element, item, name=None, **kwargs):
    if (name):
        newelement = get_element(element, name, **kwargs)
    else:
        newelement = element
    if (newelement):
        return newelement.get(item)
    return None


def get_values(element, item, name=None, **kwargs):
    elements = get_elements(element, name, **kwargs)
    values = []
    for newelement in elements:
        values.append(get_value(newelement, item))
    return values


def get_text(element, name=None, **kwargs):
    if (name):
        newelement = get_element(element, name, **kwargs)
    else:
        newelement = element
    if (newelement):
        return newelement.get_text()
    return None


def get_texts(element, name, **kwargs):
    elements = get_elements(element, name, **kwargs)
    texts = []
    for newelement in elements:
        text = get_text(newelement)
        if (text):
            texts.append(text.strip())
    return texts


def get_next_siblings_text(element, name):
    texts = []
    for sibling in element.next_siblings:
        if(isinstance(sibling, bs4.Tag)):
            if (sibling.name != name):
                break
            texts.append(get_text(sibling))
    return texts


def get_texts_and_values(element, name, item, **kwargs):
    elements = get_elements(element, name, **kwargs)
    tv = []
    for newelement in elements:
        tv.append((get_text(newelement), get_value(newelement, item)))
    return tv


def remove_element(document, name, **kwargs):
    element = get_element(document, name, **kwargs)
    if (element):
        element.decompose()
