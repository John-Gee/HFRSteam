#!/usr/bin/python

import sys
import parser
import output
import hfrparser

def main():
    numberOfArgs = len(sys.argv)
    if numberOfArgs <= 1:
        list  = hfrparser.parse_hfr()
        games = parser.parse_list(list)
    else:
        list  = open(sys.argv[1], "r")
        games = parser.parse_list(list)
        list.close()
    
    output.output_to_html(games, "list.html")

if __name__ == "__main__":
    main()
    
