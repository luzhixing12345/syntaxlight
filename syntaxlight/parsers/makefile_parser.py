from .parser import Parser
from . import ShellCSS
from ..lexers import TokenType, MakefileTokenType, MakefileTokenSet, ShellTokenType
from ..error import ErrorCode
from ..ast import AST, add_ast_type

class Makefile(AST):
    def __init__(self) -> None:
        super().__init__()

class Target(AST):
    def __init__(self) -> None:
        super().__init__()
        self.variables = None

class Variable(AST):
    def __init__(self) -> None:
        super().__init__()
        self.target:Target = None
        self.sub_nodes = None

class Declaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.target: Target = None

class Mission(AST):
    def __init__(self) -> None:
        super().__init__()

class Include(AST):
    def __init__(self) -> None:
        super().__init__()
        self.target = None

class ConditionStatement(AST):
    def __init__(self) -> None:
        super().__init__()

class Export(AST):
    def __init__(self) -> None:
        super().__init__()

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
        self.skip_crlf()
        while self.current_token.type in self.first_set.statement:
            stmt.append(self.statement())
            self.skip_crlf()
        node.update(stmt = stmt)
        return node

    def statement(self):
        '''
        <statement> ::= <declaration>
                      | <mission>
                      | <include_makefile>
                      | <condition_stmt>
                      | export <target>+
                      | unexport <target>+
                      | <command>
        '''
        if self.current_token.type == MakefileTokenType.INCLUDE:
            self.include_makefile()
        elif self.current_token.type in self.first_set.condition_stmt:
            self.condition_stmt()
        elif self.current_token.type in self.first_set.export:
            node = Export()
            node.update(keyword = self.get_keyword())
            targets = []
            while self.current_token.type in self.first_set.target:
                targets.append(self.target())
            node.update(targets = targets)
            self.eat_lf()
            return node
        # elif self.current_token.type == TokenType.DOLLAR:
        #     self.command()
        else:
            target = self.target()
            self.skip_tab()
            if self.current_token.type in self.first_set.assign_op:
                return self.declaration(target)
            elif self.current_token.type == TokenType.COLON:
                return self.mission(target)
            # else:
            #     self.error(ErrorCode.UNEXPECTED_TOKEN, "unknown ...")

    def declaration(self, target):
        '''
        <declaration> ::= <target> <assign_op> <value>* ( "\\" <value>* )* <CRLF>
        '''
        node = Declaration()
        node.update(target = target)
        node.update(assign_op = self.assign_op())
        self.skip_black_slash()
        
        while self.current_token.type != TokenType.LF:
            self.value()
            self.skip_black_slash()

        self.eat_lf()
        self.skip_crlf()
        return node


    def mission(self, target):
        '''
        <mission> ::= <target>+ ":" <TAB>* <prerequisites>? ( <CRLF> "\t" <command>)* <CRLF>
        '''
        node = Mission()
        node.update_subnode = True
        targets = [target]
        while self.current_token.type in self.first_set.target:
            targets.append(self.target())
        node.update(targets = targets)
        node.register_token(self.eat(token_type=TokenType.COLON))
        self.skip_tab()
        if self.current_token.type in self.first_set.target:
            node.update(prereq = self.prerequisites())
            
        self.skip_tab()
        
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
                      | "+="
        '''
        return self.punctuator()
    
    def include_makefile(self):
        '''
        <include_makefile> ::= include <target> <CRLF>
        '''
        node = Include()
        node.update(keyword = self.get_keyword(MakefileTokenType.INCLUDE))
        node.update(target = self.target())
        add_ast_type(node.target, ShellCSS.URL)
        self.eat_lf()
        return node
    
    def condition_stmt(self):
        '''
        <condition_stmt> ::= (ifeq | ifneq) "(" <target> "," <target>? ")" <CRLF> <command> endif
                           | (ifdef | ifndef ) <target> <CRLF>
        '''
        node = ConditionStatement()
        assert self.current_token.type in self.first_set.condition_stmt
        if self.current_token.type in (MakefileTokenType.IFEQ, MakefileTokenType.IFNEQ):
            node.update(keyword = self.get_keyword())
            node.register_token(self.eat(token_type=TokenType.LPAREN))
            node.update(target_1 = self.target())
            node.register_token(self.eat(TokenType.COMMA))
            if self.current_token.type in self.first_set.target:
                node.update(target_2 = self.target())
            node.register_token(self.eat(token_type=TokenType.RPAREN))
        else:
            node.update(keyword = self.get_keyword())
            node.update(target_1 = self.target())
        self.eat_lf()
        while self.current_token.type not in (TokenType.EOF , MakefileTokenType.ENDIF):
            self.command()
            self.eat_lf()
        node.update(end = self.get_keyword(MakefileTokenType.ENDIF))
        return node

    
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
        self.skip_tab()
        while self.current_token.type in self.first_set.target:
            result.append(self.target())
            self.skip_black_slash()
        
        return result

    def command(self):
        '''
        
        '''
        self.skip_tab()
        while self.current_token.type not in (TokenType.LF, TokenType.EOF):
            self.value()
            self.skip_tab()
            self.skip_black_slash()
            

    def variable(self):
        '''
        <variable> ::= "$" "{" <target> (","? <target>?)* "}"
                     | "$" "(" <target> (","? <target>?)* ")"
                     | <ID>
                     | <NUMBER>
                     | <STR>
        '''
        if self.current_token.value in self.lexer.reserved_keywords:
            self.current_token.type = TokenType.ID
        if self.current_token.type == TokenType.ID:
            return self.identifier()
        elif self.current_token.type == TokenType.NUMBER:
            return self.number()
        elif self.current_token.type == TokenType.STR:
            return self.string()
        elif self.current_token.type == TokenType.COLON:
            return self.punctuator()
        elif self.current_token.type == TokenType.DOLLAR:
            node = Variable()
            node.register_token(self.eat(TokenType.DOLLAR))
            if self.current_token.type == TokenType.LCURLY_BRACE:
                node.register_token(self.eat())
                node.update(target = self.target())
                self.skip_black_slash()
                sub_nodes = []
                while self.current_token.type == TokenType.COMMA or self.current_token.type in self.first_set.target:
                    if self.current_token.type == TokenType.COMMA:
                        node.register_token(self.eat(token_type=TokenType.COMMA))
                    else:
                        sub_nodes.append(self.target())
                    self.skip_black_slash()
                node.update(sub_nodes = sub_nodes)
                node.register_token(self.eat(TokenType.RPAREN))
            elif self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat())
                node.update(target = self.target())
                self.skip_black_slash()
                sub_nodes = []
                while self.current_token.type == TokenType.COMMA or self.current_token.type in self.first_set.target:
                    if self.current_token.type == TokenType.COMMA:
                        node.register_token(self.eat(token_type=TokenType.COMMA))
                    else:
                        sub_nodes.append(self.target())
                    self.skip_black_slash()
                node.update(sub_nodes = sub_nodes)
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
        if self.current_token.type == TokenType.LANGLE_BRACE:
            self.current_token.type = MakefileTokenType.REDIRECT_TO
        if self.current_token.type == TokenType.RANGLE_BRACE:
            self.current_token.type = MakefileTokenType.REDIRECT_FROM            

        self.eat()

    def skip_tab(self):
        while self.current_token.type == TokenType.TAB:
            self.eat()

    def skip_black_slash(self):
        if self.current_token.type == TokenType.BACK_SLASH:
            self.eat()
            self.eat_lf()
            self.skip_tab()