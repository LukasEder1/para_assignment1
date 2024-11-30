from enum import Enum
from DataTypes import *
from copy import deepcopy

class val_abs(Enum):
    TOP = 0  # \top
    BOT = 1  # \bot
    POS = 2  # [>= 0]
    NEG = 3  # [<= 0]

def representation_val_abs(v: val_abs):
    match v:
        case val_abs.TOP:
            return "T"
        case val_abs.BOT:
            return "BOTTOM"
        case val_abs.POS:
            return "[>= 0]"
        case val_abs.NEG:
            return "[< 0]"

class AbstractMemory:
    #states = {}
    def __init__(self, states: dict = None):
        self.states = {}

        if states != None:
            for k in states.keys():
                if isinstance(states[k], int):
                    self.states[k] = val_abs.TOP
                else:
                    self.states[k] = states[k] 

        

    def get_memory(self, x):
        return self.states.get(x, val_abs.TOP)
    
    def set_memory(self, x, n):
        self.states[x] = n

    def __str__(self):
        out = "{"
        for k, v in self.states.items():
            out += f"{k} -> {representation_val_abs(v)} "
        out += "}"
        return out

    def inclusion(self, a: val_abs, b: val_abs) -> bool:
        return (a == val_abs.BOT and b == val_abs.BOT) or b == val_abs.TOP or a == b

    def over_approximate(self, n: int) -> val_abs:
        return val_abs.NEG if n < 0 else val_abs.POS

    def val_sat(self, operation: str, n: int, v: val_abs) -> val_abs:
        if v == val_abs.BOT:
            return val_abs.BOT
        elif operation == "<=" and n < 0:
            return val_abs.BOT if v == val_abs.POS else val_abs.NEG
        elif operation == ">" and n >= 0:
            return val_abs.BOT if v == val_abs.NEG else val_abs.POS
        else:
            return v

    def abstract_union(self, a: val_abs, b: val_abs) -> val_abs:
        match (a, b):
            case (val_abs.BOT, a) | (a, val_abs.BOT):
                return a
            case (val_abs.TOP, _) | (_, val_abs.TOP) | (val_abs.POS, val_abs.NEG) | (val_abs.NEG, val_abs.POS):
                return val_abs.TOP
            case (val_abs.POS, val_abs.POS):
                return val_abs.POS
            case (val_abs.NEG, val_abs.NEG):
                return val_abs.NEG

    def abstract_addition(self, a: val_abs, b: val_abs) -> val_abs:
        match (a, b):
            case (val_abs.BOT, _) | (_, val_abs.BOT):
                return val_abs.BOT
            case (val_abs.POS, val_abs.POS):
                return val_abs.POS
            case (val_abs.NEG, val_abs.NEG):
                return val_abs.NEG
            case (_, _):
                return val_abs.TOP

    def abstract_subtraction(self, a: val_abs, b: val_abs) -> val_abs:
        match (a, b):
            case (val_abs.BOT, _) | (_, val_abs.BOT):
                return val_abs.BOT
            case (val_abs.POS, val_abs.NEG):
                return val_abs.POS
            case (val_abs.NEG, val_abs.POS):
                return val_abs.NEG
            case (_, _):
                return val_abs.TOP

    def abstract_times(self, a: val_abs, b: val_abs) -> val_abs:
        match (a, b):
            case (val_abs.BOT, _) | (_, val_abs.BOT):
                return val_abs.BOT
            case (val_abs.POS, val_abs.POS) | (val_abs.NEG, val_abs.NEG):
                return val_abs.POS
            case (val_abs.NEG, val_abs.POS) | (val_abs.POS, val_abs.NEG):
                return val_abs.NEG
            case (_, _):
                return val_abs.TOP

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
            self.states[k] = val_abs.BOT

    def is_bot(self):
        return val_abs.BOT in self.states.values()

    def evaluate_expression(self, expr: expression):
        match expr:
            case number(value):
                return self.over_approximate(value)
            case variable(name):
                return self.get_memory(name)
            case binaryOperation(bop, expr1, expr2):
                l = self.evaluate_expression(expr1)
                r = self.evaluate_expression(expr2)
                return self.f_bop(bop, l, r)

    def evaluate_filter(self, guard: cond):
        result = self.val_sat(guard.rel, guard.num, self.get_memory(guard.var))
        
        filtered_states = deepcopy(self.states)

        if result == val_abs.BOT:
            filtered_states = {k: val_abs.BOT for k in self.states}
        else:
            filtered_states[guard.var] = result

        return AbstractMemory(filtered_states)

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
        a = AbstractMemory(deepcopy(self.states))
        
        next = f(a)
        
        if a.nr_is_le(next):
            
            return a
        else:
            union_memory = AbstractMemory(deepcopy(self.states))

            for k, x in a.states.items():
                union_memory.states[k] = self.abstract_union(x, next.get_memory(k))
            return union_memory.compute_lfp(f)


    def evaluate_command(self, cmd: command):
        if not self.is_bot():
            match cmd:
                case skip():
                    pass

                case seq(c1, c2):
                    self.evaluate_command(c1)
                    self.evaluate_command(c2)
                
                case assign(var, expr):
                    self.set_memory(var, self.evaluate_expression(expr))
                    
                case input_command(var):
                    self.set_memory(var, val_abs.TOP)
                    
                case if_else(guard, c1, c2):
                    
                    mem_if = self.evaluate_filter(guard)
                    
                    mem_else = self.evaluate_filter(cond(guard.var, self.negate_binary_relation(guard.rel), guard.num))
                    
                    mem_if.evaluate_command(c1)
                    mem_else.evaluate_command(c2)

                    for k in self.states.keys():
                        self.states[k] = self.abstract_union(mem_if.get_memory(k), mem_else.get_memory(k))

                case while_command(guard, c):
                    
                    def f_loop(self):
                        mem_f = self.evaluate_filter(guard)
                        mem_f.evaluate_command(c)
                        return mem_f
                    
                    fixed_point = self.compute_lfp(f_loop)
                    
                    fixed_point.evaluate_filter(cond(guard.var, self.negate_binary_relation(guard.rel), guard.num))
                    
                    self.states = fixed_point.states