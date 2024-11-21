from dataclasses import dataclass

class expression():
    pass

@dataclass
class number(expression):
    value: int

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"{self.value}"
    
@dataclass
class variable(expression):
    name: str

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"
    
@dataclass
class binaryOperation(expression):
    bop: str
    expr1: expression
    expr2: expression

    def __init__(self, bop, expr1, expr2):
        self.bop = bop
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return f"{self.expr1} {self.bop} {self.expr2}"

@dataclass
class cond():
    var: variable
    rel: str
    num: number
    def __init__(self, var, rel, num):
        self.var = var
        self.rel = rel
        self.num = num

    def __str__(self):
        return f"{self.var} {self.rel} {self.num}"
 

class command():
    pass

@dataclass
class skip(command):
    def __init__(self):
        pass
    def __str__(self):
        return f"skip"

@dataclass
class seq(command):
    c1: command
    c2: command

    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2
    def __str__(self):
        return f"{self.c1};{self.c2}"
    
@dataclass
class assign(command):
    var: variable
    exp: expression

    def __init__(self, var, exp):
        self.var = var
        self.exp = exp

    def __str__(self):
        return f"{self.var} := {self.exp}"

@dataclass 
class input_command(command):
    var: variable

    def __init__(self, var):
        self.var = var

    def __str__(self):
        return f"input({self.var})"

@dataclass
class if_else(command):
    guard: cond
    body1: command
    body2: command

    def __init__(self, guard, body1, body2):
        self.guard = guard
        self.body1 = body1
        self.body2 = body2
    def __str__(self):
        return f'''if ({self.guard})\n {self.body1}\nelse\n {self.body2}'''

@dataclass
class while_command(command):
    guard: cond
    body: command

    def __init__(self, guard, body):
        self.guard = guard
        self.body = body

    def __str__(self):
        return f'''while ({self.guard})\n {self.body}'''
     