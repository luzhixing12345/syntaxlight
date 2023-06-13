

INTEGER       = 'INTEGER' # 整数类型
REAL          = 'REAL'    # 浮点数类型
INTEGER_CONST = 'INTEGER_CONST' # 整数常量
REAL_CONST    = 'REAL_CONST' # 浮点数常量
PLUS          = 'PLUS'
MINUS         = 'MINUS'
MUL           = 'MUL'
INTEGER_DIV   = 'INTEGER_DIV' # 整数除法(DIV保留关键字)
FLOAT_DIV     = 'FLOAT_DIV' # /
LPAREN        = 'LPAREN'
RPAREN        = 'RPAREN'
ID            = 'ID'
ASSIGN        = 'ASSIGN'
BEGIN         = 'BEGIN'
END           = 'END'
SEMI          = 'SEMI'
DOT           = 'DOT'
PROGRAM       = 'PROGRAM'
VAR           = 'VAR'
COLON         = 'COLON'
COMMA         = 'COMMA'
EOF           = 'EOF'

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER_CONST, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


RESERVED_KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
}


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char:str = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
            
    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()

    def number(self):
        """Return a (multidigit) integer or float consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

            token = Token('REAL_CONST', float(result))
        else:
            token = Token('INTEGER_CONST', int(result))
            
        return token

    def peek(self):
        peek_pos = self.pos+1
        if peek_pos > len(self.text)-1:
            return None
        else:
            return self.text[peek_pos]
        
    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        result = result.upper()
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token
        
        
    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            
            if self.current_char.isspace():
                # include '\n'
                self.skip_whitespace()
                continue
                        
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')
            
            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')
            
            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':')
            
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(FLOAT_DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            
            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')
            
            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Compound(AST):
    """Represents a 'BEGIN ... END' block"""
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """The Var node is constructed out of ID token."""
    def __init__(self, token):
        self.token = token
        self.value = token.value
        
class NoOp(AST):
    pass


class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block
        
class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement
        
class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node
        
class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    def __init__(self, lexer:Lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        """
        program : PROGRAM variable SEMI block DOT
        """
        self.eat(PROGRAM)
        var_node = self.variable()        
        program_name = var_node.value
        self.eat(SEMI)
        block_node = self.block()
        self.eat(DOT)
        program_node = Program(program_name,block_node)
        return program_node
    
    def block(self):
        """
        block : declarations compound_statement
        """
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes,compound_statement_node)
        return node

    def declarations(self):
        """
        declarations : VAR (variable_declaration SEMI)*
                     | empty
        """
        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(SEMI)
                
        return declarations
            
    def variable_declaration(self):
        """
        variable_declaration : variable (COMMA ID)* COLON type_spec
        """
        variable_nodes = [self.variable()]
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            variable_nodes.append(self.variable())
        
        self.eat(COLON)
        
        type_node = self.type_spec()
        var_declarations = [VarDecl(var_node,type_node) for var_node in variable_nodes]
        return var_declarations
    
    def type_spec(self):
        """
        type_spec : INTEGER
                  | REAL
        """
        token = self.current_token
        self.eat(token.type)
        node = Type(token)
        return node
    
    def compound_statement(self):
        """
        compound_statement: BEGIN statement_list END
        """
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)
        
        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root
    
    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """
        node = self.statement()
        
        results = [node]
        
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())
            
        return results

    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left,token,right)
        return node

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        return NoOp()
    
    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node
    
    def term(self):
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV ) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, INTEGER_DIV,FLOAT_DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == INTEGER_DIV:
                self.eat(INTEGER_DIV)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    
    def factor(self):
        """
        factor : PLUS factor
               | MINUS factor
               | INTEGER_CONST
               | REAL_CONST
               | LPAREAN expr RPAREAN
               | variable
        """
        token:Token = self.current_token
        if token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == PLUS:
            self.eat(PLUS)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == ID:
            node = self.variable()
            return node
        else:
            self.error()

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()
        return node

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        # type(node).__name__ = BinOp / Num
        method_name = 'visit_' + type(node).__name__
        #print(method_name)
        
        # equal to use : self.visit_BinOp(node) / self.visit_Num(node)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    
    
    def __init__(self, parser:Parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}
        

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_Num(self, node):
        return node.value
    
    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self,node:Compound):
        for child in node.children:
            self.visit(child)
    
    def visit_NoOp(self,node:NoOp):
        pass

    def visit_Assign(self,node:Assign):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] =  self.visit(node.right)

    def visit_Var(self,node:Var):
        var_name = node.value
        value = self.GLOBAL_SCOPE.get(var_name)
        if value is None:
            raise NameError(repr(var_name))
        else:
            return value
    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        # Do nothing
        pass

    def visit_Type(self, node):
        # Do nothing
        pass

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ''
        return self.visit(tree)
        
def main(text):
    
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    for k, v in sorted(interpreter.GLOBAL_SCOPE.items()):
        print('{} = {}'.format(k, v))


if __name__ == "__main__":
    import sys
    file_name = sys.argv[1]
    with open(file_name,'r') as f:
        text = f.read()
    # print(text)
    main(text)
    