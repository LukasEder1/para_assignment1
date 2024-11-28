# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from my_lex import tokens
from DataTypes import *

# TODO: include more cases
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),            # Unary minus operator
)

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

#TODO: FIX Issuses when p[2] is a variable
def p_expression_neg(p):
    '''expression : MINUS expression %prec UMINUS'''
    if isinstance(p[2], number):
        p[0] = number(- p[2].value)
    else:
        p[0] = binaryOperation(p[1],  number(0), p[2])

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