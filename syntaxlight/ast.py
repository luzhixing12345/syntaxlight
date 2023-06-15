
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

        self.class_name:str = self.__class__.__name__
        self._node_info:str = f'[{self.class_name}:{self.created_index}]'
        self.graph_node_info:str = None
        
        self.indent = ' ' * 4
        self._tokens:List[Token] = []

        self.depth = 0
        

    def register_token(self, token: Token):
        token.ast_types.append(self.class_name)
        self._tokens.append(token)
        token.ast = self

    def update(self, **kwargs):
        raise NotImplementedError

    def visit(self, node_visitor: 'NodeVisitor' = None, brace = False):
        '''由 node visitor 访问时递归调用'''
        node_visitor.depth -= 1 # 到达叶节点, 退出到上一层
        # 括号的深度退出一层
        if brace:
            node_visitor.brace_depth -= 1
        # print(f'visit {self.class_name}, depth = {self.depth}')
    
    def format(self, depth:int = 0, **kwargs):
        '''恢复为文本'''
        raise NotImplementedError

    def __str__(self) -> str:
        return self.format()

    def __repr__(self) -> str:
        return self.__str__()

    def get_node_info(self):
        # f'depth={self.depth}\\n'
        node_content = self._node_info + '\\n' + f'depth={self.depth}\\n' + self.graph_node_info.replace('"','\\"').replace("'","\\'")
        return f'node{self.created_index} [label="{node_content}"]'

class NodeVisitor:
    '''
    遍历 AST 节点构建 graphviz 图结构
    '''
    def __init__(self, image_name ='ast.dot') -> None:
        self.image_name = image_name
        self.depth = 0 # 当前的访问深度
        self.brace_depth = 0 # ([{<>}]) 的深度
        self.count = 0
        self.dot_header = textwrap.dedent("""\
            digraph astgraph {
                node [shape=circle, fontsize=50, fontname="Consolas Bold", height=2.5, width=2.5, style="filled", fillcolor="#DCDCDC", penwidth=2];
                edge [arrowsize=2, penwidth=5];
                graph [ranksep=1, pad=1];
            """)
        self.dot_footer = '}'
        self.dot_body = []
        self.visit_node_list = []

    def register(self, node:AST, depth:int):
        if node in self.visit_node_list:
            print("visit the same node!!!")
            exit(1)
        else:
            # 更新 AST 节点的深度
            node.depth = depth
            self.visit_node_list.append(node)
        
        self.dot_body.append(node.get_node_info())

    def link(self, root:AST, node:AST):
        
        if root not in self.visit_node_list:
            self.register(root, self.depth)

        if node not in self.visit_node_list:
            self.register(node, self.depth+1)

        self.dot_body.append(f'node{root.created_index} -> node{node.created_index}')
        self.depth += 1

    def save(self):
        '''
        save in graphviz pic
        '''

        graphviz_content = self.dot_header
        for dot in self.dot_body:
            graphviz_content += f'    {dot}\n'
        graphviz_content += self.dot_footer
        with open(self.image_name, 'w', encoding='utf-8') as f:
            f.write(graphviz_content)
        print(f'ast tree saved in [{self.image_name}], view by grpahviz')


def display_ast(root:AST, image_name = 'ast.dot'):

    node_visitor = NodeVisitor(image_name)
    root.visit(node_visitor)
    node_visitor.save()
    # print(root)