from typing import Any, Tuple
from dataclasses import dataclass
from re import split


@dataclass
class Namespace: # used only to differentiate between strings and namespaces when tokenised and to let punctuation be tokenised
    name: str


class interpret:
    def clean_expr(self, expr: list) -> Any:
        return "".join([repr(t) if type(t) != Namespace else t.name for t in expr[0]])

    def evaluate(self, expr: str) -> bool:
        return bool(eval(self.clean_expr(self.parse_expr(expr))))

    def parse_string(self, expr: str, quotetype: str) -> Tuple(str, int):
        val = ""

        skip = False

        for i, c in enumerate(expr):
            if skip:
                continue
            elif c == "\\":
                val += expr[i + 1]

                skip = True
            elif c == quotetype:
                break
            else:
                val += c
        
        return val, i + 1

    def parse_expr(self, expr: str, btype: None | str=None) -> Any:
        tokens = split(r"\b", expr[btype is not None:])

        value = []
        skip = 0

        for index, token in enumerate(tokens):
            if skip:
                skip -= 1

                continue
            elif not token.strip():
                value.append(Namespace(token))

            if token[0] in "([{":
                val, skip = self.clean_expr(self.parse_expr("".join(expr[index:]), btype=token[0]))

                if token == "(":
                    val = eval("(%s)" % val, globals=(self.vars | self.funcs))
                elif token == "[":
                    val = eval("[%s]" % val, globals=(self.vars | self.funcs))
                elif token == "{":
                    val = eval("{%s}" % val, globals=(self.vars | self.funcs))
                
                value.append(val)
            elif token in ")]}":
                break
            elif token.isdigit():
                value.append(float(token))
            elif token == "None":
                value.append(None)
            elif token in "\"'":
                val, skip = self.parse_string("".join(tokens[index:]), token)
                value.append(val)
            elif token == ",":
                value.append(Namespace(token))
            elif token in self.vars:
                value.append(Namespace(token))
            else:
                raise SyntaxError

        return value, index

    def __init__(self, code: str) -> None:
        self.code: list[str] = [
            l.split("#")[0].strip() for l in code.split("\n") if l.split("#")[0].strip()
        ] # convert code into a list of lines with trailing whitespace and comments removed

        self.funcs: dict = {}
        self.vars: dict = {}

        multiline = False # parsing a definition
    
        for i, l in enumerate(self.code): # index, line
            line: list[str] = l.split() # split line at whitespace

            namespace = line[0] # get the first 'word' of the line
            operator = line[1] # same with the second

            try:
                arguments: list[str] = line[2:-(line[-1] == "$")] # and then the rest (removing the '$' at the end if there is one)
            except IndexError:
                pass # line has weird syntax, eg 'None $' at end of func def

            if not multiline:
                if l[-1] == "$" and operator == "&": # func def
                    self.code.pop(i)

                    name = namespace # func name
                    args: list[str] = [] # func args
                    body: list[str] = [] # func body
                    
                    if operator == "&":
                        args = arguments.split()
                        
                    multiline = True
                elif operator == "=" and namespace not in (self.vars | self.funcs):
                    self.vars[namespace] = eval(self.clean_expr(self.parse_expr("".join(arguments))))
            else:
                self.code.pop(i)

                if l[-1] != "$":
                    body.append(l)
                else:
                    self.funcs[name] = (args, body, namespace, ) # namespace in this line is what to return

                    multiline = False # exit func def mode

    def __call__(self) -> None:
        multiline = False
        skip = 0
    
        for l in self.code:
            # [namespace] [operation] [object]

            # [callable] . [arg1], [arg2], [etc.]

            # [namespace] & [arg1], [arg2], [etc.] $
            # [body]
            # [what to return] $

            # [namespace] & $
            # [body]
            # [what to return] $

            if skip:
                skip -= 1

                continue

            line: list[str] = l.split() # split line at whitespace

            namespace = line[0] # get the first 'word' of the line
            operation = line[1] # same with the second

            try:
                arguments: list[str] = line[2:-(line[-1] == "$")] # and then the rest (removing the '$' at the end if there is one)
            except IndexError:
                pass # line has weird syntax, eg 'None $' at end of func def

            if not multiline:
                if l[-1] == "$": # logic / flow control
                    multiline == True

                if operation == "IMPORT": # import something from another file
                    pass
                elif operation == ".": # call func
                    pass
                else: # operate on var / func
                    pass
            else:
                if l[-1] != "$":
                    if operation == "IMPORT": # import something from another file
                        pass
                    elif operation == ".": # call func
                        pass
                    else: # operate on var / func
                        pass
                else:
                    multiline = False
