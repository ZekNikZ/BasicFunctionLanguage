from Lexer import Lexer
from Parser import Parser
import re

if __name__ == '__main__':
    with open('samples/riemannsum.txt', 'r') as myfile:
        data = myfile.read()

    debug = False
    if data.startswith('$debugmode'):
        debug = True

    l = Lexer(data, debug)

    z = l.run()

    e = Parser(z, debug)

    o = e.run()

    print('[ANS] ' + str(o))
