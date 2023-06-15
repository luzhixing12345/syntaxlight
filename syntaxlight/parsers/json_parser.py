
from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from ..ast import AST, NodeVisitor

from typing import List

class Object(AST):

    def __init__(self, members) -> None:
        super().__init__()
        self.members: List[Pair] = members
        self.graph_node_info = f'member = {len(self.members)}'

    def visit(self, node_visitor: NodeVisitor = None):
        
        for member in self.members:
            node_visitor.link(self, member)
            member.visit(node_visitor)

    def format(self, depth: int = 0, **kwargs):
        # array 里套 object 的格式化需要特殊处理一下
        if kwargs.get('object', None) == True:
            depth += 1
        result = '{'
        if len(self.members) == 0:
            result += ' }'
        else:
            result += '\n'
            result +=  self.indent * (depth+1) + f'{self.members[0].format(depth)}'
            for i in range(1, len(self.members)):
                member = self.members[i]
                result += f',\n{self.indent * (depth+1)}{member.format(depth)}'    
            result += '\n' + self.indent * depth + '}'
        return result


class Array(AST):

    def __init__(self, elements) -> None:
        super().__init__()
        self.elements:List[AST] = elements
        self.graph_node_info = f'element = {len(self.elements)}'

    def visit(self, node_visitor: NodeVisitor = None):
        
        for element in self.elements:
            node_visitor.link(self, element)
            element.visit(node_visitor)

    def format(self, depth: int = 0, **kwargs):
        # array 里套 object 的格式化需要特殊处理一下
        result = '['
        if len(self.elements) == 0:
            result += ' ]'
        else:
            result += '\n'
            result +=  self.indent * (depth+1) + f'{self.elements[0].format(depth, object=self._object_in_array(self.elements[0]))}'
            for i in range(1, len(self.elements)):
                element = self.elements[i]
                result += f',\n{self.indent * (depth+1)}{element.format(depth, object = self._object_in_array(element))}'    
            result += '\n' + self.indent * depth + ']'
        return result

    def _object_in_array(self, element:AST):

        return element.class_name == 'Object'


class Pair(AST):

    def __init__(self, key:str, value) -> None:
        super().__init__()
        self.key:str = key
        self.value:AST = value
        self.graph_node_info = f'{self.key}:{self.value.class_name}'

    def visit(self, node_visitor: NodeVisitor = None):
        
        node_visitor.link(self, self.value)
        self.value.visit(node_visitor)
        
    def format(self, depth: int = 0, **kwargs):
        return f'{self.key}: {self.value.format(depth+1)}'


class Keyword(AST):

    def __init__(self, name) -> None:
        super().__init__()
        self.name:str = name
        self.graph_node_info = self.name

    def visit(self, node_visitor: NodeVisitor = None):
        return super().visit(node_visitor)
        
    def format(self, depth: int = 0, **kwargs):
        return self.name

class String(AST):

    def __init__(self, string) -> None:
        super().__init__()
        self.string = string
        self.graph_node_info = self.string

    def visit(self, node_visitor: NodeVisitor = None):
        return super().visit(node_visitor)
    
    def format(self, depth: int = 0, **kwargs):
        return self.string

class Number(AST):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.graph_node_info = self.value

    def visit(self, node_visitor: NodeVisitor = None):
        return super().visit(node_visitor)
        
    def format(self, depth: int = 0, **kwargs):
        return self.value

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
        self.node = self.json()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )
        return self.node

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
        
        self.eat(TokenType.LCURLY_BRACE, Object)
        members = []
        if self.current_token.type == TokenType.STRING:
            members = self.members()
        self.eat(TokenType.RCURLY_BRACE, Object)
        
        return Object(members)

    def array(self):
        '''
        <Array> ::= '[' ']'
                  | '[' <Elements> ']'
        '''
        elements = []

        self.eat(TokenType.LSQUAR_PAREN, Array)
        if self.current_token.type in self.value_first_set:
            elements = self.elements()
        self.eat(TokenType.RSQUAR_PAREN, Array)
        return Array(elements)


    def members(self) -> List[Pair]:
        '''
        <Members> ::= <Pair>
                    | <Pair> ',' <Members>
        '''
        pairs = [self.pair()]
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA, Object)
            pairs.extend(self.members())

        return pairs

    def pair(self):
        '''
        <Pair> ::= String ':' <Value>
        '''
        key = self.current_token.value
        self.eat(TokenType.STRING, Pair)
        self.eat(TokenType.COLON, Pair)
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
            self.eat(TokenType.COMMA, Array)
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
