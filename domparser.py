import html5_parser
import lxml


def load_html(html):
    return html5_parser.parse(html)


def kwargs_to_constraints(**kwargs):
    l = []
    for key in kwargs.keys():
        if ('_contains' in key):
            l.append('contains(@{0}, "{1}")'.format(key.replace('_contains', ''),
                                                   kwargs[key]))
        else:
            l.append('@{0}="{1}"'.format(key, kwargs[key]))
    return (' and ').join(l).replace('class_', 'class').replace('@string=', 'text()=')


def get_element(document, name_, **kwargs):
    if (kwargs):
        constraints = kwargs_to_constraints(**kwargs)
        element = document.xpath('(.//{0}[{1}])[1]'.format(name_, constraints))
    else:
        element = document.xpath('(.//{0})[1]'.format(name_))
    if (len(element)):
        return element[0]


def get_element_string(document, name_, **kwargs):
    element = get_element(document, name_, **kwargs)
    if (element is not None):
        return lxml.etree.tostring(element, encoding='unicode')


def get_elements(document, name_, **kwargs):
    if (kwargs):
        constraints = kwargs_to_constraints(**kwargs)
        return document.xpath('.//{0}[{1}]'.format(name_, constraints))
    else:
        return document.xpath('.//{0}'.format(name_))


def get_parent(element):
    return element.getparent()


def get_value(element, item, name_=None, **kwargs):
    if (name_):
        newelement = get_element(element, name_, **kwargs)
    else:
        newelement = element
    if (newelement is not None):
        return newelement.get(item)
    return None


def get_values(element, item, name_=None, **kwargs):
    elements = get_elements(element, name_, **kwargs)
    values = []
    for newelement in elements:
        values.append(get_value(newelement, item))
    return values


def get_text(element, name_=None, **kwargs):
    if (name_):
        newelement = get_element(element, name_, **kwargs)
    else:
        newelement = element
    if (newelement is not None):
        return newelement.text
    return None


def get_texts(element, name_, **kwargs):
    elements = get_elements(element, name_, **kwargs)
    texts = []
    for newelement in elements:
        text = get_text(newelement)
        if (text):
            texts.append(text.strip())
    return texts


def get_next_siblings_text(element, name_):
    texts = []
    for sibling in element.xpath('.//following-sibling::' + name_):
        texts.append(get_text(sibling))
    return texts


def get_texts_and_values(element, name_, item, **kwargs):
    elements = get_elements(element, name_, **kwargs)
    tv = []
    for newelement in elements:
        tv.append((get_text(newelement), get_value(newelement, item)))
    return tv
