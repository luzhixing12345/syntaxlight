import textwrap
from .lexers import Token, TokenType
from typing import List

AST_CREATED_INDEX = 0


class AST(object):
    def __init__(self) -> None:
        # print(f'[{self.class_name} created]')
        global AST_CREATED_INDEX
        self.created_index = AST_CREATED_INDEX
        AST_CREATED_INDEX = AST_CREATED_INDEX + 1

        self.class_name: str = self.__class__.__name__
        self._node_info: str = f"[{self.class_name}:{self.created_index}]"
        self.graph_node_info: str = None

        self.indent = " " * 4
        self._tokens: List[Token] = []

        self.depth = 0

    def register_token(self, tokens: List[Token]):

        for token in tokens:
            token.ast_types.append(self.class_name)
            self._tokens.append(token)
            token.ast = self

    def update(self, **kwargs):
        '''{need override}'''
        raise NotImplementedError

    def visit(self, node_visitor: "NodeVisitor" = None, brace=False):
        """由 node visitor 访问时递归调用"""
        node_visitor.depth -= 1  # 到达叶节点, 退出到上一层
        # 括号的深度退出一层
        if brace:
            node_visitor.brace_depth -= 1
        # print(f'visit {self.class_name}, depth = {self.depth}')

    def format(self, depth: int = 0, **kwargs):
        '''{need override}: recovery to text'''
        raise NotImplementedError(self.class_name + ' should override format function to display')

    def __str__(self) -> str:
        return self.format()

    def __repr__(self) -> str:
        return self.__str__()

    def get_node_info(self):
        # f'depth={self.depth}\\n'
        node_content = (
            self._node_info
            + "\\n"
            + f"depth={self.depth}\\n"
            + self.graph_node_info.replace('"', '\\"').replace("'", "\\'")
        )
        return f'node{self.created_index} [label="{node_content}"]'

    def add_ast_type(self, class_name: str):

        for token in self._tokens:
            token.ast_types.append(class_name)


class Object(AST):
    '''
    { pair1, pair2, ...}
    '''
    def __init__(self, members=None) -> None:
        super().__init__()
        self.pairs: List[Pair] = members

    def update(self, **kwargs):
        self.pairs = kwargs['pairs']
        self.graph_node_info = f'pairs = {len(self.pairs)}'

    def visit(self, node_visitor: 'NodeVisitor' = None):

        for token in self._tokens:
            token.brace_depth = node_visitor.brace_depth
        node_visitor.brace_depth += 1

        for pair in self.pairs:
            node_visitor.link(self, pair)
            pair.visit(node_visitor)
        return super().visit(node_visitor, brace=True)

    def format(self, depth: int = 0, **kwargs):
        if kwargs.get('object', None) is True:
            depth += 1
        result = '{'
        if len(self.pairs) == 0:
            result += ' }'
        else:
            result += '\n'
            result += self.indent * (depth+1) + \
                f'{self.pairs[0].format(depth)}'
            for i in range(1, len(self.pairs)):
                member = self.pairs[i]
                result += f',\n{self.indent * (depth+1)}{member.format(depth)}'
            result += '\n' + self.indent * depth + '}'
        return result


class Array(AST):
    '''
    [ element1, elements2, ...]
    '''
    def __init__(self, elements=None) -> None:
        super().__init__()
        self.elements: List[AST] = elements

    def update(self, **kwargs):
        elements = kwargs['elements']
        self.elements: List[AST] = elements
        self.graph_node_info = f'element = {len(self.elements)}'

    def visit(self, node_visitor: 'NodeVisitor' = None):
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

    def visit(self, node_visitor: 'NodeVisitor' = None):

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


class Comment(AST):

    def __init__(self, comment:str) -> None:
        super().__init__()
        self.comment = comment
        self.graph_node_info = self.comment

    def format(self, depth: int = 0, **kwargs):
        return self.comment

class NodeVisitor:
    """
    遍历 AST 节点构建 graphviz 图结构
    """

    def __init__(self, image_name="ast.dot") -> None:
        self.image_name = image_name
        self.depth = 0  # 当前的访问深度
        self.brace_depth = 0  # ([{<>}]) 的深度
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
        if root not in self.visit_node_list:
            self.register(root, self.depth)

        if node not in self.visit_node_list:
            self.register(node, self.depth + 1)

        self.dot_body.append(f"node{root.created_index} -> node{node.created_index}")
        self.depth += 1

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



def display_ast(root: AST, image_name="ast.dot"):
    node_visitor = NodeVisitor(image_name)
    root.visit(node_visitor)
    node_visitor.save()
    # print(root)
