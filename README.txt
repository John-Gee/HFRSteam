This is a python (v3) script that will parse either a text list of game names (one game per line) or a MyDiscussion specific page, then map these names to games in the Steam API, query some more information and print it to a nice dynamic webpage that allows filtering, sorting on many keys.
A simple bb code outputer is also included.

The outside dependencies are python itself, BeautifulSoup v4, DateUtil v2 and Requests v2.

This software is released under the GNU GPLv3 license. 


Current issues:
- The difflib automatic mapping can result in some false positives which have to be caught either right away, or manually later (which is becoming a major issue with around 1000 games...). Because of that it's disabled unless overriden by an opt.
- Only support of English/USD so far, both on the backend and the webpage.
