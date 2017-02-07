import re

tokens_high_priority = {
    'keyword': '[a-zA-Z][a-zA-Z0-9]*',
    'numeric': '(?<!\w)-?([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)',
    'assignment': ':=',
    'less_than_equal': '<=',
    'greater_than_equal': '>='
}

tokens_low_priority = {
    'open_assignment_group': '{',
    'close_assignment_group': '}',
    'open_group': '\(',
    'close_group': '\)',
    'keyword_separator': ',',
    'expression_separator': ':',
    'statement_separator': ';',
    'plus': '\+',
    'minus': '-',
    'divide': '\/',
    'multiply': '\*',
    'power': '\^',
    'equal': '=',
    'less_than': '<',
    'greater_than': '>'
}


class Lexer(object):
    def __init__(self, code, debug=False):
        if code.startswith('$debugmode'):
            self.raw_code = code[len('$debugmode'):]
        else:
            self.raw_code = code
        self.lines = self.raw_code.split('\n')
        self.statements = []
        self.debug = debug

    def run(self):
        if self.debug:
            print('[LEXER] Starting lexing.\n')
        dcount = 0
        for line in self.lines:
            if self.debug:
                print('[LEXER] Line ' + str(dcount) + ':')
            tokens = self.tokenize(line, self.debug)
            if tokens:
                self.statements.append(tokens)
            dcount += 1
            if self.debug:
                print()
        if self.debug:
            print('[LEXER] Done lexing.\n\n')
        return self.statements

    @staticmethod
    def tokenize(statement, debug=False):
        string = statement
        token_list = []
        assigned = False
        while len(string) > 0:
            if string[0] == '#':
                break
            if string[0] == ' ':
                string = string[1:]
                continue
            done = False
            for token in tokens_high_priority:
                match = re.match('^' + tokens_high_priority[token], string)
                if not match:
                    continue
                # print(match.group())
                if token == 'assignment':
                    if assigned:
                        raise KeyError
                    assigned = True
                token_list.append([token, match.group()])
                if debug:
                    print("[LEXER] Found token '" + token + "': " + "'" + match.group() + "'")
                string = string[match.end():]
                done = True
                break
            for token in tokens_low_priority:
                match = re.match('^' + tokens_low_priority[token], string)
                if not match:
                    continue
                # print(match.group())
                token_list.append([token, match.group()])
                if debug:
                    print("[LEXER] Found token '" + token + "': " + "'" + match.group() + "'")
                string = string[match.end():]
                done = True
                break
            if not done:
                raise KeyError
        return token_list
