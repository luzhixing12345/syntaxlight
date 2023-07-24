from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, XmlTokenType
from ..error import ErrorCode
from ..ast import AST, String, NodeVisitor


class XML(AST):
    def __init__(self) -> None:
        super().__init__()
        self.prolog = None
        self.element = None

    def visit(self, node_visitor: NodeVisitor = None):
        if self.prolog:
            node_visitor.link(self, self.prolog)

        node_visitor.link(self, self.element)
        return super().visit(node_visitor)


class Prolog(AST):
    def __init__(self) -> None:
        super().__init__()
        self.attributes = None

    def visit(self, node_visitor: NodeVisitor = None):
        for attribute in self.attributes:
            node_visitor.link(self, attribute)
        return super().visit(node_visitor)


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.value = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.name)
        node_visitor.link(self, self.value)
        return super().visit(node_visitor)


class Name(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class Tag(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.attributes = None
        self.elements = None
        self.end_name = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.name)
        for attribute in self.attributes:
            node_visitor.link(self, attribute)
        if self.elements:
            for element in self.elements:
                node_visitor.link(self, element)
        if self.end_name:
            node_visitor.link(self, self.end_name)
        return super().visit(node_visitor)


class Content(AST):
    def __init__(self, content) -> None:
        super().__init__()
        self.content = content


class XmlParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        self.root = self.XML()
        if self.current_token.type == XmlTokenType.CONTENT:
            eat_flag = True
            for char in self.current_token.value:
                if char not in self.lexer.invisible_characters or char != " ":
                    eat_flag = False
                    break
            if eat_flag:
                self.eat(self.current_token.type)
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.root

    def XML(self):
        """
        <XML> ::= (<prolog>)? (<element>)?
        """
        node = XML()
        if self.current_token.type == XmlTokenType.PROLOG_START:
            node.update(prolog=self.prolog())
        if self.current_token.type == XmlTokenType.TAG_START_BEGIN:
            node.update(element=self.element())
        return node

    def prolog(self):
        """
        <prolog> ::= "<?xml" (S <Attribute>)* S? "?>"
        """
        node = Prolog()
        node.register_token(self.eat(XmlTokenType.PROLOG_START))
        attributes = []
        while self.current_token.type == XmlTokenType.NAME:
            attributes.append(self.attribute())
        node.update(attributes=attributes)
        node.register_token(self.eat(XmlTokenType.PROLOG_END))
        return node

    def element(self):
        """
        <element> ::= <EmptyElemTag> | <STag> <content> <ETag>

        <EmptyElemTag> ::= "<" <Name> (S <Attribute>)* S? "/>"

        <STag>    ::= "<" <Name> (S <Attribute>)* S? ">"
        <content> ::= (.* <element> .*)*
        <ETag>    ::= "</" <Name> S? ">"
        """
        node = Tag()
        node.register_token(self.eat(XmlTokenType.TAG_START_BEGIN))

        name = Name(self.current_token.value)
        name.register_token(self.eat(self.current_token.type))
        node.update(name=name)

        attributes = []
        while self.current_token.type == XmlTokenType.NAME:
            attributes.append(self.attribute())
        node.update(attributes=attributes)

        if self.current_token.type == XmlTokenType.TAG_SELF_END:
            node.register_token(self.eat(XmlTokenType.TAG_SELF_END))
        elif self.current_token.type == XmlTokenType.TAG_END:
            node.register_token(self.eat(XmlTokenType.TAG_END))
            elements = []
            while self.current_token.type in (XmlTokenType.CONTENT, XmlTokenType.TAG_START_BEGIN):
                if self.current_token.type == XmlTokenType.CONTENT:
                    content = Content(self.current_token.value)
                    content.register_token(self.eat(XmlTokenType.CONTENT))
                    elements.append(content)
                elif self.current_token.type == XmlTokenType.TAG_START_BEGIN:
                    elements.append(self.element())
            node.update(elements=elements)

            node.register_token(self.eat(XmlTokenType.TAG_COMPLETE_BEGIN))
            end_name = Name(self.current_token.value)
            end_name.register_token(self.eat(XmlTokenType.NAME))
            node.update(end_name=end_name)
            node.register_token(self.eat(XmlTokenType.TAG_END))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "miss > or /> tag end")
        return node

    def attribute(self):
        """
        <Attribute> ::= <Name> "=" <String>

        <Name> ::= (Letter | '_' | ':') (<NameChar>)*
        <NameChar> ::= <Letter> | <Digit> | '.' | '-' | '_' | ':'
        """
        node = Attribute()
        name = Name(self.current_token.value)
        name.register_token(self.eat(self.current_token.type))
        node.update(name=name)

        node.register_token(self.eat(TokenType.ASSIGN))
        if self.current_token.type in (TokenType.STR, TokenType.STRING):
            value = String(self.current_token.value)
            value.register_token(self.eat(self.current_token.type))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "attribute value should be a string")
        node.update(value=value)
        return node
