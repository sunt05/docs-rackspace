import argparse
import logging
from os import path

# number of tables converted during a run
numtables = 0


def readfile(infile):
    """Read data from file and return string."""
    infile = path.realpath(infile)
    try:
        with open(infile, 'r') as f:
            data = f.read()
    except IOError as ioerr:
        logging.error('File error (readData): ' + str(ioerr))
    return(data)


def writefile(outfile, data):
    """Write data to file."""
    outfile = path.realpath(outfile)
    try:
        with open(outfile, 'w') as f:
            f.write(data)
    except IOError as ioerr:
        logging.error('File error (writeData): ' + str(ioerr))


def adjustRow(row, col_num):
    """Convert a grid row to a list-table row."""
    if row.startswith('+') is True:
        return('\n')
    row = row.split('|')
    new_row = []
    for entry in row:
        new_row.append(entry)
        try:
            new_row.pop(new_row.index(''))
        except:
            pass
    convert = []
    convert.append('   * - ' + new_row[0].strip())
    for entry in new_row[1:]:
        convert.append(('\n     - ' + entry.strip()).rstrip())
    result = ''.join(convert)
    return(result)


def buildTable(data):
    """Build an RST list-table."""
    col_num = data[0].count('+') - 1
    col_width = str(int(100 / col_num))
    col_width = (' ' + col_width) * col_num

    output = []
    for line in data:
        row = adjustRow(line, col_num)
        output.append(row)
    result = ''.join(output)
    list_table = """.. list-table::\n   :widths:%s\n   :header-rows: 1\n%s""" \
                 % (col_width, result)
    global numtables
    numtables += 1
    return(list_table)


def dofile(infile, replace, create):
    """Process file to convert grid tables to list-tables."""
    data = readfile(infile)
    data = data.splitlines()
    grid = False
    insert = False
    gridtable = []
    content = []
    for line in data:
        if line.startswith('+--') is True or line.startswith('+==') is True:
            grid = True
            insert = True
            gridtable.append(line)
        elif grid is True and line.startswith('|') is True:
            gridtable.append(line)
        else:
            grid = False
        if grid is False:
            if insert is True:
                insert = False
                newtable = buildTable(gridtable)
                content.append(newtable + '\n')
                gridtable = []
            else:
                content.append(line + '\n')
    content = ''.join(content)
    if replace is True:
        writefile(infile, content)
    elif create is True:
        writefile(infile + '.new', content)
    else:
        print(content)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="table",
                                     description='''Convert RST grid table
                                     to list-table.''')
    parser.add_argument('INPUT', type=str, nargs='+', help='RST file(s)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--create', action='store_true',
                       help='''create new files (*.rst.new) with the converted
                       tables. Original files are unchanged.''')
    group.add_argument('-r', '--replace', action='store_true',
                       help='''modify input files, replacing grid tables with
                       list-tables''')
    args = parser.parse_args()
    for file in args.INPUT:
        dofile(file, args.replace, args.create)
    print('\033[92mTables converted: ' + str(numtables) + '\033[0m')