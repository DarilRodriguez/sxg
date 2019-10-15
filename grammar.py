from expressions import ExpressionAnalyzer
from lexer import Lexer, Token

class GNode:
    NONE = -1
    DEF = 0
    COND = 1
    REPEAT = 2
    LIT = 3
    OPT = 4
    
    def __init__(self, type, childs, key=""):
        self.type, self.childs, self.key = type, childs, key

class Grammar:
    def __init__(self):
        self.list = []
        self.pos = -1
        self.last_token = Token(Token.UNKNOW)
        
        self.defs = {}
        self.pre_defs = {
            'IDENT': self._ident,
            'NUMBER': self._number,
            'STRING': self._string,
            'EOL': self._eol,
            'EXPR': self._expr,
        }
    
    def load_def(self, line, line_number=0):
        ret = GDefReader.parse(line, line_number)
        self.add_def(ret.key, ret)
    
    def add_def(self, name, gnode):
        self.defs[name] = gnode
    
    def set_line(self, line):
        self.list = Lexer.from_line(line)
        self.pos = -1
        
    def next_tok(self):
        self.pos += 1
        if self.pos < len(self.list):
            self.last_token = self.list[self.pos]
            return self.list[self.pos]
        
        tok = Token(Token.EOL, "")
        tok.pos = self.pos
        return tok
        
    def _next_tok(self):
        if self.pos + 1 < len(self.list):
            self.last_token = self.list[self.pos + 1]
            return self.list[self.pos + 1]
        
        tok = Token(Token.EOL, "")
        tok.pos = self.pos
        return tok
    
    def _next_token_type(self, type):
        tok = self._next_tok()
        
        if tok == type:
            self.pos += 1
            return tok.literal
        
        return False
    
    def _ident(self):
        return self._next_token_type(Token.IDENT)
    
    def _number(self):
        return self._next_token_type(Token.NUMBER)
    
    def _string(self):
        return self._next_token_type(Token.STRING)
    
    def _eol(self):
        return self._next_token_type(Token.EOL)
    
    def _expr(self):
        return ExpressionAnalyzer(self).get()
    
    def _execute_gnode(self, gnode, data={}):
        if gnode.type == GNode.NONE:
            for child in gnode.childs:
                info = {}
                ret = self._execute_gnode(child, info)
                
                if not ret:
                    return False
                
                if info.has_key('__type__') and info['__type__'] == 'value':
                    if child.key != "":
                        data[child.key] = info['value']
                    
                elif child.key != "":
                    data[child.key] = info
            
            return True
        
        elif gnode.type == GNode.DEF:
            data['__type__'] = 'value'
            data['value'] = ''
            
            if gnode.childs in self.pre_defs.keys():
                ret = self.pre_defs[gnode.childs]()
                
                if ret != False:
                    data['value'] = ret
                    return True
                
                else:
                    return False
            
            else:
                info = {}
                ret = self._check(gnode.childs, info)
                
                if ret:
                    if info.has_key("__type__") and info["__type__"] == "value":
                        data['value'] = info['value']
                    else:
                        data['value'] = info
                    
                    return True
                
                return False
        
        elif gnode.type == GNode.REPEAT:
            data["__type__"] = "value"
            data["value"] = []
            
            stop = False
            while not stop:
                info = {}
                ret = self._execute_gnode(gnode.childs, info)
                
                if ret:
                    if info.has_key("__type__") and info["__type__"] == "value":
                        if info["value"] == None:
                            stop = True
                        
                        else:
                            data["value"].append(info["value"])
                
                else:
                    break
            
            return True
        
        elif gnode.type == GNode.LIT:
            tok = self._next_tok()
            
            if tok.literal == gnode.childs:
                self.pos += 1
                data["__type__"] = "value"
                data["value"] = tok.literal
                return True
            
            return False
        
        elif gnode.type == GNode.COND:
            info = {}
            pos = self.pos
            ret = self._execute_gnode(GNode(GNode.NONE, gnode.childs), info)
            
            if ret:
                data['__type__'] = "value"
                
                if info.has_key("__type__") and info["__type__"] == "value":
                    data['value'] = info['value']
                
                else:
                    data['value'] = info
                
                return True
            
            self.pos = pos
            return False
        
        elif gnode.type == GNode.OPT:
            data['__type__'] = "value"
            data['value'] = None
            
            for t in gnode.childs:
                info = {}
                if self._execute_gnode(t, info):
                    if info.has_key("__type__") and info['__type__'] == "value":
                        data['value'] = info["value"]
                    
                    else:
                        data["value"] = info
                    
                    return True
            
            return True
        
        return False
    
    def _check(self, def_name, data):
        info = {}
        if self.parse(def_name, info):
            data['__type__'] = "value"
            
            if info.has_key("__type__") and info["__type__"] == "value":
                data['value'] = info['value']
            else:
                data['value'] = info
                
            return True
        return False
    
    def parse(self, def_name, data):
        pos = self.pos
        if def_name in self.defs.keys():
            data["__name__"] = def_name
            ret = self._execute_gnode(self.defs[def_name], data)
            
            if not ret:
                self.pos = pos
            
            return ret
            
        else:
            print "GRAMMAR: '%s' not defined" %def_name
        
        return False
    
    def parse_line(self, line, def_name):
        info = {}
        self.set_line(line)
        ret = self.parse(def_name, info)
        
        return ret, info
    
class GDefReader:
    def __init__(self, line):
        self.grm = Grammar()
        self.grm.set_line(line)
        self.line_number = 0
        self.root = GNode(GNode.NONE, [], '')
    
    def _next_gnode(self):
        tok = self.grm.next_tok()
        
        if tok == Token.STRING:
            vtok = self.grm._next_token_type(Token.ASSIGN)
            
            if vtok:
                ntok = self._next_gnode()
                
                if ntok:
                    ntok.key = tok.literal
                    
                    return ntok
                    
                else:
                    raise Exception("GRAMMAR: Expected token after '=' at %i:%i" %(
                        self.line_number,
                        self.grm._next_tok().pos
                    ))
            
            else:
                return GNode(GNode.LIT, tok.literal)
        
        elif tok == Token.MUL:
            ntok = self._next_gnode()
            
            if ntok:
                return GNode(GNode.REPEAT, ntok)
                
            else:
                raise Exception("GRAMMAR: Expected token after '*' at %i:%i" %(
                    self.line_number,
                    self.grm._next_tok().pos
                ))
        
        elif tok == Token.IDENT:
            return GNode(GNode.DEF, tok.literal)
        
        elif tok == Token.LPAREN:
            lst = []
            
            gn = self._next_gnode()
            while gn != False and gn != -2:
                lst.append(gn)
                if gn == -2:
                    raise Exception("GRAMMAR: Unexpected ')' at %i:%i" %(
                        self.line_number,
                        self.grm._next_tok().pos
                    ))
                if gn == -3:
                    raise Exception("GRAMMAR: Unexpected ']' at %i:%i" %(
                        self.line_number,
                        self.grm._next_tok().pos
                    ))
                
                gn = self._next_gnode()
            
            return GNode(GNode.COND, lst)
        
        elif tok == Token.RPAREN:
            return -2
        
        elif tok == Token.RBRACK:
            return -3
        
        elif tok == Token.LBRACK:
            lst = []
            
            gn = self._next_gnode()
            while gn != False and gn != -3:
                lst.append(gn)
                if gn == -2:
                    raise Exception("GRAMMAR: Unexpected ')' at %i:%i" %(
                        self.line_number,
                        self.grm._next_tok().pos
                    ))
                if gn == -3:
                    raise Exception("GRAMMAR: Unexpected ']' at %i:%i" %(
                        self.line_number,
                        self.grm._next_tok().pos
                    ))
                
                gn = self._next_gnode()
            
            return GNode(GNode.OPT, lst)
        
        elif tok == Token.EOL:
            return False
        
        else:
            raise Exception("GRAMMAR: Invalid selector '%s' at %i:%i" %(
                tok.literal,
                self.line_number,
                self.grm._next_tok().pos
            ))
        
        return False
    
    def _load(self, log_all=True):
        ret = self.grm._ident()
        
        if ret:
            self.root.key = ret
        else:
            if log_all:
                raise Exception("GRAMMAR: Expected IDENT at %i:%i" %(
                    self.line_number,
                    self.grm._next_tok().pos
                ))
            
            else:
                return False
        
        ret = self.grm._next_token_type(Token.COLON)
        
        if not ret:
            if log_all:
                raise Exception("GRAMMAR: Expected COLON(':') at %i:%i" %(
                    self.line_number,
                    self.grm._next_tok().pos
                ))
            
            else:
                return False
        
        ret = self._next_gnode()
        while ret != False:
            if ret == -2:
                raise Exception("GRAMMAR: Unexpected sym at %i:%i" %(
                    self.line_number,
                    self.grm._next_tok().pos
                ))
            
            self.root.childs.append(ret)
            ret = self._next_gnode()
        
        return self.root
    
    @staticmethod
    def parse(line, line_number=0):
        gdr = GDefReader(line)
        gdr.line_number = line_number
        gdr._load(False)
        return gdr.root
