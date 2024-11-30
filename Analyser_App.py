
import MyLexer
import builtins
from MyParser import *
from SignAbstraction import AbstractMemory
from IntervalAbstraction import AbstractMemoryIntervals
from ConcreteSemantics import Memory

import streamlit as st


#st.header("These headers have rotating dividers", divider=True)

# Call the function to get user input
st.set_page_config(page_title="Static Analysis Tool", page_icon="💠", layout="wide")
st.header(":blue[Static] Analysis Tool", divider=True)

example_codes = ["",
"""x:=8;
y:=1;
if (x <= 0){
    y := 0
} else {
   skip 
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

code = st.text_area('Code: ', example_codes[selection], height=200)
run = st.button('Analyse')


# BEGIN: Display Results
pre_condition = {'x': 10, 'y': 0}
m = Memory(pre_condition)
am = AbstractMemory(pre_condition)
am_i = AbstractMemoryIntervals(pre_condition)
if run:
    try:
        result = parser.parse(code)
        m.evaluate_command(result)
        st.write("Concrete: ", m)
        am.evaluate_command(result)
        st.write("Sign: ",am)
        am_i.evaluate_command(result)
        st.write("Interval: ", am_i)

        st.write("Code was parsed as: ",result)
        
    except SyntaxError as e:
        st.error(f"{e}")