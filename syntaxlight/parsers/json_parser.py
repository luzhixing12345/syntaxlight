

from .parser import Parser
from ..lexers.json_lexer import *

class JsonParser(Parser):

    def __init__(self, lexer):
        super().__init__(lexer)

    def parse(self):
        node = self.json()
        if self.current_token.type != JsonTokenType.EOF:
            self.error(
                error_code=JsonErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )
        return node
    
    def json(self):
        '''
        <Json> ::= <Object>
                 | <Array>
        '''
        if self.current_token.type == JsonTokenType.LCURLY_BRACE:
            return self.object()
        elif self.current_token.type == JsonTokenType.LSQUAR_PAREN:
            return self.array()
        else:
            self.error(JsonErrorCode.UNEXPECTED_TOKEN, self.current_token)
    
    def object(self):
        '''
        <Object> ::= '{' '}'
                   | '{' <Members> '}'
        '''
        members = []
        self.eat(JsonTokenType.LCURLY_BRACE)
        if self.current_token.type == JsonTokenType.QUOTO_MARK:
            members = self.members()
        self.eat(JsonTokenType.RCURLY_BRACE)
        return members

    def array(self):
        '''
        <Array> ::= '[' ']'
                  | '[' <Elements> ']'
        '''
        elements = []
        self.eat(JsonTokenType.LSQUAR_PAREN)
        # if self.current_token.type == 
        self.eat(JsonTokenType.RSQUAR_PAREN)

    def members(self):
        '''
        <Members> ::= <Pair>
                    | <Pair> ',' <Members>
        '''
        ...

    def pair(self):
        '''
        <Pair> ::= String ':' <Value>
        '''

    def elements(self):
        '''
        <Elements> ::= <Value>
                     | <Value> ',' <Elements>
        '''


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