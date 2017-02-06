from Lexer import Lexer
from Parser import Parser

if __name__ == '__main__':
    with open('samples/riemannsum.txt', 'r') as myfile:
        data = myfile.read()

    l = Lexer(data)

    z = l.run()

    e = Parser(z)

    o = e.run()

    print('[ANS] ' + str(o))
