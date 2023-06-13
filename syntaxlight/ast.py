

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

    def _self_elements(self):
        self_elements_str = ""
        for attr, value in self.__dict__.items():
            self_elements_str += f'{attr} : {value}\n'
        return self_elements_str

def display_ast(node, picture_name = 'ast.dot'):

    ...

    print(f'ast tree saved in [{picture_name}], view by grpahviz')