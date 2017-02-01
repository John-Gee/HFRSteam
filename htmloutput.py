import datetime
import os
import sys


_indentcount = 4
_INDENTSTEP = 4


def writeline(line):
    newline = ''
    for i in range(0, _INDENTSTEP * _indentcount):
        newline += ' '
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
    reviewMapping['10'] = 'Overwhelmingly Positive'
    reviewMapping['9']  = 'Very Positive'
    reviewMapping['8']  = 'Positive'
    reviewMapping['7']  = 'Mostly Positive'
    reviewMapping['6']  = 'Mixed'
    reviewMapping['5']  = 'Mostly Negative'
    reviewMapping['4']  = 'Negative'
    reviewMapping['3']  = 'Very Negative'
    reviewMapping['2']  = 'Overwhelmingly Negative'
    data = ''
    justifyFormat = '<div style=\\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\\">{0}</div>'

    for gameName in sorted(games):
        game = games[gameName]
        if (game.available == 'no'):
            continue

        data += writeline('var row = {')
        increase_indent_count()
        data += writeline('name: "{0}",'.format(game.name))
        #data += writeline('name: "' + game.name + '"')
        if (game.link != ''):
            data += writeline('nameFormat: "<a href=\\"{0}\\"><b>{1}</b></a><img src=\\"{2}\\" width=\\"100%\\"/>",'.format(game.link, justifyFormat, game.image))
        else:
            data += writeline('nameFormat: "<b>{0}</b>",'.format(justifyFormat))
        if(game.description):
            data += writeline('description: "{0}",'.format(game.description))
        data += writeline('dlc: {0},'.format(game.is_dlc))
        if (len(game.os) > 0):
            data += writeline('os: "{0}",'.format(', '.join(game.os)))
        if (game.price == None):
            data += writeline('priceFormat: "{0}",'.format(justifyFormat.replace(
                '{0}', 'Not available. <div style=\\"white-space: nowrap\\">({0})</div>'.
                format(game.price_date))))
        else:
            data += writeline('price: {0},'.format(str(game.price)))
            if (game.price == 0):
                data += writeline('priceFormat: "{0}",'
                                  .format(justifyFormat.replace('{0}',
                                                                'Free <div style=\\"white-space: nowrap\\">({0})</div>'.
                                                                format(game.price_date))))
            else:
                data += writeline('priceFormat: "{0}",'.
                                  format(justifyFormat.replace('{0}',
                                                               '${0} <div style=\\"white-space: nowrap\\">({1})</div>'.
                                                               format(str(game.price), game.price_date))))

        if (len(game.genres) > 0):
            data += writeline('genres: "{0}",'.format(', '.join(game.genres)))
        if (game.release_date):
            data += writeline('date: "{0}",'.format(game.release_date))
        if (game.avg_review in reviewMapping):
            avg_review_text = reviewMapping[game.avg_review]
            avg_review      = game.avg_review
            if (len(avg_review) == 1):
                avg_review = '0{0}'.format(avg_review)
            data += writeline('review: "{0} {1}",'.
                              format(avg_review, avg_review_text))
            data += writeline('reviewFormat: "{0}",'.
                              format(justifyFormat.replace('{0}',
                                                           '{0} ({1})'.
                                                           format(avg_review_text,
                                                                  game.cnt_review))))
        else:
            if (game.avg_review):
                print('The average review {0} for game {1} is not in the mapping!'.
                      format(game.avg_review, game.name))

        decrease_indent_count()
        data += writeline('};')
        data += writeline('rows.push(row);')

    return data


def output_to_html(games, file):
    TEMPLATE_FILE   = 'templates/index.html.t'
    TEXT_TO_REPLACE = '$TEMPLATE$'
    DATE_TO_REPLACE = '$DATE$'

    f            = open(TEMPLATE_FILE, 'r')
    templatetext = f.read()
    f.close()

    data = get_data(games)

    text = templatetext.replace(TEXT_TO_REPLACE, data)

    text = text.replace('$DATE$', datetime.date.today().isoformat())

    f = open(file, 'w')
    f.write(text)
    f.close()
