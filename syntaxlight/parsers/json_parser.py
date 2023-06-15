
from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from .ast import AST, NodeVisitor

from typing import List


class Object(AST):

    def __init__(self, members=None) -> None:
        super().__init__()
        self.members: List[Pair] = members

    def update(self, **kwargs):
        self.members = kwargs['members']
        self.graph_node_info = f'member = {len(self.members)}'

    def visit(self, node_visitor: NodeVisitor = None):

        for token in self._tokens:
            token.brace_depth = node_visitor.brace_depth
        node_visitor.brace_depth += 1

        for member in self.members:
            node_visitor.link(self, member)
            member.visit(node_visitor)
        return super().visit(node_visitor, brace=True)

    def format(self, depth: int = 0, **kwargs):
        if kwargs.get('object', None) is True:
            depth += 1
        result = '{'
        if len(self.members) == 0:
            result += ' }'
        else:
            result += '\n'
            result += self.indent * (depth+1) + \
                f'{self.members[0].format(depth)}'
            for i in range(1, len(self.members)):
                member = self.members[i]
                result += f',\n{self.indent * (depth+1)}{member.format(depth)}'
            result += '\n' + self.indent * depth + '}'
        return result


class Array(AST):

    def __init__(self, elements=None) -> None:
        super().__init__()
        self.elements: List[AST] = elements

    def update(self, **kwargs):
        elements = kwargs['elements']
        self.elements: List[AST] = elements
        self.graph_node_info = f'element = {len(self.elements)}'

    def visit(self, node_visitor: NodeVisitor = None):

        for token in self._tokens:
            token.brace_depth = node_visitor.brace_depth

        node_visitor.brace_depth += 1

        for element in self.elements:
            node_visitor.link(self, element)
            element.visit(node_visitor)

        return super().visit(node_visitor, brace=True)

    def format(self, depth: int = 0, **kwargs):

        result = '['
        if len(self.elements) == 0:
            result += ' ]'
        else:
            result += '\n'
            result += self.indent * \
                (depth+1) + \
                f'{self.elements[0].format(depth, object=self._object_in_array(self.elements[0]))}'
            for i in range(1, len(self.elements)):
                element = self.elements[i]
                is_object = self._object_in_array(element)
                result += f',\n{self.indent * (depth+1)}{element.format(depth, object = is_object)}'
            result += '\n' + self.indent * depth + ']'
        return result

    def _object_in_array(self, element: AST):

        return element.class_name == 'Object'


class Pair(AST):

    def __init__(self, key: str, value: AST = None) -> None:
        super().__init__()
        self.key: str = key
        self.value: AST = value

    def update(self, **kwargs):

        value = kwargs['value']
        self.value: AST = value
        self.graph_node_info = f'{self.key}:{self.value.class_name}'

    def visit(self, node_visitor: NodeVisitor = None):

        node_visitor.link(self, self.value)
        self.value.visit(node_visitor)
        return super().visit(node_visitor)

    def format(self, depth: int = 0, **kwargs):
        return f'{self.key}: {self.value.format(depth+1)}'


class Keyword(AST):

    def __init__(self, name) -> None:
        super().__init__()
        self.name: str = name
        self.graph_node_info = self.name

    def format(self, depth: int = 0, **kwargs):
        return self.name


class String(AST):

    def __init__(self, string) -> None:
        super().__init__()
        self.string = string
        self.graph_node_info = self.string

    def format(self, depth: int = 0, **kwargs):
        return self.string


class Number(AST):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.graph_node_info = self.value

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
        # print(self.node)
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

        node = Object()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        if self.current_token.type == TokenType.STRING:
            members = self.members(node)
            node.update(members=members)

        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def array(self):
        '''
        <Array> ::= '[' ']'
                  | '[' <Elements> ']'
        '''
        node = Array()
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        if self.current_token.type in self.value_first_set:
            elements = self.elements(node)
            node.update(elements=elements)

        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def members(self, object: Object) -> List[Pair]:
        '''
        <Members> ::= <Pair>
                    | <Pair> ',' <Members>
        '''
        pairs = [self.pair()]
        if self.current_token.type == TokenType.COMMA:
            object.register_token(self.eat(TokenType.COMMA))
            pairs.extend(self.members(object))

        return pairs

    def pair(self):
        '''
        <Pair> ::= String ':' <Value>
        '''
        key = self.current_token.value
        node = Pair(key, None)

        node.register_token(self.current_token)
        self.eat(TokenType.STRING)

        node.register_token(self.current_token)
        self.eat(TokenType.COLON)

        value = self.value()
        node.update(value=value)
        return node

    def elements(self, array: Array):
        '''
        <Elements> ::= <Value>
                     | <Value> ',' <Elements>
        '''
        if self.current_token.type not in self.value_first_set:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)

        values = [self.value()]

        if self.current_token.type == TokenType.COMMA:
            array.register_token(self.eat(TokenType.COMMA))
            values.extend(self.elements(array))
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
            message = f'"{self.current_token.value}" does not support for json value'
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token, message)

        if self.current_token.type in JsonTokenType:
            node = Keyword(self.current_token.value)
            node.register_token(self.eat(self.current_token.type))
            return node

        if self.current_token.type == TokenType.STRING:
            node = String(self.current_token.value)
            node.register_token(self.eat(TokenType.STRING))
            return node

        if self.current_token.type == TokenType.NUMBER:
            node = Number(self.current_token.value)
            node.register_token(self.eat(TokenType.NUMBER))
            return node

        if self.current_token.type == TokenType.LCURLY_BRACE:
            return self.object()

        if self.current_token.type in self.value_first_set:
            return self.array()

        # should never arrive here
