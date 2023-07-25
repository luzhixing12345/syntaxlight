import textwrap
from enum import Enum
from .lexers import Token
from typing import List, Union, Dict, Tuple
from .gdt import Enum

AST_CREATED_INDEX = 0


class AST(object):
    def __init__(self) -> None:
        # 节点被创建的顺序
        global AST_CREATED_INDEX
        self._created_index = AST_CREATED_INDEX
        AST_CREATED_INDEX = AST_CREATED_INDEX + 1

        self.class_name: str = self.__class__.__name__
        self.node_info: str = f"[{self.class_name}:{self._created_index}]"

        self._indent = " " * 4
        # AST 树包含的 Token
        self._tokens: List[Token] = []
        self._depth = 0  # 节点深度
        self.is_leaf_ast = False  # 底层 AST, 叶节点

        # 默认 update 的时候只会为一级 AST 添加当前类名, 启用此选项后会递归地将类名传递给其下的每一个叶节点
        # 默认不开启以减少对子类的影响
        self.update_subnode = False  

    def register_token(self, tokens: List[Token], extra_class_name: str = None):
        """
        将 token 注册到 AST 树中以更新 token 的属性
        """
        for token in tokens:
            token.class_list.add(self.class_name)
            if extra_class_name:
                token.class_list.add(extra_class_name)
            self._tokens.append(token)
            token.ast = self

    def update(self, **kwargs):
        """
        对于一些后续才可以获取的属性, 或者子 AST 节点的注册, 调用此方法更新子 AST 对象内部的元素
        """
        for key, node in kwargs.items():
            setattr(self, key, node)
            # update 的时候将子元素的 token 也添加当前 AST 的 class
            if isinstance(node, AST):
                for token in node._tokens:
                    token.class_list.add(self.class_name)
            if self.update_subnode:
                self._update_sub_ast(node, self.class_name)

    def _update_sub_ast(self, node: "AST", class_name: str):
        """
        为叶节点补充添加类名信息, 但 token 会有很复杂的 class name, 不宜采用
        """
        if node is None:
            return
        if type(node) == list:
            for nod in node:
                self._update_sub_ast(nod, class_name)
            return
        if node.is_leaf_ast:
            node.class_name = class_name
            for token in node._tokens:
                token.class_list.add(class_name)
            return
        else:
            for _, attribute_value in vars(node).items():
                if isinstance(attribute_value, AST):
                    self._update_sub_ast(attribute_value, class_name)
                elif type(attribute_value) == list:
                    if len(attribute_value) > 0 and isinstance(attribute_value[0], AST):
                        for a_v in attribute_value:
                            self._update_sub_ast(a_v, class_name)

    def visit(self, node_visitor: "NodeVisitor" = None):
        """
        由 node visitor 访问时递归调用
        """
        node_visitor.depth -= 1  # 到达叶节点, 退出到上一层
        # print(f'visit {self.class_name}, depth = {self.depth}')

    def formatter(self, depth: int = 0):
        raise NotImplementedError(self.class_name + " should override format function to display")

    def __str__(self) -> str:
        return self.formatter()

    def __repr__(self) -> str:
        return self.__str__()

    def get_node_info(self):
        # f'depth={self.depth}\\n'
        node_content = self.node_info + "\\n" + f"depth={self._depth}"
        return f'node{self._created_index} [label="{node_content}"]'


class Object(AST):
    """
    { pair1, pair2, ...}
    """

    def __init__(self, members=None) -> None:
        super().__init__()
        self.pairs: List[Pair] = members
        self._inside_array = False  # only use in format

    def update(self, **kwargs):
        return super().update(**kwargs)

    def visit(self, node_visitor: "NodeVisitor" = None):
        for pair in self.pairs:
            node_visitor.link(self, pair)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        if self._inside_array:
            depth += 1
        result = "{"
        if len(self.pairs) == 0:
            result += " }"
        else:
            result += "\n"
            result += self._indent * (depth + 1) + f"{self.pairs[0].formatter(depth)}"
            for i in range(1, len(self.pairs)):
                member = self.pairs[i]
                result += f",\n{self._indent * (depth+1)}{member.formatter(depth)}"
            result += "\n" + self._indent * depth + "}"
        return result


class Array(AST):
    """
    [ element1, elements2, ...]
    """

    def __init__(self, elements=None) -> None:
        super().__init__()
        self.elements: List[AST] = elements

    def update(self, **kwargs):
        return super().update(**kwargs)

    def visit(self, node_visitor: "NodeVisitor" = None):
        for element in self.elements:
            node_visitor.link(self, element)

        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        result = "["
        for e in self.elements:
            if e.class_name == "Object":
                e._inside_array = True
        if len(self.elements) == 0:
            result += " ]"
        else:
            result += "\n"
            result += self._indent * (depth + 1) + f"{self.elements[0].formatter(depth)}"
            for i in range(1, len(self.elements)):
                element = self.elements[i]
                result += f",\n{self._indent * (depth+1)}{element.formatter(depth)}"
            result += "\n" + self._indent * depth + "]"
        return result


class Pair(AST):
    def __init__(self, key: AST = None, value: AST = None) -> None:
        super().__init__()
        self.key: AST = key
        self.value: AST = value

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.key)
        node_visitor.link(self, self.value)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        return f"{self.key.formatter(depth+1)}: {self.value.formatter(depth+1)}"


class Keyword(AST):
    def __init__(self, name) -> None:
        super().__init__()
        self.name: str = name
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.name}"

    def formatter(self, depth: int = 0):
        return self.name


class Identifier(AST):
    def __init__(self, id) -> None:
        super().__init__()
        self.id: str = id
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.id}"

    def formatter(self, depth: int = 0):
        return self.id

class Punctuator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.op = self.op
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.op}"


class Constant(AST):
    def __init__(self, constant) -> None:
        super().__init__()
        self.constant = constant
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.constant}"


class String(AST):
    def __init__(self, string) -> None:
        super().__init__()
        self.string: str = string
        self.is_leaf_ast = True

        string_info = self.string.replace("\\", "\\\\").replace('"', '\\"')
        self.node_info += f"\\n{string_info}"

    def __str__(self) -> str:
        return self.string

    def formatter(self, depth: int = 0):
        return self.string


class Char(AST):
    def __init__(self, string) -> None:
        super().__init__()
        self.string = string
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.string}"

    def formatter(self, depth: int = 0):
        return self.string


class Number(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.value}"

    def formatter(self, depth: int = 0):
        return self.value


class Punctuator(AST):
    def __init__(self, op) -> None:
        super().__init__()
        self.op = op
        self.is_leaf_ast = True

    def formatter(self, depth: int = 0):
        return self.op


class UnaryOp(AST):
    def __init__(self, expr: AST = None, op: str = None) -> None:
        super().__init__()
        self.expr = expr
        self.op = op

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.expr)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        return self.op + self.expr.formatter(depth + 1)


class BinaryOp(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr_left = None
        self.expr_rights: List[AST] = None
        self.op = None

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.expr_left)
        node_visitor.link(self, self.expr_rights)
        return super().visit(node_visitor)


class AssignOp(AST):
    def __init__(self, op: str = None) -> None:
        super().__init__()
        self.op = op
        self.is_leaf_ast = True
        self.node_info += f"\\n{self.op}"

    def visit(self, node_visitor: "NodeVisitor" = None):
        return super().visit(node_visitor)


class ConditionalExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.condition_expr = None
        self.value_true = None
        self.value_false = None

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.condition_expr)
        if self.value_true:
            node_visitor.link(self, self.value_true)
        if self.value_false:
            node_visitor.link(self, self.value_false)
        return super().visit(node_visitor)


class Expression(AST):
    def __init__(self, exprs: List[AST] = None) -> None:
        super().__init__()
        self.exprs = exprs

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.exprs)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        result = ""
        if self.exprs:
            for expr in self.exprs:
                result += expr.formatter(depth + 1)

        return result + "\n"


class NodeVisitor:
    """
    遍历 AST 节点构建 graphviz 图结构
    """

    def __init__(self) -> None:
        self.image_name = "ast.dot"
        self.depth = 0  # 当前的访问深度
        self.count = 0
        self.dot_header = textwrap.dedent(
            """\
            digraph astgraph {
                node [shape=circle, fontsize=50, fontname="Consolas Bold", height=2.5, width=2.5, style="filled", fillcolor="#DCDCDC", penwidth=2];
                edge [arrowsize=2, penwidth=5];
                graph [ranksep=1, pad=1];
            """
        )
        self.dot_footer = "}"
        self.dot_body = []
        self.visit_node_list = []

    def register(self, node: AST, depth: int):
        if node in self.visit_node_list:
            print("visit the same node!!!")
            exit(1)
        else:
            # 更新 AST 节点的深度
            node._depth = depth
            self.visit_node_list.append(node)

        self.dot_body.append(node.get_node_info())

    def link(self, root: AST, node: AST):
        """
        usage inside AST : node_visitor.link(self, self.xxx)

        内部做了各种判断, 只需考虑访问顺序
        """
        if root not in self.visit_node_list:
            self.register(root, self.depth)

        # 判空
        if node is None:
            return
        # 列表
        if type(node) == list:
            for n in node:
                self.link(root, n)
            return
        if node not in self.visit_node_list:
            self.register(node, self.depth + 1)

        self.dot_body.append(f"node{root._created_index} -> node{node._created_index}")
        self.depth += 1
        node.visit(self)

    def save(self):
        """
        save in graphviz pic
        """

        graphviz_content = self.dot_header
        for dot in self.dot_body:
            graphviz_content += f"    {dot}\n"
        graphviz_content += self.dot_footer
        with open(self.image_name, "w", encoding="utf-8") as f:
            f.write(graphviz_content)
        print(f"ast tree saved in [{self.image_name}], view by grpahviz")


def display_ast(node: AST, sub_roots: List[AST], save_ast_tree=False):
    node_visitor = NodeVisitor()
    node.visit(node_visitor)
    for sub_root in sub_roots:
        node_visitor.depth += 1
        sub_root.visit(node_visitor)

    if save_ast_tree:
        node_visitor.save()
    # node.formatter()
    assert node_visitor.depth == -1


def add_ast_type(node: AST, css_type: Enum):
    """
    为叶节点补充添加类名信息
    """
    if node is None:
        return
    if type(node) == list:
        for nod in node:
            add_ast_type(nod, css_type)
        return

    if node.is_leaf_ast:
        node.class_name = css_type.value
        for token in node._tokens:
            token.class_list.add(css_type.value)
            # print(token, f"[{class_name}]")
        return
    else:
        # 遍历对象的所有属性
        for _, attribute_value in vars(node).items():
            if isinstance(attribute_value, AST):
                add_ast_type(attribute_value, css_type)
            elif type(attribute_value) == list:
                if len(attribute_value) > 0 and isinstance(attribute_value[0], AST):
                    for a_v in attribute_value:
                        add_ast_type(a_v, css_type)


def delete_ast_type(node: AST, css_type: Enum):
    """
    为叶节点补充去除类名信息
    """
    if node is None:
        return
    if type(node) == list:
        for nod in node:
            delete_ast_type(nod, css_type)
        return

    if node.is_leaf_ast:
        for token in node._tokens:
            if css_type.value in token.class_list:
                token.class_list.remove(css_type.value)
            # print(token, f"[{class_name}]")
        return
    else:
        # 遍历对象的所有属性
        for _, attribute_value in vars(node).items():
            if isinstance(attribute_value, AST):
                delete_ast_type(attribute_value, css_type)
            elif type(attribute_value) == list:
                if len(attribute_value) > 0 and isinstance(attribute_value[0], AST):
                    for a_v in attribute_value:
                        delete_ast_type(a_v, css_type)
