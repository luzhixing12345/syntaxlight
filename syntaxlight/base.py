
import os
import re
from .grammar import CFG

class Core:

    def __init__(self, file_path) -> None:
        
        self.read_file(file_path)

    def read_file(self, file_path: str):

        exam_path = re.findall(re.compile(r'e:(\d+):(\d+)'),file_path)
        
        if len(exam_path) == 1 and len(exam_path[0]) == 2:
            file_path = os.path.join(os.path.dirname(__file__),'exam',exam_path[0][0],exam_path[0][1] + '.txt')

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read().split('\n')
        self.parse_grammar(file_content)

    def parse_grammar(self, file_content):
        '''解析产生式'''
        raise NotImplementedError
        

class CFGCore(Core):
    
    def __init__(self, file_path) -> None:
        super().__init__(file_path)
        
    def parse_grammar(self, file_content):
        
        self.grammar = CFG()

        if len(file_content) == 0:
            raise ValueError('文件内容为空')
        # 文法展开
        for i in range(len(file_content)):
            line:str = file_content[i]
            production = line.split('->')
            if len(production) != 2:
                raise ValueError(f"产生式不符合规范: {production}")
            production_head = production[0].strip()
            if len(production_head) != 1:
                raise ValueError(f"产生式规则的左侧应为单个终结符: {production_head}")

            if i == 0:
                self.grammar.begin_symbol = production_head  # 起始符号

            if self.grammar.productions.get(production_head) is None:
                self.grammar.productions[production_head] = []
            # 展开所有产生式
            production_bodys = production[1].split('|')
            for production_body in production_bodys:
                production_body = production_body.strip()
                if self.grammar.epsilon in production_body and len(production_body) != 1:
                    raise ValueError(f"产生式 {production_body} 中不应出现 {self.grammar.epsilon}")
                if production_body in self.grammar.productions[production_head]:
                    raise ValueError(f"产生式 {production_body} 重复出现")
                self.grammar.productions[production_head].append(production_body)

        self.grammar.parse()
        self.grammar.info()
        self.grammar.show_productions()
