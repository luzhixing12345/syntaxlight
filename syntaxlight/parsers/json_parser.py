
from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from ..ast import Object, Array, Pair, String, Number, Keyword

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
        <Object> ::= '{' <Pair>? ( ',' <Pair> )* '}'
        '''

        node = Object()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))

        pairs = []
        if self.current_token.type == TokenType.STRING:
            pairs.append(self.pair())
            while self.current_token.type == TokenType.COMMA:
                comma = self.current_token
                node.register_token(self.eat(TokenType.COMMA))
                # "not": {
                #     "$ref": "#/definitions/Schema1",
                #                                    |
                # }                             trailing comma
                if self.current_token.type == TokenType.RCURLY_BRACE:
                    self.error(ErrorCode.TRAILING_COMMA, comma, TokenType.COMMA.value)
                pairs.append(self.pair())
            
            # { pair1   pair2}
            #         |
            #   miss ',' here
            if self.current_token.type != TokenType.RCURLY_BRACE:
                self.error(ErrorCode.MISS_EXPECTED_TOKEN, self.current_token, TokenType.COMMA.value)
            
        node.update(pairs=pairs)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def array(self):
        '''
        <Array> ::= '[' <Value>? ( ',' <Value> )* ']'
        '''
        node = Array()
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))

        elements = []
        if self.current_token.type in self.value_first_set:
            elements.append(self.value())
            while self.current_token.type == TokenType.COMMA:
                comma = self.current_token
                node.register_token(self.eat(TokenType.COMMA))
                if self.current_token.type == TokenType.RSQUAR_PAREN:
                    self.error(ErrorCode.TRAILING_COMMA, comma, TokenType.COMMA.value)
                elements.append(self.value())

            if self.current_token.type != TokenType.RSQUAR_PAREN:
                self.error(ErrorCode.MISS_EXPECTED_TOKEN, self.current_token, TokenType.COMMA.value)
    
        node.update(elements=elements)
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def pair(self):
        '''
        <Pair> ::= String ':' <Value>
        '''
        key = String(self.current_token.value)
        node = Pair(key, None)

        node.register_token(self.eat(TokenType.STRING))
        node.register_token(self.eat(TokenType.COLON))

        value = self.value()
        node.update(value=value)
        return node

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
