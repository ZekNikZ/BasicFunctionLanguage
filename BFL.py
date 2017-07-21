from Lexer import Lexer
from Parser import Parser
import sys

if __name__ == '__main__':
    debug = False
    filter_output = False
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-help' or sys.argv[i] == '-?':
            print('BFL Help',
                  '========',
                  '-help, -?:',
                  '  Display this information.',
                  '-file, -f:',
                  '  Execute code in a file containing BFL code.',
                  '-filteroutput, -fo:',
                  '  Filter "None" types out of the output.',
                  '-debug, -d',
                  '  Turn on debug mode (can also be done by '
                  '  placing "$debugmode" at the beginning of the file)',
                  sep="\n")
            i += 1
        elif sys.argv[i] == '-file' or sys.argv[i] == '-f':
            if i + 1 >= len(sys.argv):
                print('ERROR: Not enough arguments.')
                break
            else:
                with open(sys.argv[i + 1], 'r') as code_file:
                    data = code_file.read()

                code = data.split('\n', 1)
                first_line = code[0]

                prev_flags = (debug, filter_output)
                if first_line.startswith('$'):
                    if 'debugmode' in first_line:
                        debug = True
                    if 'filteroutput' in first_line:
                        filter_output = True

                lexer = Lexer(code[1] if first_line.startswith('$') else data, debug)
                token_list = lexer.run()

                parser = Parser(token_list, debug)
                result = parser.run()
                if filter_output:
                    result = list(filter(lambda x: x is not None, result))
                print('[ANS] ' + str(result))

                if first_line.startswith('$'):
                    if 'debugmode' in first_line:
                        debug = prev_flags[0]
                    if 'filteroutput' in first_line:
                        filter_output = prev_flags[0]

                i += 2
        elif sys.argv[i] == '-debug' or sys.argv[i] == '-d':
            debug = True
            i += 1
        elif sys.argv[i] == '-filteroutput' or sys.argv[i] == '-fo':
            filter_output = True
            i += 1
        else:
            print('ERROR: Invalid flag: %s' % sys.argv[i])
            break
