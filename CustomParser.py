# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from my_lex import tokens

from dataclasses import dataclass


# TODO: include more cases
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),            # Unary minus operator
)
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
     
# statements
def p_stmt_expr(p):
    '''statement : expression'''
    p[0] = p[1]

def p_stmt_cond(p):
    '''statement : cond'''
    p[0] = p[1]

def p_stmt_command(p):
    '''statement : command'''
    p[0] = p[1]

#commands
def p_command_skip(p):
    '''command : skip'''
    p[0] = skip()

def p_command_seq(p):
    '''command : command SEQ command'''
    p[0] = seq(p[1], p[3])   

def p_command_assign(p):
    '''command : VAR ASSIGN expression'''
    p[0] = assign(p[1], p[3]) 

def p_command_input(p):
    '''command : input LPAREN VAR RPAREN'''
    p[0] = input_command(p[3])

def p_command_if(p):
    '''command : if cond LCURL command RCURL else LCURL command RCURL'''
    p[0] = if_else(p[2], p[4], p[8])

def p_command_while(p):
    '''command : while cond LCURL command RCURL'''
    p[0] = while_command(p[2], p[4])

# Booleans Relations
def p_cond(p):
    '''
    cond : LPAREN VAR binaryREL NUMBER RPAREN
    '''
    p[0] = cond(p[2], p[3], p[4])

def p_binary_relation(p):
    '''binaryREL : LEQ
                | LE
                | GE
                | GEQ'''
    p[0] = p[1]

# Expressions
def p_expression_number(p):
    '''expression : NUMBER
    '''
    p[0] = number(p[1])

def p_expression_var(p):
    '''expression : VAR
    '''
    p[0] = variable(p[1])

def p_expression_neg(p):
    '''expression : MINUS expression %prec UMINUS'''
    p[0] = binaryOperation(p[1], number(0), p[2])

def p_expression(p):
    '''expression : expression binaryOP expression'''
    p[0] = binaryOperation(p[2], p[1], p[3])


def p_binary_operator(p):
    '''binaryOP : PLUS
                | MINUS
                | TIMES'''
    p[0] = p[1]


# Error rule for syntax errors
def p_error(p):
    raise SyntaxError(f"Syntax error in input!")

# Build the parser
parser = yacc.yacc(debug=True)