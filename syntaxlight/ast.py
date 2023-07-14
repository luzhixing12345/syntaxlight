import textwrap

from .lexers import Token
from typing import List

AST_CREATED_INDEX = 0


class AST(object):
    def __init__(self) -> None:
        # 节点被创建的顺序
        global AST_CREATED_INDEX
        self.created_index = AST_CREATED_INDEX
        AST_CREATED_INDEX = AST_CREATED_INDEX + 1

        self.class_name: str = self.__class__.__name__
        self._node_info: str = f"[{self.class_name}:{self.created_index}]"

        self.indent = " " * 4
        # AST 树包含的 Token
        self._tokens: List[Token] = []
        self.depth = 0  # 节点深度

    def register_token(self, tokens: List[Token], extra_class_name:str = None):
        """
        将 token 注册到 AST 树中以更新 token 的属性
        """
        for token in tokens:
            token.class_list.append(self.class_name)
            if extra_class_name:
                token.class_list.append(extra_class_name)
            self._tokens.append(token)
            token.ast = self

    def update(self, **kwargs):
        """
        对于一些后续才可以获取的属性, 或者子 AST 节点的注册, 调用此方法更新子 AST 对象内部的元素
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
            # update 的时候将子元素的 token 也添加当前 AST 的 class
            if isinstance(value, AST):
                for token in value._tokens:
                    token.class_list.append(self.class_name)

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
        node_content = self._node_info + "\\n" + f"depth={self.depth}"
        return f'node{self.created_index} [label="{node_content}"]'

    def add_ast_type(self, class_name: str):
        for token in self._tokens:
            token.class_list.append(class_name)


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
            result += self.indent * (depth + 1) + f"{self.pairs[0].formatter(depth)}"
            for i in range(1, len(self.pairs)):
                member = self.pairs[i]
                result += f",\n{self.indent * (depth+1)}{member.formatter(depth)}"
            result += "\n" + self.indent * depth + "}"
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
            result += self.indent * (depth + 1) + f"{self.elements[0].formatter(depth)}"
            for i in range(1, len(self.elements)):
                element = self.elements[i]
                result += f",\n{self.indent * (depth+1)}{element.formatter(depth)}"
            result += "\n" + self.indent * depth + "]"
        return result


class Pair(AST):
    def __init__(self, key: AST = None, value: AST = None) -> None:
        super().__init__()
        self.key: AST = key
        self.value: AST = value

    def update(self, **kwargs):
        return super().update(**kwargs)

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

    def formatter(self, depth: int = 0):
        return self.name


class Identifier(AST):
    def __init__(self, id) -> None:
        super().__init__()
        self.id = id


class Constant(AST):
    def __init__(self, constant) -> None:
        super().__init__()
        self.constant = constant

class String(AST):
    def __init__(self, string) -> None:
        super().__init__()
        self.string = string

    def formatter(self, depth: int = 0):
        return self.string


class Number(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def formatter(self, depth: int = 0):
        return self.value


class UnaryOp(AST):
    def __init__(self, expr: AST = None, op: str = None) -> None:
        super().__init__()
        self.expr = expr
        self.op = op
        self.keyword = None

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.expr)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        return self.op + self.expr.formatter(depth + 1)


class BinaryOp(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr_left = None
        self.expr_rights:List[AST] = None
        self.op = None

    def visit(self, node_visitor: "NodeVisitor" = None):
        node_visitor.link(self, self.expr_left)
        if self.expr_rights:
            for expr_right in self.expr_rights:
                node_visitor.link(self, expr_right)
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
        if self.exprs:
            for expr in self.exprs:
                node_visitor.link(self, expr)

        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        result = ""
        if self.exprs:
            for expr in self.exprs:
                result += expr.formatter(depth + 1)

        return result + "\n"


class AssignMent(AST):

    def __init__(self, op) -> None:
        super().__init__()
        self.op = op


class NodeVisitor:
    """
    遍历 AST 节点构建 graphviz 图结构
    """

    def __init__(self, image_name="ast.dot") -> None:
        self.image_name = image_name
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
            node.depth = depth
            self.visit_node_list.append(node)

        self.dot_body.append(node.get_node_info())

    def link(self, root: AST, node: AST):
        '''
        usage inside AST : node_visitor.link(self, self.xxx)

        内部做了各种判断, 只需考虑访问顺序
        '''
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

        self.dot_body.append(f"node{root.created_index} -> node{node.created_index}")
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
        # with open(self.image_name, "w", encoding="utf-8") as f:
        #     f.write(graphviz_content)
        # print(f"ast tree saved in [{self.image_name}], view by grpahviz")


def display_ast(node: AST, image_name="ast.dot"):
    node_visitor = NodeVisitor(image_name)
    node.visit(node_visitor)

    node_visitor.save()
    # node.formatter()

    assert node_visitor.depth == -1
