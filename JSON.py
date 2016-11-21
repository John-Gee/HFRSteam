import json
import urllib.request

def get_data_from_url(url):
    f = urllib.request.urlopen(url)
    return json.loads(f.read().decode('utf-8'))
