
from enum import Enum
from .lexer import Lexer, TokenType, Token

class RustTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    ABSTRACT = 'abstract'
    ALIGNOF = 'alignof'
    AS = 'as'
    BECOME = 'become'
    BOX = 'box'
    BREAK = 'break'
    CONST = 'const'
    CONTINUE = 'continue'
    CRATE = 'crate'
    DO = 'do'
    ELSE = 'else'
    ENUM = 'enum'
    EXTERN = 'extern'
    FALSE = 'false'
    FINAL = 'final'
    FN = 'fn'
    FOR = 'for'
    IF = 'if'
    IMPL = 'impl'
    IN = 'in'
    LET = 'let'
    LOOP = 'loop'
    MACRO = 'macro'
    MATCH = 'match'
    MOD = 'mod'
    MOVE = 'move'
    MUT = 'mut'
    OFFSETOF = 'offsetof'
    OVERRIDE = 'override'
    PRIV = 'priv'
    PROC = 'proc'
    PUB = 'pub'
    PURE = 'pure'
    REF = 'ref'
    RETURN = 'return'
    SSELF = 'Self'
    SELF = 'self'
    SIZEOF = 'sizeof'
    STATIC = 'static'
    STRUCT = 'struct'
    SUPER = 'super'
    TRAIT = 'trait'
    TRUE = 'true'
    TYPE = 'type'
    TYPEOF = 'typeof'
    UNSAFE = 'unsafe'
    UNSIZED = 'unsized'
    USE = 'use'
    VIRTUAL = 'virtual'
    WHERE = 'where'
    WHILE = 'while'
    YIELD = 'yield'
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

class RustLexer(Lexer):
    
    def __init__(self, text: str, LanguageTokenType: Enum = RustTokenType):
        super().__init__(text, LanguageTokenType)
        
        
    def get_next_token(self):
        
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char == "/" and self.peek() == "/":
                return self.get_comment("//", "\n")
            if self.current_char == "/" and self.peek() == "*":
                return self.get_comment("/*", "*/")
            
            if self.current_char.isalnum() or self.current_char == '_':
                return self.get_id()

            try:
                token_type = TokenType(self.current_char)
            except ValueError:  # pragma: no cover
                token = Token(TokenType.TEXT, self.current_char, self.line, self.column)
                self.advance()
                return token
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # End of File
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)
    

class RustTokenSet:
    def __init__(self) -> None:
        pass