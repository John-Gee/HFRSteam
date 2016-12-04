import os
import sys

_indentcount = 4
_INDENTSTEP = 4


def writeline(line):
    newline = ""
    for i in range(0, _INDENTSTEP * _indentcount):
        newline += " "
    newline += line + os.linesep
    return newline


def increase_indent_count():
    global _indentcount
    _indentcount += 1


def decrease_indent_count():
    global _indentcount
    _indentcount -= 1


def get_data(games):
    reviewMapping = dict()
    reviewMapping['overwhelmingly positive'] = '4'
    reviewMapping['very positive'] = '3'
    reviewMapping['positive'] = '2'
    reviewMapping['mostly positive'] = '1'
    reviewMapping['mixed'] = '0'
    reviewMapping['mostly negative'] = '-1'
    reviewMapping['negative'] = '-2'
    reviewMapping['very negative'] = '-3'
    reviewMapping['overwhelmingly negative'] = '-4'
    data = ""
    justifyFormat = '<div style=\\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\\">{0}</div>'

    for gameName in sorted(games):
        game = games[gameName]
        if (game.available == 'no'):
            continue

        data += writeline('var row = {')
        increase_indent_count()
        data += writeline('name: "' + game.name + '",')
        if (game.link != ''):
            data += writeline('nameFormat: "<a href=\\"' + game.link + '\\"><b>' + justifyFormat +
                      '</b></a><img src=\\"' + game.image + '\\" width=\\"100%\\"/>",')
        else:
            data += writeline('nameFormat: "<b>' + justifyFormat + '</b>",')
        data += writeline('description: "' + game.description.strip() + '",')
        data += writeline('dlc: ' + game.is_dlc + ',')
        data += writeline('os: "' + ', '.join(game.os) + '",')
        if (game.price == None):
            data += writeline('priceFormat: "' + justifyFormat.replace(
                '{0}', 'Not available.' + ' <div style=\\"white-space: nowrap\\">(' + game.price_date + ')</div>') + '",')
        else:
            data += writeline('price: ' + str(game.price) + ',')
            if (game.price == 0):
                data += writeline('priceFormat: "' + justifyFormat.replace(
                    '{0}', 'Free' + ' <div style=\\"white-space: nowrap\\">(' + game.price_date + ')</div>') + '",')
            else:
                data += writeline('priceFormat: "' + justifyFormat.replace('{0}', '$' + str(
                    game.price) + ' <div style=\\"white-space: nowrap\\">(' + game.price_date + ')</div>') + '",')

        data += writeline('genres: "' + ', '.join(game.genres) + '",')
        data += writeline('date: "' + game.release_date + '",')
        if (game.avg_review.lower() in reviewMapping):
            avg_review = reviewMapping[game.avg_review.lower()]
            data += writeline('review: "' + avg_review +
                      ' ' + game.avg_review + '",')
            data += writeline('reviewFormat: "' + justifyFormat.replace(
                '{0}', game.avg_review + ' (' + game.cnt_review + ')') + '",')
        else:
            if (game.avg_review != ''):
                print('The average review ' + game.avg_review +
                      'for game ' + game.name + ' is not in the mapping!')

        decrease_indent_count()
        data += writeline('};')
        data += writeline('rows.push(row);')

    return data


def output_to_html(games, file):
    TEMPLATE_FILE   = 'templates/index.html.t'
    TEXT_TO_REPLACE = '$TEMPLATE$'

    f            = open(TEMPLATE_FILE, 'r')
    templatetext = f.read()
    f.close()

    data = get_data(games)

    text = templatetext.replace(TEXT_TO_REPLACE, data)

    f = open(file, 'w')
    f.write(text)
    f.close()
