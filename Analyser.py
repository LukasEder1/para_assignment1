from CustomParser import parser

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
        match expression[0]:
            case 'const':
                return expression[1]
            case 'var':
                return self.get_memory(expression[1])
            case 'binaryOP':
                return self.evaluate(expression[2]) + self.evaluate(expression[3])
    
    def evaluate_bool_expression(self, b):
        pass

    def evaluate_command(self, command):
        pass


if __name__ == '__main__':
    # Build the lexer and try it out
    m = Memory({'x': 1, 'y': 2})
    
