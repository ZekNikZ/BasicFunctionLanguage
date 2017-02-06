import itertools


class Parser(object):
    def __init__(self, ml_asm):
        self.ml = ml_asm
        self.vars = {}
        self.funcs = {}
        self.pfuncs = {}

    def run(self):
        print('[PARSER] Starting parsing.\n')
        result = []
        dcount = 0
        for line in self.ml:
            print('[PARSER] Line ' + str(dcount) + ':')
            output = Parser.evaluate(line, cvars=self.vars, funcs=self.funcs, pfuncs=self.pfuncs)
            if type(output) is dict:
                if 'result' in output:
                    result.append(output['result'])
                else:
                    result.append(None)
                if 'vars' in output:
                    self.vars = output['vars']
                if 'funcs' in output:
                    self.funcs = output['funcs']
                if 'pfuncs' in output:
                    self.pfuncs = output['pfuncs']
            else:
                result.append(output)
            dcount += 1
            print()
        print('[PARSER] Done parsing.\n\n')
        return result

    @staticmethod
    def evaluate(_code, svars={}, cvars={}, funcs={}, pfuncs={}):
        code = _code[:]
        if code[0][0] == 'keyword':
            if len(code) == 1:
                print("[PARSER] Parsed command 'retrieve_var': ", end='')
                if code[0][1] in svars:
                    print('svar ' + code[0][1] + ' -> ' + str(svars[code[0][1]]))
                    return svars[code[0][1]]
                else:
                    print('cvar ' + code[0][1] + ' -> ' + str(cvars[code[0][1]]))
                    return cvars[code[0][1]]
            elif code[1][0] == 'assignment':
                result = Parser.peval(Parser.evaluate(code[2:], svars=svars, cvars=cvars, funcs=funcs, pfuncs=pfuncs))
                print("[PARSER] Parsed command 'assign_var': cvar " + code[0][1] + ' := ' + str(result))
                cvars[code[0][1]] = result
                return {'result': result, 'vars': cvars}
            elif code[1][0] == 'open_group':
                index = -1
                for j in range(len(code)):
                    if code[j][0] == 'close_group':
                        index = j
                        break
                arguments = [list(x[1]) for x in itertools.groupby(code[2:index], lambda x: x[0] == 'keyword_separator')
                             if not x[0]]
                if index + 1 < len(code) and code[index + 1][0] == 'assignment':
                    for argument in arguments:
                        if len(argument) != 1 or argument[0][0] != 'keyword':
                            raise NameError
                    if code[index + 2][0] != 'open_assignment_group':
                        print("[PARSER] Parsed command 'assign_func': func " + code[0][
                            1] + ' := ' + Parser.format_tokens(code[index + 2:]))
                        funcs[code[0][1]] = Parser.Function(code[index + 2:], *[x[0][1] for x in arguments])
                        return {'funcs': funcs}
                    else:
                        print("[PARSER] Parsed command 'assign_func_p': pfunc " + code[0][
                            1] + ' := ' + Parser.format_tokens(code[index + 2:]))
                        pfuncs[code[0][1]] = Parser.PiecewiseFunction(code[index + 2:],
                                                                      *[x[0][1] for x in arguments])
                        return {'pfuncs': pfuncs}
                        # else:
                        #     if code[0][1] in funcs:
                        #         return funcs[code[0][1]].run(svars, cvars, funcs, pfuncs, *arguments)
                        #     elif code[0][1] in pfuncs:
                        #         return pfuncs[code[0][1]].run(svars, cvars, funcs, pfuncs, *arguments)
                        #     raise NameError
        print("[PARSER] Evaluating basic string: '" + Parser.format_tokens(code)[:-1] + "'")
        for i in range(len(code)):
            if code[i] is None:
                continue
            if code[i][0] == 'keyword':
                if i + 1 >= len(code) or code[i + 1][0] != 'open_group':
                    if code[i][1] in svars:
                        code[i] = ['numeric', svars[code[i][1]]]
                    else:
                        code[i] = ['numeric', cvars[code[i][1]]]
                else:
                    index = -1
                    for j in range(i, len(code)):
                        if code[j][0] == 'close_group':
                            index = j
                            break
                    arguments = [list(x[1]) for x in
                                 itertools.groupby(code[i + 2:index], lambda x: x[0] == 'keyword_separator') if
                                 not x[0]]
                    if code[i][1] in funcs:
                        output = funcs[code[i][1]].run(svars, cvars, funcs, pfuncs, *arguments)
                    elif code[i][1] in pfuncs:
                        output = pfuncs[code[i][1]].run(svars, cvars, funcs, pfuncs, *arguments)
                    else:
                        raise NameError
                    code[i] = ['numeric', output]
                    for k in range(i + 1, index + 1):
                        code[k] = None
        return Parser.peval(code)

    def call_func(self, *arguments):
        pass

    @staticmethod
    def format_tokens(code):
        result = ''
        if type(code) != list:
            return code
        for token in code:
            if token is None:
                continue
            if token[0] == 'power':
                result += '** '
            elif token[0] == 'equal':
                result += '== '
            else:
                result += str(token[1]) + ' '
        return result

    @staticmethod
    def peval(code):
        result = ''
        if type(code) != list:
            return code
        for token in code:
            if token is None:
                continue
            if token[0] == 'power':
                result += '** '
            elif token[0] == 'equal':
                result += '== '
            else:
                result += str(token[1]) + ' '
        return eval(result)

    class Function(object):

        def __init__(self, body, *args):
            self.body = body
            self.argnames = args

        def run(self, _svars_ps, _cvars, _funcs, _pfuncs, *args):
            _svars = {}
            for i in range(len(args)):
                _svars[self.argnames[i]] = Parser.evaluate(args[i], svars=_svars_ps, cvars=_cvars, funcs=_funcs,
                                                           pfuncs=_pfuncs)
            return Parser.evaluate(self.body, cvars=_cvars, svars=_svars, funcs=_funcs, pfuncs=_pfuncs)

    class PiecewiseFunction(object):

        def __init__(self, body, *args):
            self.body = body
            self.argnames = args
            pieces = [list(x[1]) for x in itertools.groupby(body[1:-1], lambda x: x[0] == 'statement_separator') if
                      not x[0]]
            self.bodies = [
                [list(x[1]) for x in itertools.groupby(piece, lambda x: x[0] == 'expression_separator') if not x[0]][0]
                for piece in pieces]
            self.conditions = [
                [list(x[1]) for x in itertools.groupby(piece, lambda x: x[0] == 'expression_separator') if not x[0]][1]
                for piece in pieces]

        def run(self, _svars_ps, _cvars, _funcs, _pfuncs, *args):
            _svars = {}
            for i in range(len(args)):
                _svars[self.argnames[i]] = Parser.evaluate(args[i], svars=_svars_ps, cvars=_cvars, funcs=_funcs,
                                                           pfuncs=_pfuncs)
            for j in range(len(self.conditions)):
                if Parser.evaluate(self.conditions[j], cvars=_cvars, svars=_svars, funcs=_funcs, pfuncs=_pfuncs):
                    return Parser.evaluate(self.bodies[j], cvars=_cvars, svars=_svars, funcs=_funcs, pfuncs=_pfuncs)
