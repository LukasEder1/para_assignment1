from enum import Enum
from DataTypes import *
import copy


class val_abs(Enum):
    TOP = 0 # \top
    BOT = 1 # \bot
    POS = 2 # [>= 0],
    NEG = 3 # [<= 0]

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

class RELOP(Enum):
    Cinfeq = 1 # <=
    Csup = 2 # >


class AbstractMemory():
    states = {}

    def __init__(self, states:dict=None):
        if states != None:
            for k in states.keys():
                self.states[k] = val_abs.TOP 

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
    
    def inclusion(self, a :val_abs, b: val_abs) -> bool:
        # Return true if a \sqsubseteq b
        return (
            (a == val_abs.BOT and b == val_abs.BOT) 
            or b == val_abs.TOP
            or a == b
        )

    def over_approximate(self, n: int) -> bool:
        # phi_v(n)
        return val_abs.NEG if n < 0 else val_abs.POS
    
    def val_sat(self, operation:str, n:int, v: val_abs) -> val_abs:
        """
        val_sat over-approximates the effect of
        condition tests
        """
        if v == val_abs.BOT:
            return val_abs.BOT
        #TODO: 
        elif operation == "<=" and n < 0:
            return val_abs.BOT if v == val_abs.POS else val_abs.NEG
        
        elif operation == ">"and n >= 0:
            return val_abs.BOT if v == val_abs.NEG else val_abs.POS
        
        else:
            return v
        
    def abstract_union(self, a: val_abs, b:val_abs) -> val_abs:
        """
        over-approximates concrete unions
        """
        match (a, b):
            case (val_abs.BOT, a) | (a, val_abs.BOT):
                return a
            case (val_abs.TOP, _) | (_, val_abs.TOP) | (val_abs.POS, val_abs.NEG) | (val_abs.NEG, val_abs.POS):
                return val_abs.TOP
            case (val_abs.POS, val_abs.POS):
                return val_abs.POS
            case (val_abs.NEG, val_abs.NEG):
                return val_abs.NEG
            
    def abstract_addition(self, a: val_abs, b:val_abs) -> val_abs:
        """
        implements +^#
        """
        match (a, b):
            case (val_abs.BOT, _) | (_, val_abs.BOT):
                return val_abs.BOT
            case (val_abs.POS, val_abs.POS):
                return val_abs.POS
            case (val_abs.NEG, val_abs.NEG):
                return val_abs.NEG
            case (_, _):
                return val_abs.TOP
            

    def abstract_substraction(self, a: val_abs, b:val_abs) -> val_abs:
        """
        implements -#
        """
        match (a, b):
            case (val_abs.BOT, _) | (_, val_abs.BOT):
                return val_abs.BOT
            case (val_abs.POS, val_abs.NEG):
                return val_abs.POS
            case (val_abs.NEG, val_abs.POS):
                return val_abs.NEG
            case (_, _):
                return val_abs.TOP
            
    def abstract_times(self, a: val_abs, b:val_abs) -> val_abs:
        """
        implements *#
        """
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
                return self.abstract_substraction(l, r)
            case '*':
                return self.abstract_times(l, r)
            
    def set_to_bot_state(self):
        ai_mem = copy.deepcopy(self.states)
        # sets each variable to BOT
        for k in ai_mem.keys():
            ai_mem[k] = val_abs.BOT
        return ai_mem

    def is_bot(self):
        return val_abs.BOT in self.states.values()
    
    def evaluate_expression(self, expr: expression):
        match expr:
            case number(value):
                return self.over_approximate(value)
            case variable(name):
                return self.get_memory(name)
            case binaryOperation(bop, expr1, expr2):
                #if isinstance(expr1, number) and expr1.value == 0:
                #    return self.evaluate_expression(expr2)
                #if isinstance(expr2, number) and expr2.value == 0:
                #    return self.evaluate_expression(expr1)
                l = self.evaluate_expression(expr1)
                r = self.evaluate_expression(expr2)
                return self.f_bop(bop,l, r)
    
    def evaluate_filter(self, guard: cond):
        result = self.val_sat(guard.rel, guard.num, self.get_memory(guard.var))
        #print(guard.rel, guard.num, self.get_memory(guard.var))
        #print(guard, " ", result)
        ai_mem = copy.deepcopy(self.states)
        # check if guard is feasable
        if result == val_abs.BOT:
            return self.set_to_bot_state()
        else:
            ai_mem[guard.var] = result
            return ai_mem

    #def less_than_equals(self, a, b):


    def compute_least_fix_point(f, a):
        pass
        

    def negate_binary_relation(self, rel: str):
        return ">" if rel == "<=" else "<="


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
                    x, b, n = guard.get_elements()

                    mem_if = self.evaluate_filter(guard)
                    mem_else = self.evaluate_filter(cond(x, self.negate_binary_relation(b), n))
                    self.evaluate_command_tmp(c1, mem_if),
                    self.evaluate_command_tmp(c2, mem_else)
                    for k, v in mem_if.items():
                        self.states[k] = self.abstract_union(v, mem_else[k])
                    

                case while_command(guard, c):
                    pass
            
    def evaluate_command_tmp(self, cmd: command, memory: dict):
        if not self.is_bot():
            match cmd:
                case skip():
                    pass

                case seq(c1, c2):
                    self.evaluate_command_tmp(c1, memory)
                    self.evaluate_command_tmp(c2, memory)
                    
                case assign(var, expr):
                    #print("1: ", memory)
                    memory[var] = self.evaluate_expression(expr)
                    #print("2: ", memory)

                case input_command(var):
                    memory[var] =  val_abs.TOP
                

                case if_else(guard, c1, c2):
                    x, b, n = guard.get_elements()

                    mem_if = self.evaluate_filter(guard)
                    mem_else = self.evaluate_filter(cond(x, self.negate_binary_relation(b), n))
                    self.evaluate_command_tmp(c1, mem_if),
                    self.evaluate_command_tmp(c2, mem_else)

                    for k, v in mem_if.items():
                        memory[k] = self.abstract_union(v, mem_else[k])
                    