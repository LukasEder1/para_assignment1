import ply.lex as lex

reserved = {
    "if": "if",
    "else": "else",
    "skip": "skip",
    "input": "input",
    "while": "while"
}

tokens = [
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LCURL',
    'RCURL',
    'LEQ',
    'GEQ',
    'LE',
    'GE',
    'ASSIGN',
    'SEQ',
    'ID', # for all reseved words
    'VAR'
    ] + list(reserved.values())

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LCURL   = r'\{'
t_RCURL   = r'\}'
t_SEQ     = r'\;'
t_LEQ     = r'\<='
t_GEQ     = r'\>='
t_LE      = r'\<'
t_GE      = r'\>'
t_ASSIGN  = r'\:='

def t_ID( t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'VAR')
    return t

# A regular expression rule with some action code
# Note addition of self parameter since we're in a class
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

# Test it output
def print_tokens(data):
    lexer.input(data)
    return [tok for tok in lexer]