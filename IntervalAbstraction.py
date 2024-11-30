from copy import deepcopy
from DataTypes import *

TOP = (float('-inf'), float('inf'))
BOT = set()

class AbstractMemoryIntervals:
    #states = {}
    def __init__(self, states:dict):

        self.states = {}
        
        if len(states) > 0:
            if isinstance(states[next(iter(states))], int):
                for k,v in states.items():
                    self.states[k] = (v, v)
            else:
                self.states = states

    def get_memory(self, x: str) -> tuple[int, int]:
        return self.states.get(x, TOP)
    
    def set_memory(self, x: str, t: tuple[float, float]):
        self.states[x] = t

    def __str__(self):
        out = "{ "
        for k, v in self.states.items():
            out += f"{k} -> {v} "
        out += "}"
        return out
    
    def inclusion(self, I1, I2) -> bool:
        a, b = I1
        c, d = I2
        return (a >= c) and (b <= d)
    
    def abstract_union(self, I1, I2):
        if len(I2) == 0:
            return I1 
        if len(I1) == 0:
            return I2
        a, b = I1
        c, d = I2
        return (min(a, c), max(b, d))
    
    def abstract_addition(self, I1, I2):
        if len(I2) == 0 or len(I1) == 0:
            return BOT
        a, b = I1
        c, d = I2
        return (a + c, b + d)
    
    def abstract_subtraction(self, I1, I2):
        if len(I2) == 0 or len(I1) == 0:
            return BOT
        a, b = I1
        c, d = I2
        return (a - d, b - c)
    
    def abstract_times(self, I1, I2):
        if len(I2) == 0 or len(I1) == 0:
            return BOT
        a, b = I1
        c, d = I2
        combinations = [a * c, a * d, b * c, b * d]
        return (min(combinations), max(combinations))
    
    def f_bop(self, binOP, l, r):
        match binOP:
            case '+':
                return self.abstract_addition(l, r)
            case '-':
                return self.abstract_subtraction(l, r)
            case '*':
                return self.abstract_times(l, r)
    
    def set_to_bot_state(self):
        for k in self.states.keys():
            self.states[k] = BOT
    
    def is_bot(self):
        return any(len(v) == 0 for v in self.states.values())
    
    def evaluate_expression(self, expr):
        match expr:
            case number(value):
                return (value, value)
            case variable(name):
                return self.get_memory(name)
            case binaryOperation(bop, expr1, expr2):
                l = self.evaluate_expression(expr1)
                r = self.evaluate_expression(expr2)
                return self.f_bop(bop, l, r)
    
    def evaluate_filter(self, guard):
        I = self.get_memory(guard.var)
        filtered_states = deepcopy(self.states)

        if len(I) > 0:
            a, b = I
            if guard.rel == "<=":
                if a > guard.num:
                    filtered_states = {k: BOT for k in self.states}
                elif a <= guard.num and b >= guard.num:
                    filtered_states[guard.var] = (a, guard.num)
                elif b <= guard.num:
                    pass  
            elif guard.rel == ">":
                if b <= guard.num:
                    filtered_states = {k: BOT for k in self.states}
                elif a <= guard.num and b >= guard.num:
                    filtered_states[guard.var] = (guard.num, b)
                elif a >= guard.num:
                    pass  
        else:
            filtered_states = {k: BOT for k in self.states}
        
        return AbstractMemoryIntervals(filtered_states)
    
    def negate_binary_relation(self, rel: str):
        return ">" if rel == "<=" else "<="
    
    def nr_is_le(self, b):
        r = True
        for k, x in self.states.items():
            r = r and self.inclusion(x, b.get_memory(k))

            if not r:
                break

        return r


    def compute_lfp(self, f):
        a = AbstractMemoryIntervals(deepcopy(self.states))
        #union_memory = AbstractMemoryIntervals(deepcopy(self.states))
        next = f(a)
        
        while True:
            
            if a.nr_is_le(next):
                break

            for k, x in a.states.items():
                a.states[k] = self.abstract_union(x, next.get_memory(k))

            next = f(a)
        
        return a

        
    def evaluate_command(self, cmd):
        if not self.is_bot(): # coalescent product
            match cmd:
                case skip():
                    pass

                case seq(c1, c2):
                    self.evaluate_command(c1)
                    self.evaluate_command(c2)
                
                case assign(var, expr):
                    self.set_memory(var, self.evaluate_expression(expr))
                    
                case input_command(var):
                    self.set_memory(var, TOP)
                    
                case if_else(guard, c1, c2):
                    mem_if = self.evaluate_filter(guard)
                    mem_else = self.evaluate_filter(cond(guard.var, self.negate_binary_relation(guard.rel), guard.num))
                    
                    mem_if.evaluate_command(c1)
                    mem_else.evaluate_command(c2)

                    for k in self.states.keys():
                        self.states[k] = self.abstract_union(mem_if.get_memory(k), mem_else.get_memory(k))

                case while_command(guard, c):
                    print("not yet implemented")
                    """
                    def f_loop(self):
                        mem_f = self.evaluate_filter(guard)
                        mem_f.evaluate_command(c)
                        return mem_f
                    
                    fixed_point = self.compute_lfp(f_loop)
                    
                    fixed_point.evaluate_filter(cond(guard.var, self.negate_binary_relation(guard.rel), guard.num))
                    
                    self.states = fixed_point.states
                    """