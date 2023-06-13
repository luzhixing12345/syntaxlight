

AST_CREATED_INDEX = 0

class AST(object):
    
    def __init__(self) -> None:
        # show_info = True
        show_info = False

        if show_info:
            print(f'[{self.__class__.__name__} created]')

        global AST_CREATED_INDEX
        self.created_index = AST_CREATED_INDEX
        AST_CREATED_INDEX = AST_CREATED_INDEX + 1

    def visit(self):
        '''
        重写此方法
        '''
        raise NotImplementedError

def display_ast(node, picture_name = 'ast.dot'):

    ...

    print(f'ast tree saved in [{picture_name}], view by grpahviz')