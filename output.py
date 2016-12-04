import sys
import os
import Game

indentcount = 0

def writeline(f, line):
    indent = 4
    for i in range(0, indent * indentcount):
        f.write(' ')
    f.write(line)
    f.write(os.linesep)

def increase_indent_count():
    global indentcount
    indentcount += 1

def decrease_indent_count():
    global indentcount
    indentcount -= 1


def output_to_html(games, file):
    f = open(file, 'w')
    writeline(f, '<html>')
    increase_indent_count()
    writeline(f, '<head>')
    increase_indent_count()
    writeline(f, '<title>HFR Steam List</title>')
    writeline(f, '<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>')
    writeline(f, '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>')
    writeline(f, '<script src="jquery.watable.js"></script>')
    writeline(f, '<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"/>')
    writeline(f, '<link href="watable.css" rel="stylesheet"/>')
    writeline(f, '<meta name="viewport" content="width=device-width, initial-scale=1">')
    decrease_indent_count()
    writeline(f, '</head>')
    writeline(f, '<body>')
    increase_indent_count()
    writeline(f, '<h1>HFR Steam List</h1>')
    writeline(f, '<div id="wata" style="width:auto"></div>')
    
    writeline(f, '<script type="text/javascript">')
    increase_indent_count()
    writeline(f, '$(\'#wata\').WATable({')
    increase_indent_count()
    writeline(f, 'debug: false,')
    writeline(f, 'filter: true,')
    writeline(f, 'sorting: true,')
    writeline(f, 'sortEmptyLast: true,')
    writeline(f, 'columnPicker: true,')
    writeline(f, 'pageSize: 10,')
    writeline(f, 'hidePagerOnEmpty: true,')
    writeline(f, 'types: {')
    increase_indent_count()
    writeline(f, 'string: {')
    increase_indent_count()
    writeline(f, 'placeHolder: ""')
    decrease_indent_count()
    writeline(f, '},')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'data: getData(),')
    decrease_indent_count()
    writeline(f, '}).data(\'WATable\');')
    writeline(f, '')
    justifyFormat = '<div style=\\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\\">{0}</div>'
    writeline(f, 'function getData() {')
    increase_indent_count()
    writeline(f, 'var cols = {')
    increase_indent_count()
    writeline(f, 'name: {')
    increase_indent_count()
    writeline(f, 'index: 1,')
    writeline(f, 'type: "string",')
    writeline(f, 'friendly: "Name",')
    writeline(f, 'format: "' + justifyFormat + '",')
    writeline(f, 'unique: "true",')
    writeline(f, 'sortOrder: "asc",')
    writeline(f, 'tooltip: "The game\'s name",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'description: {')
    increase_indent_count()
    writeline(f, 'index: 2,')
    writeline(f, 'type: "string",')
    writeline(f, 'friendly: "Description",')
    writeline(f, 'format: "' + justifyFormat.replace(';', '; text-indent:1em;', 1) + '",')
    writeline(f, 'unique: "true",')
    writeline(f, 'tooltip: "The game\'s description",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'dlc: {')
    increase_indent_count()
    writeline(f, 'index: 3,')
    writeline(f, 'type: "bool",')
    writeline(f, 'friendly: "DLC?",')
    writeline(f, 'unique: "false",')
    writeline(f, 'tooltip: "Is this a DLC?",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'os: {')
    increase_indent_count()
    writeline(f, 'index: 4,')
    writeline(f, 'type: "string",')
    writeline(f, 'friendly: "Supported OS?",')
    writeline(f, 'format: "' + justifyFormat + '",')
    writeline(f, 'unique: "false",')
    writeline(f, 'tooltip: "Supported OS",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'price: {')
    increase_indent_count()
    writeline(f, 'index: 5,')
    writeline(f, 'type: "number",')
    writeline(f, 'decimals: 2,')
    writeline(f, 'friendly: "Price",')
    writeline(f, 'format: "' + justifyFormat + '",')
    writeline(f, 'unique: "false",')
    writeline(f, 'tooltip: "The game\'s price and its retrieved date",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'genres: {')
    increase_indent_count()
    writeline(f, 'index: 6,')
    writeline(f, 'type: "string",')
    writeline(f, 'friendly: "Genres",')
    writeline(f, 'format: "' + justifyFormat + '",')
    writeline(f, 'unique: "false",')
    writeline(f, 'tooltip: "The game\'s genres",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'date: {')
    increase_indent_count()
    writeline(f, 'index: 7,')
    writeline(f, 'type: "string",')
    writeline(f, 'friendly: "Release Date",')
    writeline(f, 'format: "' + justifyFormat + '",')
    writeline(f, 'unique: "false",')
    writeline(f, 'tooltip: "The game\'s release date",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    writeline(f, 'review: {')
    increase_indent_count()
    writeline(f, 'index: 8,')
    writeline(f, 'type: "string",')
    writeline(f, 'friendly: "Reviews",')
    writeline(f, 'format: "' + justifyFormat + '",')
    writeline(f, 'unique: "false",')
    writeline(f, 'tooltip: "The game\'s average review and the review count",')
    writeline(f, 'filter: "",')
    decrease_indent_count()
    writeline(f, '},')
    decrease_indent_count()
    writeline(f, '};')
    writeline(f, '')
    writeline(f, 'var rows = [];')
    writeline(f, '')
    
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

    for gameName in sorted(games):
        game = games[gameName]
        if (game.available == 'no'):
            continue
        
        writeline(f, 'var row = {')
        increase_indent_count()
        writeline(f, 'name: "' + game.name + '",')
        if (game.link != ''):
            writeline(f, 'nameFormat: "<a href=\\"' + game.link + '\\"><b>' + justifyFormat + '</b></a><img src=\\"' + game.image + '\\" width=\\"100%\\"/>",')
        else:
            writeline(f, 'nameFormat: "<b>' + justifyFormat + '</b>",')
        writeline(f, 'description: "' + game.description.strip() + '",')
        writeline(f, 'dlc: ' + game.is_dlc + ',')
        writeline(f, 'os: "' + ', '.join(game.os) + '",')
        if (game.price == None):
            writeline(f, 'priceFormat: "' + justifyFormat.replace('{0}', 'Not available.' + ' <div style=\\"white-space: nowrap\\">(' + game.price_date+ ')</div>') + '",')
        else:
            writeline(f, 'price: ' + str(game.price) + ',')
            if (game.price == 0):
                writeline(f, 'priceFormat: "' + justifyFormat.replace('{0}', 'Free' + ' <div style=\\"white-space: nowrap\\">(' + game.price_date+ ')</div>') + '",')
            else:
                writeline(f, 'priceFormat: "' + justifyFormat.replace('{0}', '$' + str(game.price) + ' <div style=\\"white-space: nowrap\\">(' + game.price_date+ ')</div>') + '",')
        
        writeline(f, 'genres: "' + ', '.join(game.genres) + '",')
        writeline(f, 'date: "' + game.release_date + '",')
        if (game.avg_review.lower() in reviewMapping):
            avg_review = reviewMapping[game.avg_review.lower()]
            writeline(f, 'review: "' + avg_review + ' ' + game.avg_review + '",')
            writeline(f, 'reviewFormat: "' + justifyFormat.replace('{0}', game.avg_review + ' (' + game.cnt_review + ')') + '",')
        else:
            if (game.avg_review != ''):
                print('The average review ' + game.avg_review + 'for game ' +game.name + ' is not in the mapping!')
        
        decrease_indent_count()
        writeline(f, '};')
        writeline(f, 'rows.push(row);')
    
    writeline(f, 'var data = {')
    increase_indent_count()
    writeline(f, 'cols: cols,')
    writeline(f, 'rows: rows,')
    decrease_indent_count()
    writeline(f, '};')
    writeline(f, '')
    writeline(f, 'return data;')
    decrease_indent_count()
    writeline(f, '}')
    decrease_indent_count()
    writeline(f, '</script>')
    
    decrease_indent_count()
    writeline(f, '</body>')
    decrease_indent_count()
    writeline(f, '</html>')
    f.close()
