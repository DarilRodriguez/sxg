_COUNT = -2

def auto():
    global _COUNT
    _COUNT += 1
    return _COUNT

class Token:
	# Token names are from the golang source code
	EOL = (auto(), "")
	UNKNOW = (auto(),)
	IDENT = (auto(),)
	NUMBER = (auto(),)
	STRING = (auto(),)

	COMMENT = (auto(),)

	DECORATOR = (auto(), "@")
	
	ADD = (auto(), "+")
	SUB = (auto(), "-")
	MUL = (auto(), "*")
	QUO = (auto(), "/")
	REM = (auto(), "%")

	AND = (auto(), "&")
	OR = (auto(), "|")
	SHL = (auto(), "<<")
	SHR = (auto(), ">>")
		
	ADD_ASSIGN = (auto(), "+=")
	SUB_ASSIGN = (auto(), "-=")
	MUL_ASSIGN = (auto(), "*=")
	DIV_ASSIGN = (auto(), "/=")
	AND_ASSIGN = (auto(), "&=")
	OR_ASSIGN = (auto(), "|=")
	SHL_ASSIGN = (auto(), "<<=")
	SHR_ASSIGN = (auto(), ">>=")

	LAND = (auto(), "&&")
	LOR = (auto(), "||")
	INC = (auto(), "++")
	DEC = (auto(), "--")

	EQL = (auto(), "==")
	LSS = (auto(), "<")
	GTR = (auto(), ">")
	ASSIGN = (auto(), "=")

	NEQ = (auto(), "!=")
	LEQ = (auto(), "<=")
	GEQ = (auto(), ">=")
	DEFINE = (auto(), ":=")
	ELLIPSIS = (auto(), "...")

	LPAREN = (auto(), "(")
	LBRACK = (auto(), "[")
	LBRACE = (auto(), "{")
	POINT = (auto(), ".")
	COMMA = (auto(), ",")

	RPAREN = (auto(), ")")
	RBRACK = (auto(), "]")
	RBRACE = (auto(), "}")
	COLON = (auto(), ":")
	SEMICOLON = (auto(), ";")

	# used for Translator
	KEYWORD = (auto(),)
	TYPEDEF = (auto(),)
	NAME = (auto(),)

	def __init__(self, type=(0,), literal="", pos=0):
		self.type = type
		self.literal = literal
		self.pos = pos

	def __eq__(self, t):
		if type(t) == tuple:
			return self.type[0] == t[0]

		else:
			return self.type[0] == t.type[0]
		
	def __ne__(self, t):
		if type(t) == tuple:
			return self.type[0] != t[0]

		else:
			return self.type[0] != t.type[0]
    
	def __str__(self):
		n = Token.__dict__
		t = "UNKNOW"

		for k in n:
			if k[:1] == "_":
				continue

			if type(n[k]) == tuple and n[k][0] == self.type[0]:
				t = k

		return "%s(literal=\"%s\")" %(t, self.literal)
        
	@staticmethod
	def from_literal(lit):
		n = Token.__dict__
		t = "UNKNOW"

		for k in n:
			if k[:1] == "_":
				continue

			if type(n[k]) == tuple and len(n[k]) >= 2:
				if callable(n[k][1]):
					if n[k][1](lit):
						t = k

				elif n[k][1] == lit:
					t = k

		return Token(type=n[t], literal=lit)

class TokenScanner:
    def __init__(self, line):
        self.line = line
        self.pos = -1
        self.ignore = [" ", "\t"]
        self.scape = "\\"
        self.eol = ["\n", ";"]
    
    def _check_scape(self):
        pass
    
    def _get_string(self, end):
        acc = ""
        ch = self.next_char()
        
        while ch != end:
            acc += ch
            ch = self.next_char()
            
            if ch == "":
                # ERROR End Of Line while scanning string
                raise SyntaxError("EOL while scanning string")
                pass
        
        return acc
    
    def _get_number(self):
        acc = ""
        ch = self.line[self.pos]
        
        while ch.isdigit():
            acc += ch
            ch = self.next_char()
        
        self.pos -= 1
        return acc
    
    def _get_ident(self):
        acc = ""
        ch = self.line[self.pos]
        
        while ch.isalnum() or ch == "_":
            acc += ch
            ch = self.next_char()
        
        self.pos -= 1
        return acc
    
    def next_char(self):
        self.pos += 1
        
        if self.pos >= len(self.line):
            return ""
        
        ch = self.line[self.pos]
        
        return ch
        
    def back(self, n):
        self.pos -= n
    
    def next_c(self, count):
        out = ""
        
        c = self.next_char()
        while c in self.ignore:
            c = self.next_char()
            
            if c == "":
                return ""
        
        self.back(1)
        for x in xrange(count):
            out += self.next_char()
        
        return out
    
    def next(self):
        lit = self.next_c(3)
        tok = Token.from_literal(lit)
        tok.pos = self.pos
        
        if tok == Token.EOL:
            return tok
        
        if tok != Token.UNKNOW and len(tok.literal) == 3:
            return tok
        
        self.back(3)
        
        lit = self.next_c(2)
		
        tok = Token.from_literal(lit)
        tok.pos = self.pos
		
        if tok == Token.EOL:
            return tok
        
        if tok != Token.UNKNOW and len(tok.literal) == 2:
            return tok
        
        self.back(2)
        
        lit = self.next_c(1)
        
        tok = Token.from_literal(lit)
        tok.pos = self.pos
        pos = self.pos
        
        if tok == Token.EOL:    
            tok.pos = self.pos
            return tok
        
        if tok != Token.UNKNOW:
            return tok
        
        if lit == "_" or lit.isalpha():
            tok = Token(type=Token.IDENT, literal=self._get_ident())
            tok.pos = pos
		
        elif lit.isdigit():
            tok = Token(type=Token.NUMBER, literal=self._get_number())
            tok.pos = pos
            
        elif lit == "\"" or lit == "'":
            tok = Token(type=Token.STRING, literal=self._get_string(lit))
            tok.pos = pos
        
        elif lit == "#":
            tok = Token(type=Token.COMMENT, literal=self.line[self.pos:])
            #self.pos = len(self.line)
		
        elif lit in self.eol:
            tok = Token(type=Token.EOL, literal=lit)
            tok.pos = pos
		
        return tok

class Lexer:
    @staticmethod
    def from_line(line):
        out = []
        scan = TokenScanner(line)
        
        tok = scan.next()
        while tok != Token.EOL:
            out.append(tok)
            tok = scan.next()
        
        return out
