from lexer import Token

_COUNT = -1
def auto():
    global _COUNT
    _COUNT += 1
    return _COUNT

class ExpressionAnalyzer:
    def __init__(self, gscan):
        self.gscan = gscan
        self.start_pos = self.gscan.pos
    
    def get_next(self):
        data = {}
        
        if self.gscan.parse("expr_val", data=data):
            if data['val'] == None:
                if self.gscan.parse("expr_op", data=data):
                    if data['op'] == None:						
                        if self.gscan._next_tok() == Token.RPAREN:
                            self.gscan.pos += 1
                            return "RPAREN"
                        
                        elif self.gscan._next_tok() == Token.LPAREN:
                            self.gscan.pos += 1
                            lst = []
                            next = self.get_next()
                            while next != None and next != "RPAREN":
                                lst.append(next)
                                next = self.get_next()
                            
                            return Operand('', Operand.PARENT, lst)
                            
                        return None
                    
                    # is operator
                    return Operand('', Operand.OPERATION, data['op'])
                
                return None
            
            # is value
            op = Operand('', None, None)
            
            if data['val']['__name__'] == "expr_new":
                op.type = Operand.INSTANCING
                op.data = data['val']['val']
            
            elif data['val']['__name__'] == "func_call":
                op.type = Operand.FUNCTION
                op.data = data['val']
            
            elif data['val']['__name__'] == "dotted_name":
                op.type = Operand.VARIABLE
                op.data = data['val']
            
            elif data['val']['__name__'] == "literal_str":
                op.type = Operand.STRING
                op.data = data['val']
            
            elif data['val']['__name__'] == "literal_num":
                op.type = Operand.NUMBER
                op.data = data['val']
            
            else:
                print data['val']
            
            return op
        
        return None
    
    def get(self):
        lst = []
        next = self.get_next()
        while next != None and next != "RPAREN":
            lst.append(next)
            next = self.get_next()
        
        if next == "RPAREN":
            self.gscan.pos -= 1
        
        if len(lst) == 0:
            return False
        
        return lst

class Operand:
    NUMBER = auto()
    STRING = auto()
    VARIABLE = auto()
    FUNCTION = auto()
    PARENT = auto()
    OPERATION = auto()
    INSTANCING = auto()
    
    def __init__(self, sign, type, data):
        self.sign = sign
        self.type = type
        self.data = data

    def __str__(self):
        t = ""
        lst = Operand.__dict__
        
        for n in lst:
            if lst[n] == self.type:
                t = n
                break
        
        return "Operand(%s, %s, %s)" %(self.sign, t, self.data)