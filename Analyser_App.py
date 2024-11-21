from CustomLexer import MyLexer
import my_lex
import builtins
from CustomParser import *

import streamlit as st


def f_bop(binOP, l, r):
    match binOP:
        case '+':
            return l + r
        case '-':
            return l - r
        case '*':
            return l * r 

    
class Memory():
    states = {}

    def __init__(self, states=None):
        if states != None:
            self.states = states

    def get_memory(self, x):
        return self.states.get(x, "")
    
    def set_memory(self, x, n):
        self.states[x] = n

    def __str__(self):
        out = "{"
        for k, v in self.states.items():
            out += f"{k} -> {v} "
        out += "}"

        return out
    
    def evaluate_expression(self, expression):
        match expression:
            case number(value):
                return value
            case variable(name):
                return self.get_memory(name)
            case binaryOperation(bop, expr1, expr2):
                l = self.evaluate_expression(expr1)
                r = self.evaluate_expression(expr2)
                return f_bop(bop,l, r)

st.set_page_config(page_title="Static Analysis Tool", page_icon="ℹ️", layout="wide")


example_codes = ["",
"""if (x <= 0){
    y := -x
} else {
   y  := x 
}""",
"""input(x);
y :=10;
while (x < 100){
    y := y - 3;
    x := x + y;
    y := y + 3
}
"""]

display = ("Custom", "Example 0", "Example 1")

options = list(range(len(display)))

selection = st.selectbox(
    'Choose a Code Example or try it with your own one.', options, format_func=lambda x: display[x])


code = st.text_area('Older Version: ', example_codes[selection], height=400)
run = st.button('Analyse')


# BEGIN: Display Results
m = Memory({'x': 1, 'y': 2})
if run:
    
   
   result = parser.parse(code)
   st.write(m.evaluate_expression(result))
   #st.write(m)