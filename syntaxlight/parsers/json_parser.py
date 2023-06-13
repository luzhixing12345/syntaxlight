
from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from ..ast import AST

class Object(AST):

    def __init__(self, members) -> None:
        super().__init__()
        self.members = members

class Array(AST):

    def __init__(self, elements) -> None:
        super().__init__()
        self.elements = elements


class Pair(AST):

    def __init__(self, key, value) -> None:
        super().__init__()
        self.key = key
        self.value = value

class Members(AST):

    def __init__(self, pairs) -> None:
        super().__init__()
        self.pairs = pairs

class Elements(AST):

    def __init__(self, values) -> None:
        super().__init__()
        self.values = values


class Keyword(AST):

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

class String(AST):

    def __init__(self, string) -> None:
        super().__init__()
        self.string = string


class Number(AST):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class JsonParser(Parser):

    def __init__(self, lexer):
        super().__init__(lexer)

        self.value_first_set = [
            TokenType.STRING,
            TokenType.NUMBER,
            TokenType.LSQUAR_PAREN,
            TokenType.LCURLY_BRACE,
            JsonTokenType.TRUE,
            JsonTokenType.FALSE,
            JsonTokenType.NULL
        ]

    def parse(self):
        node = self.json()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )
        return node

    def json(self):
        '''
        <Json> ::= <Object>
                 | <Array>
        '''
        if self.current_token.type == TokenType.LCURLY_BRACE:
            return self.object()
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            return self.array()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)

    def object(self):
        '''
        <Object> ::= '{' '}'
                   | '{' <Members> '}'
        '''
        
        if self.current_token.type == TokenType.LCURLY_BRACE:
            self.eat(TokenType.LCURLY_BRACE)
            members = self.members()
        else:
            self.eat(TokenType.LCURLY_BRACE)
            members = None

        self.eat(TokenType.RCURLY_BRACE)
        
        return Object(members)

    def array(self):
        '''
        <Array> ::= '[' ']'
                  | '[' <Elements> ']'
        '''
        elements = []

        self.eat(TokenType.LSQUAR_PAREN)
        if self.current_token.type in self.value_first_set:
            elements = self.elements()
        self.eat(TokenType.RSQUAR_PAREN)
        return Array(elements)


    def members(self):
        '''
        <Members> ::= <Pair>
                    | <Pair> ',' <Members>
        '''
        pairs = [self.pair()]
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            pairs.extend(self.members())

        return pairs

    def pair(self):
        '''
        <Pair> ::= String ':' <Value>
        '''
        key = self.current_token.value
        self.eat(TokenType.STRING)
        self.eat(TokenType.COLON)
        value = self.value()
        return Pair(key, value)


    def elements(self):
        '''
        <Elements> ::= <Value>
                     | <Value> ',' <Elements>
        '''
        if self.current_token.type not in self.value_first_set:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        
        values = [self.value()]
        
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            values.extend(self.elements())
        return values

    def value(self):
        '''
        <Value> ::= String
                  | Number
                  | <Object>
                  | <Array>
                  | true
                  | false
                  | null
        '''
        # print(self.current_token.type)
        if self.current_token.type not in self.value_first_set:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)

        if self.current_token.type in JsonTokenType:
            node = Keyword(self.current_token.value)
            self.eat(self.current_token.type)
            return node
        
        if self.current_token.type == TokenType.STRING:
            node = String(self.current_token.value)
            self.eat(TokenType.STRING)
            return node
        
        if self.current_token.type == TokenType.NUMBER:
            node = Number(self.current_token.value)
            self.eat(TokenType.NUMBER)
            return node
        
        if self.current_token.type == TokenType.LCURLY_BRACE:
            return self.object()
        
        if self.current_token.type in self.value_first_set:
            return self.array()
        
        self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
