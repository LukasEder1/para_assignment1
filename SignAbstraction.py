from enum import Enum
from DataTypes import *

class val_abs(Enum):
    TOP = 1 # \top
    BOT = 2 # \bot
    POS = 3 # [>= 0],
    NEG = 4 # [<= 0]

class RELOP(Enum):
    LEQ = 1 # <=
    GE = 2 # >


class AbstractMemory():
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
    
    def val_sat(self, operation:RELOP, n:int, v: val_abs) -> bool:
        """
        val_sat over-approximates the effect of
        condition tests
        """
        if v == val_abs.BOT:
            return val_abs.BOT
        
        elif operation == RELOP.LEQ and n < 0:
            return val_abs.BOT if v == val_abs.POS else val_abs.NEG
        
        elif operation == RELOP.GE and n >= 0:
            return val_abs.BOT if v == val_abs.NEG else val_abs.POS
        
        else:
            return v
        
    def abstract_union(self, a: val_abs, b:val_abs) -> val_abs:
        """
        over-approximates concrete unions
        """
        match (a, b):
            case (val_abs.TOP, a) | (a, val_abs.TOP):
                return a
            case (val_abs.TOP, _) | (_, val_abs.TOP) | (val_abs.POS, val_abs.NEG) | (val_abs.NEG, val_abs.POS):
                return val_abs.TOP
            case (val_abs.POS, val_abs.POS):
                return val_abs.POS
            case (val_abs.NEG, val_abs.NEG):
                return val_abs.NEG

    def abstract_addition(self, a: val_abs, b:val_abs) -> val_abs:
        """
        implements +^{\#}
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
        implements -^{\#}
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
        implements *^{\#}
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
            
    def non_relational_bot(self, aenv):
        # sets each variable to BOT
        for k in self.states.keys():
            self.states[k] = val_abs.BOT


    def is_bot(self):
        return val_abs.BOT in self.states.values()
    
    
    
