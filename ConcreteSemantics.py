from DataTypes import *
from random import randint

def f_bop(binOP, l, r):
    match binOP:
        case '+':
            return l + r
        case '-':
            return l - r
        case '*':
            return l * r 

    
class Memory():
    

    def __init__(self, states=None):
        states = {}
        
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
                self.set_memory(var, randint(-20, 20))
            case if_else(guard, c1, c2):
                if self.evaluate_binary_relation(guard):
                    self.evaluate_command(c1)
                else:
                    self.evaluate_command(c2)
            case while_command(guard, c):
                while self.evaluate_binary_relation(guard):
                    self.evaluate_command(c)
            
