import sys

import pycparser

def ast_from_file(filename):
    return pycparser.parse_file(filename)

def get_all_statements(filename):
    ast = ast_from_file(filename)
    statements = ast.ext[0].body.block_items
    return statements



if __name__ == '__main__':
    y = get_all_statements("Trivial.c")
    x = 'stop'