from enum import Enum
from DataTypes import *
import copy


@dataclass
class interval():
    first: int
    second: int

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __str__(self):
        return f"[{self.first}, {self.second}]"
            

class RELOP(Enum):
    Cinfeq = 1 # <=
    Csup = 2 # >

TOP = (float('-inf'), float('inf'))
BOT = set()

class AbstractMemoryIntervals():
    states = {}

    def __init__(self, states:dict=None):
        if states != None:
            for k in states.keys():
                self.states[k] =  TOP

    def get_memory(self, x: variable):
        return self.states.get(x, TOP)
    
    def set_memory(self, x:variable, t: tuple[number, number]):
        self.states[x] = t

    def set_memory_element_wise(self, x:variable, first, second):
        self.states[x] = first, second

    def __str__(self):
        out = "{ "
        for k, v in self.states.items():
            out += f"{k} -> {v} "
        out += "}"

        return out
    
    def inclusion(self, I1 , I2) -> bool:
        # Return true if I1 \sqsubseteq I2
        a, b = I1
        c, d = I2
        return (a >= c) and (b <= d)

        
    def abstract_union(self,  I1 , I2):
        """
        over-approximates concrete unions
        """
        if len(I2) == 0:
            return I1 
            
        if len(I1) == 0:
            return I2
        
        a,b = I1
        c,d = I2
        print(I1, I2)
        return (min(a, c), max(b, d))
            
    def abstract_addition(self, I1 , I2):
        """
        implements +^#
        """
        # BOT + BOT
        if len(I2) == 0 or len(I1) == 0:
            return set()
        
        a, b = I1
        c, d = I2
             

        return (a+c, b+d)
            

    def abstract_substraction(self, I1 , I2):
        """
        implements -^#
        """
        if len(I2) == 0 or len(I1) == 0:
            return set()
        
        a, b = I1
        c, d = I2
        return (a-d, b-c)
            
    def abstract_times(self, I1 , I2):
        """
        implements *^#
        """
        if len(I2) == 0 or len(I1) == 0:
            return set()
        
        a, b = I1
        c, d = I2
        combinations = [a*c, a*d, b*c, d*b]
        return (min(combinations), max(combinations))
    
    def f_bop(self, binOP, l, r):
        match binOP:
            case '+':
                return self.abstract_addition(l, r)
            case '-':
                return self.abstract_substraction(l, r)
            case '*':
                return self.abstract_times(l, r)
            
    def set_to_bot_state(self, memory):
        ai_mem = copy.deepcopy(memory)
        # sets each variable to BOT
        for k in ai_mem.keys():
            ai_mem[k] = BOT
        return ai_mem

    def is_bot(self, memory):
        contains_bot = False
        for _, v in memory.items():
            if len(v) == 0:
                contains_bot = True
                break
        return contains_bot
    
    def evaluate_expression(self, expr: expression, memory):
        match expr:
            case number(value):
                return (value, value)
            case variable(name):
                return memory[name]
            case binaryOperation(bop, expr1, expr2):
                l = self.evaluate_expression(expr1, memory)
                r = self.evaluate_expression(expr2, memory)
                return self.f_bop(bop,l, r)
    
    def evaluate_filter(self, guard: cond, memory):
        I = memory.get(guard.var, TOP)
  
        ai_mem = copy.deepcopy(memory)

        if len(I) > 0:
            a, b = I

            # x <= 0
            # M#(X) -> (-2, 10)
            if guard.rel == "<=":
                if a > guard.num:
                    return self.set_to_bot_state(memory)
                elif a <= guard.num and b >= guard.num:
                    ai_mem[guard.var] = (a, guard.num)
                    return ai_mem
                elif b <= guard.num:
                    return ai_mem
            
            # x > 10
            # M#(X) -> (8, 12)
            elif guard.rel == ">":
                if b <= guard.num:
                    return self.set_to_bot_state(memory)
                elif a <= guard.num and b >= guard.num:
                    ai_mem[guard.var] = (guard.num, b)
                    return ai_mem
                elif a >= guard.num:
                    return ai_mem
        else:
            return self.set_to_bot_state(memory)


    def negate_binary_relation(self, rel: str):
        return ">" if rel == "<=" else "<="


    def evaluate_command(self, cmd: command):
        if not self.is_bot(self.states):
            match cmd:
                case skip():
                    pass

                case seq(c1, c2):
                    self.evaluate_command(c1)
                    self.evaluate_command(c2)
                
                case assign(var, expr):
                    self.set_memory(var, self.evaluate_expression(expr, self.states))
                    
                case input_command(var):
                    self.set_memory(var, TOP)
                    
                case if_else(guard, c1, c2):
                    x, b, n = guard.get_elements()

                    mem_if = self.evaluate_filter(guard, self.states)

                    mem_else = self.evaluate_filter(cond(x, self.negate_binary_relation(b), n), self.states)

                    self.evaluate_command_tmp(c1, mem_if),
                    self.evaluate_command_tmp(c2, mem_else)

                    for k, v in mem_if.items():
                        self.states[k] = self.abstract_union(v, mem_else[k])
                    
            
    def evaluate_command_tmp(self, cmd: command, memory: dict):
        if not self.is_bot(memory): # coalescent product
            match cmd:
                case skip():
                    pass

                case seq(c1, c2):
                    self.evaluate_command_tmp(c1, memory)
                    self.evaluate_command_tmp(c2, memory)
                    
                case assign(var, expr):
                    memory[var] = self.evaluate_expression(expr, memory)
                case input_command(var):
                    memory[var] =  TOP
                
                case if_else(guard, c1, c2):
                    x, b, n = guard.get_elements()

                    mem_if = self.evaluate_filter(guard, memory)

                    mem_else = self.evaluate_filter(cond(x, self.negate_binary_relation(b), n), memory)

                    self.evaluate_command_tmp(c1, mem_if),
                    self.evaluate_command_tmp(c2, mem_else)

                    for k, v in mem_if.items():
                        memory[k] = self.abstract_union(v, mem_else[k])
