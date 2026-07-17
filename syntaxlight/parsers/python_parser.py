import ast
import re

from .parser import Parser
from ..asts.python_ast import ClassDef, Decorator, FunctionDef, ImportStmt, Python, TypeAlias
from ..gdt import CSS, GlobalDescriptorTable
from ..lexers import PythonLexer, PythonTokenSet, PythonTokenType, Token, TokenType

GDT = GlobalDescriptorTable()


class PythonParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.python_first_set = PythonTokenSet()

    def parse(self):
        """
        file: [statements] ENDMARKER
        statements: statement+
        """
        GDT.reset()
        self.root = Python()
        statements = []
        while self.current_token.type != TokenType.EOF:
            token_id = self.current_token._id
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
            if self.current_token.type != TokenType.EOF and self.current_token._id == token_id:
                self.eat()
        self.root.update(statements=statements)
        GDT.reset()
        return self.root

    def statement(self):
        """
        statement: compound_stmt | simple_stmts

        The highlighter parses declaration-shaped statements structurally and
        consumes expression-shaped statements token by token. This keeps
        incomplete editor snippets renderable while following Python's BNF
        boundaries for definitions, imports, decorators and annotations.
        """
        if self.current_token.type == TokenType.AT_SIGN and self._is_line_start():
            return self.decorator()
        if self.current_token.type == PythonTokenType.ASYNC:
            if self.peek_next_token().type == PythonTokenType.DEF:
                return self.function_def()
        if self.current_token.type == PythonTokenType.DEF:
            return self.function_def()
        if self.current_token.type == PythonTokenType.CLASS:
            return self.class_def()
        if self.current_token.type == PythonTokenType.FROM and self._line_has_token(PythonTokenType.IMPORT):
            return self.import_from()
        if self.current_token.type == PythonTokenType.IMPORT:
            return self.import_name()
        if (
            self.current_token.type == TokenType.ID
            and self.current_token.value == PythonTokenType.SOFT_TYPE.value
            and self._is_line_start()
            and self.peek_next_token().type == TokenType.ID
            and self._line_has_token(TokenType.ASSIGN)
        ):
            return self.type_alias()
        if self.current_token.type == TokenType.ID and self._is_line_start():
            if (
                self.current_token.value == PythonTokenType.SOFT_MATCH.value
                and self._line_has_token(TokenType.COLON)
                and not self._line_has_token(TokenType.ASSIGN)
            ):
                self.current_token.type = PythonTokenType.SOFT_MATCH
            elif (
                self.current_token.value == PythonTokenType.SOFT_CASE.value
                and self._line_has_token(TokenType.COLON)
            ):
                self.current_token.type = PythonTokenType.SOFT_CASE
        if self._is_fstring(self.current_token):
            self.fstring()
            return None
        if self.current_token.type == TokenType.COLON and self._is_variable_annotation():
            self._highlight_annotation(CSS.CLASS_INSTANTIATION)
            return None

        self._highlight_current_token()
        self.eat()
        return None

    def fstring(self):
        """
        fstring:
            FSTRING_START fstring_middle* FSTRING_END
        fstring_replacement_field:
            '{' (yield_expr | star_expressions) '='?
            [fstring_conversion] [fstring_full_format_spec] '}'
        """
        value = self.current_token.value
        match = re.match(r"(?i)^([rubf]*)(\"\"\"|'''|\"|')", value)
        if match is None:
            self._highlight_current_token()
            self.eat()
            return

        quote = match.group(2)
        opening = match.group(0)
        body_start = len(opening)
        body_end = len(value) - len(quote)
        self._register_fstring_piece(opening, TokenType.STR, 0)

        text_start = body_start
        index = body_start
        while index < body_end:
            char = value[index]
            if char == "{" and index + 1 < body_end and value[index + 1] == "{":
                index += 2
                continue
            if char == "}" and index + 1 < body_end and value[index + 1] == "}":
                index += 2
                continue
            if char != "{":
                index += 1
                continue

            field_end = self._find_fstring_field_end(value, index + 1, body_end)
            if field_end is None:
                break
            if text_start < index:
                self._register_fstring_piece(
                    value[text_start:index],
                    TokenType.STR,
                    text_start,
                )
            self._register_fstring_piece("{", TokenType.LCURLY_BRACE, index)

            field = value[index + 1 : field_end]
            expression, suffix = self._split_fstring_field(field)
            expression_offset = index + 1
            self._register_fstring_expression(expression, expression_offset)
            if suffix:
                self._register_fstring_piece(
                    suffix,
                    TokenType.STR,
                    expression_offset + len(expression),
                )
            self._register_fstring_piece("}", TokenType.RCURLY_BRACE, field_end)
            index = field_end + 1
            text_start = index

        if text_start < body_end:
            self._register_fstring_piece(
                value[text_start:body_end],
                TokenType.STR,
                text_start,
            )
        self._register_fstring_piece(quote, TokenType.STR, body_end)
        self.manual_get_next_token()

    def parse_expression_fragment(self):
        while self.current_token.type != TokenType.EOF:
            if self._is_fstring(self.current_token):
                self.fstring()
            else:
                self._highlight_current_token()
                self.eat()
        return self.token_list

    def _register_fstring_expression(self, expression, offset):
        if not expression:
            return
        parser = PythonParser(PythonLexer(expression))
        tokens = parser.parse_expression_fragment()
        token_offset = offset
        for token in tokens:
            self._set_fstring_position(token, token_offset, len(token.value))
            self.manual_register_token(token)
            token_offset += len(token.value)

    def _register_fstring_piece(self, value, token_type, offset):
        if not value:
            return
        token = Token(token_type, value)
        token.add_css(CSS.FORMAT)
        self._set_fstring_position(token, offset, len(value))
        self.manual_register_token(token)

    def _set_fstring_position(self, token, offset, length):
        start_pos = self.lexer.pos - len(self.current_token.value)
        end_pos = start_pos + offset + max(length - 1, 0)
        source = self.lexer.text
        token.line = source.count("\n", 0, end_pos + 1) + 1
        previous_lf = source.rfind("\n", 0, end_pos + 1)
        token.column = end_pos + 1 if previous_lf == -1 else end_pos - previous_lf

    @staticmethod
    def _find_fstring_field_end(value, start, body_end):
        depth = 0
        quote = None
        index = start
        while index < body_end:
            if quote is not None:
                if value[index] == "\\":
                    index += 2
                    continue
                if value.startswith(quote, index):
                    index += len(quote)
                    quote = None
                    continue
                index += 1
                continue

            if value.startswith('"""', index) or value.startswith("'''", index):
                quote = value[index : index + 3]
                index += 3
                continue
            if value[index] in ('"', "'"):
                quote = value[index]
                index += 1
                continue
            if value[index] == "{":
                depth += 1
            elif value[index] == "}":
                if depth == 0:
                    return index
                depth -= 1
            index += 1
        return None

    @staticmethod
    def _split_fstring_field(field):
        depth = 0
        quote = None
        split_at = len(field)
        index = 0
        while index < len(field):
            if quote is not None:
                if field[index] == "\\":
                    index += 2
                    continue
                if field.startswith(quote, index):
                    index += len(quote)
                    quote = None
                    continue
                index += 1
                continue
            if field.startswith('"""', index) or field.startswith("'''", index):
                quote = field[index : index + 3]
                index += 3
                continue
            if field[index] in ('"', "'"):
                quote = field[index]
                index += 1
                continue
            if field[index] in "([{":
                depth += 1
            elif field[index] in ")]}":
                depth -= 1
            elif depth == 0 and field[index] in "!:":
                split_at = index
                break
            index += 1

        expression = field[:split_at]
        suffix = field[split_at:]
        stripped = expression.rstrip()
        if stripped.endswith("=") and not stripped.endswith(("==", "!=", "<=", ">=", ":=")):
            debug_end = len(stripped) - 1
            suffix = expression[debug_end:] + suffix
            expression = expression[:debug_end]
        return expression, suffix

    @staticmethod
    def _is_fstring(token):
        return (
            token.type == TokenType.STR
            and re.match(r"(?i)^[rub]*f[rub]*([\"'])", token.value) is not None
        )

    def decorator(self):
        """
        decorators: ('@' named_expression NEWLINE)+
        """
        node = Decorator()
        line = self.current_token.line
        self.eat(TokenType.AT_SIGN)
        while self.current_token.type != TokenType.EOF and self.current_token.line == line:
            if self.current_token.type == TokenType.ID:
                self._confirm_function(self.current_token)
                if node.name is None:
                    node.name = self.current_token
            else:
                self._highlight_current_token()
            self.eat()
        return node

    def class_def(self):
        """
        class_def_raw:
            'class' NAME [type_params] ['(' [arguments] ')'] ':' block
        """
        node = ClassDef()
        self.eat(PythonTokenType.CLASS)
        if self.current_token.type != TokenType.ID:
            return node

        node.name = self.current_token
        self._add_css(self.current_token, CSS.CLASS_NAME)
        GDT.register_id(self.current_token.value, CSS.CLASS_NAME)
        self.eat(TokenType.ID)

        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.type_params = self._consume_type_params()
        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            depth = 1
            while self.current_token.type != TokenType.EOF and depth > 0:
                if self.current_token.type == TokenType.LPAREN:
                    depth += 1
                elif self.current_token.type == TokenType.RPAREN:
                    depth -= 1
                    if depth == 0:
                        self.eat(TokenType.RPAREN)
                        break
                elif self.current_token.type == TokenType.ID:
                    self._confirm_class(self.current_token)
                    node.bases.append(self.current_token)
                self._highlight_current_token()
                self.eat()
        return node

    def function_def(self):
        """
        function_def_raw:
            ['async'] 'def' NAME [type_params] '(' [params] ')'
            ['->' expression] ':' block
        """
        node = FunctionDef()
        if self.current_token.type == PythonTokenType.ASYNC:
            node.async_kw = self.current_token
            self.eat(PythonTokenType.ASYNC)
        if self.current_token.type != PythonTokenType.DEF:
            return node
        self.eat(PythonTokenType.DEF)
        if self.current_token.type != TokenType.ID:
            return node

        node.name = self.current_token
        self._add_css(self.current_token, CSS.FUNCTION_NAME)
        GDT.register_id(self.current_token.value, CSS.FUNCTION_NAME)
        self.eat(TokenType.ID)

        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.type_params = self._consume_type_params()
        if self.current_token.type == TokenType.LPAREN:
            node.params = self._consume_parameters()
        if self.current_token.type == TokenType.POINT:
            self.eat(TokenType.POINT)
            node.return_annotation = self._consume_annotation(
                CSS.FUNCTION_RETURN_TYPE,
                {TokenType.COLON},
            )
        return node

    def import_name(self):
        """
        import_name: 'import' dotted_as_names
        dotted_as_name: dotted_name ['as' NAME]
        """
        node = ImportStmt()
        line = self.current_token.line
        self.eat(PythonTokenType.IMPORT)
        alias_expected = False
        while self.current_token.type != TokenType.EOF and self.current_token.line == line:
            if self.current_token.type == PythonTokenType.AS:
                alias_expected = True
            elif self.current_token.type == TokenType.ID:
                self._add_css(self.current_token, CSS.IMPORT_LIBNAME)
                if alias_expected:
                    node.aliases.append(self.current_token)
                    alias_expected = False
                else:
                    node.names.append(self.current_token)
                GDT.register_id(self.current_token.value, CSS.IMPORT_LIBNAME)
            self.eat()
        return node

    def import_from(self):
        """
        import_from:
            'from' ('.' | '...')* dotted_name 'import' import_from_targets
        """
        node = ImportStmt()
        self.eat(PythonTokenType.FROM)
        module_parts = []
        while self.current_token.type not in (PythonTokenType.IMPORT, TokenType.EOF):
            if self.current_token.type == TokenType.ID:
                self._add_css(self.current_token, CSS.IMPORT_LIBNAME)
                module_parts.append(self.current_token.value)
            self.eat()
        node.from_module = ".".join(module_parts)
        if self.current_token.type == PythonTokenType.IMPORT:
            self.eat(PythonTokenType.IMPORT)

        depth = 0
        alias_expected = False
        imported_css = None
        start_line = self.current_token.line
        while self.current_token.type != TokenType.EOF:
            if depth == 0 and self.current_token.line != start_line:
                break
            if self.current_token.type in (
                TokenType.LPAREN,
                TokenType.LSQUAR_PAREN,
                TokenType.LCURLY_BRACE,
            ):
                depth += 1
            elif self.current_token.type in (
                TokenType.RPAREN,
                TokenType.RSQUAR_PAREN,
                TokenType.RCURLY_BRACE,
            ):
                depth -= 1
            elif self.current_token.type == PythonTokenType.AS:
                alias_expected = True
            elif self.current_token.type == TokenType.ID:
                if alias_expected:
                    css = imported_css or self._infer_imported_name(self.current_token.value)
                    node.aliases.append(self.current_token)
                    alias_expected = False
                else:
                    css = self._infer_imported_name(self.current_token.value)
                    imported_css = css
                    node.names.append(self.current_token)
                self._replace_semantic_css(self.current_token, css)
                GDT.register_id(self.current_token.value, css)
            self.eat()
        return node

    def type_alias(self):
        """
        type_alias: 'type' NAME [type_params] '=' expression
        """
        node = TypeAlias()
        self.current_token.type = PythonTokenType.SOFT_TYPE
        self.eat(PythonTokenType.SOFT_TYPE)
        if self.current_token.type != TokenType.ID:
            return node
        node.name = self.current_token
        self._add_css(self.current_token, CSS.TYPEDEF)
        GDT.register_id(self.current_token.value, CSS.TYPEDEF)
        self.eat(TokenType.ID)
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.type_params = self._consume_type_params()
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
        return node

    def _consume_type_params(self):
        params = []
        self.eat(TokenType.LSQUAR_PAREN)
        depth = 1
        while self.current_token.type != TokenType.EOF and depth > 0:
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                depth += 1
            elif self.current_token.type == TokenType.RSQUAR_PAREN:
                depth -= 1
                if depth == 0:
                    self.eat(TokenType.RSQUAR_PAREN)
                    break
            elif self.current_token.type == TokenType.ID:
                self._add_css(self.current_token, CSS.FUNCTION_ARG_TYPE)
                params.append(self.current_token)
            self.eat()
        return params

    def _consume_parameters(self):
        params = []
        self.eat(TokenType.LPAREN)
        stack = [TokenType.RPAREN]
        state = "parameter"
        while self.current_token.type != TokenType.EOF and stack:
            token_type = self.current_token.type
            if token_type == stack[-1]:
                stack.pop()
                self.eat()
                continue
            closing = self._closing_token(token_type)
            if closing is not None:
                stack.append(closing)
                self._highlight_current_token()
                self.eat()
                continue

            at_parameter_level = len(stack) == 1
            if at_parameter_level and token_type == TokenType.COMMA:
                state = "parameter"
            elif at_parameter_level and token_type == TokenType.COLON:
                state = "annotation"
            elif at_parameter_level and token_type == TokenType.ASSIGN:
                state = "default"
            elif at_parameter_level and token_type == TokenType.ID and state == "parameter":
                self._add_css(self.current_token, CSS.FUNCTION_ARG_NAME)
                params.append(self.current_token)
                state = "after_parameter"
            elif state == "annotation":
                self._highlight_type_token(self.current_token, CSS.FUNCTION_ARG_TYPE)
            else:
                self._highlight_current_token()
            self.eat()
        return params

    def _consume_annotation(self, css, stop_types):
        tokens = []
        stack = []
        while self.current_token.type != TokenType.EOF:
            token_type = self.current_token.type
            if not stack and token_type in stop_types:
                break
            if stack and token_type == stack[-1]:
                stack.pop()
            else:
                closing = self._closing_token(token_type)
                if closing is not None:
                    stack.append(closing)
            self._highlight_type_token(self.current_token, css)
            tokens.append(self.current_token)
            self.eat()
        return tokens

    def _highlight_annotation(self, css):
        line = self.current_token.line
        self.eat(TokenType.COLON)
        stack = []
        stop_types = {TokenType.ASSIGN, TokenType.COMMA, TokenType.SEMI}
        while self.current_token.type != TokenType.EOF:
            token_type = self.current_token.type
            if not stack and (token_type in stop_types or self.current_token.line != line):
                break
            if stack and token_type == stack[-1]:
                stack.pop()
            else:
                closing = self._closing_token(token_type)
                if closing is not None:
                    stack.append(closing)
            self._highlight_type_token(self.current_token, css)
            self.eat()

    def _highlight_type_token(self, token, css):
        if token.type == TokenType.STR:
            forward_references = self._forward_reference_names(token.value)
            if forward_references:
                for name in forward_references:
                    GDT.register_id(name, CSS.CLASS_NAME)
                self._add_css(token, css)
        elif token.type == TokenType.ID or token.type in (
            PythonTokenType.BOOL,
            PythonTokenType.INT,
            PythonTokenType.STRR,
        ):
            if token.type == TokenType.ID:
                GDT.register_id(token.value, CSS.CLASS_NAME)
            self._add_css(token, css)

    def _highlight_current_token(self):
        if self.current_token.type == TokenType.ID:
            if self.peek_next_token().type == TokenType.LPAREN:
                descriptor = GDT[self.current_token.value]
                if descriptor in (CSS.CLASS_NAME, CSS.CLASS_INSTANTIATION):
                    self._replace_semantic_css(self.current_token, CSS.CLASS_INSTANTIATION)
                elif self._looks_like_class_name(self.current_token.value):
                    self._replace_semantic_css(self.current_token, CSS.CLASS_INSTANTIATION)
                    GDT.register_id(self.current_token.value, CSS.CLASS_NAME)
                else:
                    self._confirm_function(self.current_token)
            elif self.current_token.value in GDT:
                self._add_css(self.current_token, GDT[self.current_token.value])
            elif re.match(r"^[A-Z][A-Z0-9_]*$", self.current_token.value):
                self._add_css(self.current_token, CSS.ENUM_ID)
        elif (
            self.current_token.type == TokenType.STR
            and self.current_token.value[:1].lower() == "f"
        ):
            self._add_css(self.current_token, CSS.FORMAT)

    def _is_variable_annotation(self):
        previous = self._previous_significant_token()
        if previous is None or previous.type != TokenType.ID:
            return False
        if self._inside_delimiters() or self._line_contains_before(PythonTokenType.LAMBDA):
            return False
        next_token = self.peek_next_token()
        return next_token.type in (
            TokenType.ID,
            TokenType.LPAREN,
            TokenType.LSQUAR_PAREN,
            PythonTokenType.BOOL,
            PythonTokenType.INT,
            PythonTokenType.NONE,
            PythonTokenType.STRR,
        )

    def _line_has_token(self, token_type):
        line = self.current_token.line
        for offset in range(1, 256):
            token = self.peek_next_token(offset)
            if token.type == TokenType.EOF or token.line != line:
                return False
            if token.type == token_type:
                return True
        return False

    def _is_line_start(self):
        previous = self._previous_significant_token()
        return previous is None or previous.line < self.current_token.line

    def _previous_significant_token(self):
        ignored = {
            TokenType.BACKSPACE,
            TokenType.COMMENT,
            TokenType.CR,
            TokenType.FORM_FEED,
            TokenType.LF,
            TokenType.SPACE,
            TokenType.TAB,
            TokenType.VERTICAL_TAB,
        }
        for token in reversed(self.token_list):
            if token.type not in ignored:
                return token
        return None

    def _inside_delimiters(self):
        depths = {
            TokenType.LPAREN: 0,
            TokenType.LSQUAR_PAREN: 0,
            TokenType.LCURLY_BRACE: 0,
        }
        closing_to_opening = {
            TokenType.RPAREN: TokenType.LPAREN,
            TokenType.RSQUAR_PAREN: TokenType.LSQUAR_PAREN,
            TokenType.RCURLY_BRACE: TokenType.LCURLY_BRACE,
        }
        for token in self.token_list:
            if token.type in depths:
                depths[token.type] += 1
            elif token.type in closing_to_opening:
                opening = closing_to_opening[token.type]
                depths[opening] -= 1
        return any(depth > 0 for depth in depths.values())

    def _line_contains_before(self, token_type):
        line = self.current_token.line
        for token in reversed(self.token_list):
            if token.line != line:
                break
            if token.type == token_type:
                return True
        return False

    @staticmethod
    def _closing_token(token_type):
        return {
            TokenType.LPAREN: TokenType.RPAREN,
            TokenType.LSQUAR_PAREN: TokenType.RSQUAR_PAREN,
            TokenType.LCURLY_BRACE: TokenType.RCURLY_BRACE,
        }.get(token_type)

    @staticmethod
    def _add_css(token, css):
        if css.value not in token.class_list:
            token.add_css(css)

    @staticmethod
    def _looks_like_class_name(name):
        return bool(re.match(r"^[A-Z][A-Za-z0-9]*$", name))

    def _infer_imported_name(self, name):
        if self._looks_like_class_name(name):
            return CSS.CLASS_NAME
        return CSS.IMPORT_LIBFUNCTION

    def _forward_reference_names(self, value):
        try:
            annotation = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return []
        if not isinstance(annotation, str):
            return []
        return [
            name
            for name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", annotation)
            if self._looks_like_class_name(name)
        ]

    def _confirm_class(self, token):
        self._replace_semantic_css(token, CSS.CLASS_NAME)
        GDT.register_id(token.value, CSS.CLASS_NAME)

    def _confirm_function(self, token):
        self._replace_semantic_css(token, CSS.FUNCTION_CALL)
        GDT.register_id(token.value, CSS.FUNCTION_CALL)

    @staticmethod
    def _replace_semantic_css(token, css):
        semantic_classes = {
            CSS.CLASS_INSTANTIATION.value,
            CSS.CLASS_NAME.value,
            CSS.FUNCTION_CALL.value,
            CSS.FUNCTION_NAME.value,
            CSS.IMPORT_LIBFUNCTION.value,
            CSS.IMPORT_LIBNAME.value,
            CSS.TYPEDEF.value,
        }
        token.class_list = [
            class_name
            for class_name in token.class_list
            if class_name not in semantic_classes
        ]
        token.add_css(css)
