
import textwrap

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

    def visit(self, node_visitor: 'NodeVisitor' = None):
        return
    
    def format(self, depth:int = 0, **kwargs):
        '''恢复为文本'''
        raise NotImplementedError

    def __str__(self) -> str:
        return self._node_info + '\n' + self.format()

    def __repr__(self) -> str:
        return self.__str__()

class NodeVisitor:
    '''
    遍历 AST 节点构建 graphviz 图结构
    '''
    def __init__(self, image_name) -> None:
        self.image_name = image_name
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

    def _visit(self, node:AST):
        if node in self.visit_node_list:
            print("visit the same node!!!")
            exit(1)
        else:
            self.visit_node_list.append(node)
        
        node_content = node._node_info + '\\n' + node.graph_node_info.replace('"','\\"').replace("'","\\'")
        self.dot_body.append(f'node{node.created_index} [label="{node_content}"]')

    def link(self, root:AST, node:AST):
        
        if root not in self.visit_node_list:
            self._visit(root)

        if node not in self.visit_node_list:
            self._visit(node)

        self.dot_body.append(f'node{root.created_index} -> node{node.created_index}')

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