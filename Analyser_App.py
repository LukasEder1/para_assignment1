from CustomLexer import MyLexer
import my_lex
import builtins
from CustomParser import *

import streamlit as st

# Call the function to get user input

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
    
    def evaluate_expression(self, expr: expression):
        match expr:
            case number(value):
                return value
            case variable(name):
                return self.get_memory(name)
            case binaryOperation(bop, expr1, expr2):
                l = self.evaluate_expression(expr1)
                r = self.evaluate_expression(expr2)
                return f_bop(bop,l, r)
            

    def evaluate_binary_relation(self, relation: cond):
        match relation:
            case cond(var, "<=", num):
                return self.get_memory(var) <= num
            case cond(var, "<", num):
                return self.get_memory(var) < num
            case cond(var, ">=", num):
                return self.get_memory(var) >= num
            case cond(var, ">", num):
                return self.get_memory(var) > num
            
    def evaluate_command(self, cmd: command):
        match cmd:
            case skip():
                pass
                #return self.states
            case seq(c1, c2):
                
                self.evaluate_command(c1)
                self.evaluate_command(c2)
            case assign(var, expr):
                self.set_memory(var, self.evaluate_expression(expr))
            case input_command(var):
                self.set_memory(var, 42)
            case if_else(guard, c1, c2):
                if self.evaluate_binary_relation(guard):
                    self.evaluate_command(c1)
                else:
                    self.evaluate_command(c2)
            case while_command(guard, c):
                while self.evaluate_binary_relation(guard):
                    self.evaluate_command(c)

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
""",
"""x := 0;
while (x < 1000){
    x := x + 1
}
"""]

display = ("Custom", "Example 0", "Example 1", "Example 2")

options = list(range(len(display)))

selection = st.selectbox(
    'Choose a Code Example or try it with your own one.', options, format_func=lambda x: display[x])


code = st.text_area('Older Version: ', example_codes[selection], height=400)
run = st.button('Analyse')


# BEGIN: Display Results

m = Memory({'x': 0, 'y': 0})

if run:
    try:
        result = parser.parse(code)
        m.evaluate_command(result)
        st.write(m)
    except Exception as e:
        st.error(f"{e}")