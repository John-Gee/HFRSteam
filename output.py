import sys
import os
import Game

indentcount = 0

def writeline(f, line):
    indent = 4
    for i in range(0, indent * indentcount):
        f.write(" ")
    f.write(line)
    f.write(os.linesep)

def increase_indent_count():
    global indentcount
    indentcount += 1

def decrease_indent_count():
    global indentcount
    indentcount -= 1


def output_to_html(games, file):
    f = open(file, "w")
    writeline(f, "<html>")
    increase_indent_count()
    writeline(f, "<head>")
    increase_indent_count()
    writeline(f, "<title>HFR Steam List</title>")
    #writeline(f, "<script type=\"text/javascript\" src=\"scripts/jquery.tablesorter/jquery.tablesorter.js\"></script>")
    writeline(f, "<link rel=\"stylesheet\" href=\"https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css\">")
    writeline(f, "<script src=\"https://code.jquery.com/jquery-1.11.3.min.js\"></script>")
    writeline(f, "<script src=\"https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js\"></script>")
    writeline(f, "<script>")
    increase_indent_count()
    writeline(f, "<style>")
    increase_indent_count()
    writeline(f, "table, th, td {")
    increase_indent_count()
    writeline(f, "border: 1px solid black;")
    decrease_indent_count()
    writeline(f, "}")
    writeline(f, "th {")
    increase_indent_count()
    writeline(f, "white-space: nowrap;")
    decrease_indent_count()
    writeline(f, "}")
    decrease_indent_count()
    writeline(f, "</style>")
    decrease_indent_count()
    writeline(f, "</script>")
    decrease_indent_count()
    writeline(f, "</head>")
    writeline(f, "<body>")
    increase_indent_count()
    writeline(f, "<div style=\"width: 100%; overflow: auto\">")
    increase_indent_count()
    writeline(f, "<table id=\"myTable\" class=\"ui-responsive ui-shadow\" cellpadding=\"5\" data-role=\"table\" data-mode=\"columntoggle\" data-filter=\"true\" data-input=\"#filterTable-input\">")
    increase_indent_count()
    writeline(f, "<thead>")
    increase_indent_count()
    writeline(f, "<tr>")
    increase_indent_count()
    writeline(f, "<th data-priority=\"1\">Game</th>")
    writeline(f, "<th data-priority=\"2\">Description</th>")
    writeline(f, "<th data-priority=\"9\">Is a DLC</th>")
    writeline(f, "<th data-priority=\"4\">Supports Linux</th>")
    writeline(f, "<th data-priority=\"8\">Price</th>")
    writeline(f, "<th data-priority=\"5\">Genres</th>")
    writeline(f, "<th data-priority=\"9\">Release Date</th>")
    writeline(f, "<th data-priority=\"6\">Average Review</th>")
    writeline(f, "<th data-priority=\"7\">Review Count</th>")
    decrease_indent_count()
    writeline(f, "</tr>")
    decrease_indent_count()
    writeline(f, "</thead>")
    writeline(f, "<tbody>")
    increase_indent_count()
    for gameName in sorted(games):
        game = games[gameName]
        if (game.available == "no") or (game.is_linux !=  "yes"):
            continue
        writeline(f, "<tr>")
        increase_indent_count()
        if (game.link != ""):
            writeline(f, "<td> <a href=\"" + game.link + "\">" + game.name + "</a> <br/>")
            writeline(f, "<img src=" + game.image + " width=\"40%\" height=\"40%\"/> </td>")
        else:
            writeline(f, "<td> " + game.name + "</td>")
        writeline(f, "<td>" + game.description + "</td>")
        writeline(f, "<td>" + game.is_dlc + "</td>")
        writeline(f, "<td>" + game.is_linux + "</td>")
        writeline(f, "<td>" + game.price + "</td>")
        genres = ""
        for genre in iter(game.genres):
            genres = genres + (genre + ", ")
        genres = genres[:-2]
        writeline(f, "<td>" + genres + "</td>")
        writeline(f, "<td>" + game.release_date + "</td>")
        writeline(f, "<td>" + game.avg_review + "</td>")
        writeline(f, "<td>" + game.cnt_review + "</td>")
        decrease_indent_count()
        writeline(f, "</tr>")
    decrease_indent_count()
    writeline(f, "</tbody>")
    decrease_indent_count()
    writeline(f, "</table>")
    decrease_indent_count()
    writeline(f, "</div>")
    decrease_indent_count()
    writeline(f, "</body>")
    decrease_indent_count()
    writeline(f, "</html>")
    f.close()
