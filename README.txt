This is a python (v3) script that will parse either a txt list of game names (one game per line) or a MyDiscussion specific page, then map these names to games in the Steam API, query some more information and print it to a nice dynamic webpage that allows filtering, sorting on many keys.

The only outside dependencies are python itself and BeautifulSoup v4.5.1.

Please contact me for changes, bugs or pull requests.

This software is released under the GNU GPLv3 license. 


Current issues:
- Somestimes the price of a game will be massive, this seems to an issue on the Steam API end, so not easy to fix.
- The script does not support bundles as I have not found a way to query the API for them.
- Currently most of the data is pulled from the API, but the reviews are pulled from the Webpage, it probably would make sense to pull everything from the same place, ie the webpage, and that should fix the previous issues,
- The difflib automatic mapping can result in some false positives which have to be caught either right away, or manually later (which is becoming a major issue with around 1000 games...). Fixing this would be nice.
- It only supports English/USD so far, both on the backend and the webpage.
