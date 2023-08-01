from .parser import Parser
from . import ShellCSS
from ..lexers import TokenType, MakefileTokenType, MakefileTokenSet, ShellTokenType
from ..error import ErrorCode
from ..ast import AST
from ..gdt import GlobalDescriptorTable

class Makefile(AST):
    def __init__(self) -> None:
        super().__init__()

class Target(AST):
    def __init__(self) -> None:
        super().__init__()
        

class Variable(AST):
    def __init__(self) -> None:
        super().__init__()

class Declaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.target: Target = None

class Mission(AST):
    def __init__(self) -> None:
        super().__init__()

GDT = GlobalDescriptorTable()


class MakefileParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=False, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        self.first_set = MakefileTokenSet()

    def parse(self):
        self.root = self.makefile()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF: # pragma: no cover
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.root


    def makefile(self):
        '''
        <makefile> ::= <statement>*
        '''
        node = Makefile()
        stmt = []
        while self.current_token.type in self.first_set.statement:
            stmt.append(self.statement())
        node.update(stmt = stmt)
        return node

    def statement(self):
        '''
        <statement> ::= <declaration>
                      | <mission>
        '''
        target = self.target()
        if self.current_token.type in self.first_set.assign_op:
            return self.declaration(target)
        elif self.current_token.type == TokenType.COLON:
            return self.mission(target)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "?")

    def declaration(self, target):
        '''
        <declaration> ::= <target> <assign_op> <value>* ( "\\" <value>* )* <CRLF>
        '''
        node = Declaration()
        node.update(target = target)
        node.update(assign_op = self.assign_op())
        while self.current_token.type != TokenType.LF:
            self.value()
            if self.current_token.type == TokenType.BACK_SLASH:
                node.register_token(self.eat())
        GDT.register_id(node.target)
        self.eat_lf()
        self.skip_crlf()
        return node


    def mission(self, target):
        '''
        <mission> ::= <target>+ ":" <prerequisites>? ( <CRLF> "\t" <command>)* <CRLF>
        '''
        node = Mission()
        node.update_subnode = True
        targets = [target]
        while self.current_token.type in self.first_set.target:
            targets.append(self.target())
        node.update(targets = targets)
        node.register_token(self.eat(token_type=TokenType.COLON))
        if self.current_token.type in self.first_set.target:
            node.update(prereq = self.prerequisites())
        
        while self.current_token.type == TokenType.LF:
            self.eat_lf()
            self.skip_crlf()
            if self.current_token.type == TokenType.TAB:
                node.register_token(self.eat(TokenType.TAB))
                self.command()
            else:
                break
        return node


    def assign_op(self):
        '''
        <assign_op> ::= "="
                      | ":="
        '''
        return self.punctuator()
    
    def target(self):
        '''
        <target> ::= <variable> ("/" <variable>?)* 
        '''
        node = Target()
        node.update_subnode = True
        variables = [self.variable()]
        while self.current_token.type == TokenType.DIV:
            self.current_token.type = MakefileTokenType.PATH_SLASH
            node.register_token(self.eat())
            if self.current_token.type in self.first_set.variable:
                variables.append(self.variable())

        node.update(variables = variables)
        return node

    def prerequisites(self):
        '''
        <prerequisites> ::= <target>*
        '''
        result = []
        while self.current_token.type in self.first_set.target:
            result.append(self.target())
        return result

    def command(self):
        '''
        
        '''
        while self.current_token.type != TokenType.LF:
            self.value()

    def variable(self):
        '''
        <variable> ::= "$" "{" <target> "}"
                     | "$" "(" <target> ")"
                     | <ID>
        '''
        
        if self.current_token.type == TokenType.ID:
            return self.identifier()
        elif self.current_token.type == TokenType.DOLLAR:
            node = Variable()
            node.register_token(self.eat(TokenType.DOLLAR))
            if self.current_token.type == TokenType.LCURLY_BRACE:
                node.register_token(self.eat())
                node.update(target = self.target)
                node.register_token(self.eat(TokenType.RPAREN))
            elif self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat())
                node.update(target = self.target())
                node.register_token(self.eat(token_type=TokenType.RPAREN))
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "should be { or (")
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be $ or ID")

    def value(self):
        
        if self.current_token.type == TokenType.ID:
            if self.current_token.value.startswith('-'):
                self.current_token.type = ShellTokenType.OPTION
        if self.current_token.type == TokenType.DIV:
            self.current_token.type = MakefileTokenType.PATH_SLASH
        self.eat()

        