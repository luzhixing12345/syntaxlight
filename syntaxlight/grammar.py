
import os
import copy
import itertools

def print_set(name ,table):
    print(name)
    max_str_length = max(len(s) for s in table.keys()) + 1
    for key, value in table.items():
        print(f'   {key:<{max_str_length}}: {str(value)}')
    print()

class Core:

    def __init__(self, file_path) -> None:
        
        self.read_file(file_path)
        self.grammar = BNF()

    def read_file(self, file_path: str):

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read().split('\n')
        self.parse_grammar(file_content)

    def parse_grammar(self, file_content):
        
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


class Grammar:
    
    def __init__(self) -> None:
        self.begin_symbol = 'S'
        self.epsilon = 'ε'
        self.non_terminal_symbols = set()
        self.terminal_symbols = set()
        self.productions = {}
        
        self.first_set = None
        self.follow_set = None
        self.select_set = None        

class BNF(Grammar):

    def __init__(self) -> None:
        super().__init__()
        '''上下文无关文法 Context-Free Grammar(CFG)'''
        
    def parse(self):
        # 产生式左侧的是非终结符
        self.non_terminal_symbols = set(self.productions.keys())
        # 在右侧但不在左侧的符号是终结符
        for production_body in itertools.chain.from_iterable(self.productions.values()):
            for symbol in production_body:
                if symbol not in self.non_terminal_symbols:
                    self.terminal_symbols.add(symbol)
        self.terminal_symbols = set(self.terminal_symbols)
        
        self.eliminate_left_recursion()
        self.eliminate_left_public_factor()
        # 清空first集, 因为之前文法的预处理可能引入了新的非终结符
        self.first_set = None
        self.calculate_select_set()
        
    def eliminate_left_recursion(self):
        self.eliminate_indirect_left_recursion()
        self.eliminate_direct_left_recursion()        
        
    def eliminate_indirect_left_recursion(self):
        
        self.calculate_first_set()
        existed_symbols = set() # 左侧已出现的非终结符
        extend_symbols = {} # 需要被展开的左递归非终结符, key中的value需要被展开
        
        for production_head, production_bodys in self.productions.items():
            for production_body in production_bodys:
                for char in production_body:
                    if char in self.terminal_symbols:
                        # 终结符,退出
                        break
                    else:
                        # 如果当前非终结符已经出现在左侧了
                        # 则存在间接左递归
                        if char in existed_symbols:
                            if extend_symbols.get(production_head) is not None:
                                raise ValueError(f"{production_head} 出现了过多间接左递归依赖, 请重写文法")
                            if char in extend_symbols.keys():
                                raise ValueError(f'{char} 出现了多级间接左递归依赖, 过于复杂请重写文法')
                            if char == production_head:
                                # 交给直接左递归消除 去处理
                                break
                            print(f'[{char} {production_head} 存在间接左递归]: {production_head} -> {production_body}')
                            extend_symbols[production_head] = char
                            break
                        else:
                            existed_symbols.add(production_head)
                            if self.epsilon in self.first_set[char]:
                                # 当前非终结符的first集中含有 ε
                                # 继续判断下一个
                                pass
                            else:
                                break
        for symbol, sub_symbol in extend_symbols.items():
            productions = self.productions[symbol]
            new_productions = []
            sub_productions = self.productions[sub_symbol]
            for production in productions:
                if sub_symbol in production:
                    for sub_production in sub_productions:
                        if sub_production == self.epsilon:
                            sub_production = ''
                        new_productions.append(production.replace(sub_symbol,sub_production))
                else:
                    new_productions.append(production)
            self.productions[symbol] = new_productions
        
        if extend_symbols != {}:
            print('[修正后的产生式]:')
            self.show_productions()
        
    def eliminate_direct_left_recursion(self):
        
        flag = False
        extend_productions = {}
        
        for production_head, production_bodys in self.productions.items():
            for production_body in production_bodys:
                if production_body[0] == production_head:
                    flag = True
                    break
            if flag:
                # 存在直接左递归
                print(f"[{production_head} 存在直接左递归]: {production_head} -> {production_body}")
                new_symbol = self._register_new_symbol()
                # P -> Pα1 | Pα2 | Pαn | β1 | β2 | βm
                #
                # P -> β1P' | β2P' | βmP'     (1)
                # P'-> α1P' | α2P' | αnP' | ε (2)
                
                new_productions = [self.epsilon] # 新符号的产生式集合
                head_productions = [] # 存在左递归的head的新产生式集合
                for production_body in production_bodys:
                    if production_body[0] == production_head:
                        # 情况(2)
                        new_productions.append(production_body[1:] + new_symbol)
                    else:
                        # 情况(1)
                        if production_body == self.epsilon:
                            production_body = ''
                        head_productions.append(production_body + new_symbol)
                
                extend_productions[new_symbol] = new_productions
                self.productions[production_head] = head_productions
                flag = False
        # 遍历结束统一添加
        for new_symbol, new_productions in extend_productions.items():
            self.productions[new_symbol] = new_productions
    
    def eliminate_left_public_factor(self):
        
        extend_productions = {}
        
        for production_head, producton_bodys in self.productions.items():
            
            trie = Trie(producton_bodys) # 字典树
            common_nodes = trie.find_common_prefixes() # 找到公共前缀组
            if len(common_nodes) != 0:
                for node in common_nodes:
                    print(f"[{production_head} 存在左公因子]: {node.prefix}")
                extend_productions[production_head] = common_nodes
        
        for production_head, common_nodes in extend_productions.items():
            
            productions = self.productions[production_head]
            self.productions[production_head] = [] # 清空
            remove_productions = []
            for node in common_nodes:
                node: TrieNode
                prefix = node.prefix
                new_symbol = self._register_new_symbol()
                self.productions[production_head].append(prefix + new_symbol) # 替换左公因子
                self.productions[new_symbol] = node.children_str # 新非终结符的产生式
                remove_productions.extend([prefix + i for i in node.children_str])
                
            rest_productions = [i for i in productions if i not in remove_productions]
            self.productions[production_head].extend(rest_productions) # 保留剩下的没有影响的因子
        
        if extend_productions != {}:
            # 递归
            # 因为消除共同前缀之后还可能继续有共同前缀
            # S -> S + A | S - A | S + B
            self.eliminate_left_public_factor()
                
    
    def calculate_first_set(self):
        
        init_first_set = {}
        for non_terminal_symbol in self.non_terminal_symbols:
            # 使用set去重
            init_first_set[non_terminal_symbol] = set()
        
        self.first_set = self._calculate_first_set(init_first_set)
        
        
    def _calculate_first_set(self, first_set):
        
        current_frist_set = copy.deepcopy(first_set)
        
        for production_head, production_bodys in self.productions.items():
            for production_body in production_bodys:
                for i in range(len(production_body)):
                    char = production_body[i]
                    if char in self.terminal_symbols:
                        # 如果char字符是一个终结符
                        # 将char加入到production_statement的first集,结束
                        first_set[production_head].add(char)
                        break
                    else:
                        # char字符是非终结符
                        # 将char的first集(除去ε) 加入到production_statement的first集中
                        
                        exist_empty = False # char的first集中是否包含ε
                        for c in first_set[char]:
                            if c != self.epsilon:
                                first_set[production_head].add(c)
                            else:
                                exist_empty = True
                        
                        if not exist_empty:
                            # 如果char的first集中不包含'ε', 则结束
                            break
                        else:
                            # 如果包含了ε, 那么继续判断下一个字符
                            # 如果该字符已经是产生式的最后一个字符,则将ε加入到first集中
                            if i == len(production_body) - 1:
                                first_set[production_head].add(self.epsilon)
        
        if current_frist_set == first_set:
            # over
            return first_set
        else:
            # print_set("当前first set",first_set)
            return self._calculate_first_set(first_set)

    def calculate_follow_set(self):
        
        if self.first_set is None:
            self.calculate_first_set()
            
        init_follow_set = {}
        for non_terminal_symbol in self.non_terminal_symbols:
            init_follow_set[non_terminal_symbol] = set()
        # 将 $ 加入到起始元素的follow集中
        init_follow_set[self.begin_symbol].add('$')
        
        self.follow_set = self._calculate_follow_set(init_follow_set)
        
    
    def _calculate_follow_set(self, follow_set):
        
        current_follow_set = copy.deepcopy(follow_set)
        
        for production_head, production_bodys in self.productions.items():
            for production_body in production_bodys:
                for i in range(len(production_body)):
                    char = production_body[i]
                    
                    # 如果是终结符则看下一个
                    # 如果是非终结符
                    if char in self.non_terminal_symbols:
                        for j in range(i+1, len(production_body)):
                            # 找到后面的符号
                            follow_char = production_body[j]
                            if follow_char in self.terminal_symbols:
                                # 如果是终结符, 则加入到char的follow集中,结束
                                follow_set[char].add(follow_char)
                                break
                            else:
                                # 如果是非终结符,则将follow_char的first集的元素加入到
                                # char的follow集中
                                for symbol in self.first_set[follow_char]:
                                    follow_set[char].add(symbol)
                                # 如果char的follow集中有 ε 则去掉 ε 继续
                                if self.epsilon in follow_set[char]:
                                    follow_set[char].remove(self.epsilon)
                                else:
                                    # 如果没有 ε 则结束
                                    break
                for i in range(len(production_body)-1,-1,-1):
                    char = production_body[i]
                    # 如果结尾是一个终结符,则结束
                    # 如果结尾元素是一个非终结符
                    # 那么将产生式头部的follow集加入到结尾元素的follow集中
                    if char in self.terminal_symbols:
                        break
                    else:
                        for symbol in follow_set[production_head]:
                            follow_set[char].add(symbol)
                        # 如果结尾元素的follow集中不含 ε 则结束
                        # 否则继续向前判断
                        if self.epsilon not in self.first_set[char]:
                            break
        if current_follow_set == follow_set:
            # over
            return follow_set
        else:
            # print_set("当前follow集", follow_set)
            return self._calculate_follow_set(follow_set)
        
    def calculate_select_set(self):
        
        if self.first_set is None:
            self.calculate_first_set()
        if self.follow_set is None:
            self.calculate_follow_set()
    
        self.select_set = {}
        
        for production_head, production_bodys in self.productions.items():
            for production_body in production_bodys:
                first_char = production_body[0]
                
                production = f'{production_head} -> {production_body}'
                if first_char == self.epsilon:
                    # 如果产生式的第一个字符为 ε
                    # 该产生式的select集是production_head的follow集
                    self.select_set[production] = self.follow_set[production_head]
                elif first_char in self.terminal_symbols:
                    # 如果第一个字符是终结符
                    # 该产生式的select集是这个字符
                    self.select_set[production] = set(first_char)
                else:
                    # 如果第一个字符是非终结符
                    # 该产生式的select集是第一个字符的first集
                    self.select_set[production] = self.first_set[first_char]
    

    def info(self):

        print(f'[起始符号]: {self.begin_symbol}')
        print(f'[非终结符]: {str(self.non_terminal_symbols)}')
        print(f'[终结符  ]: {str(self.terminal_symbols)}')
        
        print_set("[first set]:",self.first_set)
        print_set("[follow set]:", self.follow_set)
        print_set('[select set]:',self.select_set)
    
    def show_productions(self):
        print('[产生式]:')
        for production_head, production_bodys in self.productions.items():
            for production_body in production_bodys:
                print(f'  {production_head} -> {production_body}')
        
    def _register_new_symbol(self):
        '''选择一个新的非终结符修正原文法'''
        
        for i in range(ord('A'), ord('Z') + 1):
            new_symbol = chr(i)
            if new_symbol not in self.non_terminal_symbols and \
                new_symbol not in self.terminal_symbols:

                self.non_terminal_symbols.add(new_symbol)
                self.terminal_symbols.add(self.epsilon)
                return new_symbol
        
        for i in range(ord('a'), ord('z') + 1):
            new_symbol = chr(i) 
            if new_symbol not in self.non_terminal_symbols and \
                new_symbol not in self.terminal_symbols:

                self.non_terminal_symbols.add(new_symbol)
                self.terminal_symbols.add(self.epsilon)
                return new_symbol
        
        raise ValueError("没有可用字符")

class TrieNode:
    def __init__(self, char):
        self.char = char
        self.children = {}
        self.children_str = []
        self.prefix = ''
        self.counter = 1

class Trie:
    def __init__(self, words):
        self.root = TrieNode('')
        for word in words:
            self.insert(word)  
        
    def insert(self, word):
        node = self.root
        for i in range(len(word)):
            char = word[i]
            if char in node.children:
                node.children_str.append(word[i:])
                node = node.children[char]
                node.counter += 1
            else:
                new_node = TrieNode(char)
                node.children[char] = new_node
                node.children_str.append(word[i:])
                new_node.prefix = node.prefix + char
                node = new_node
        
    def find_common_prefixes(self):

        common_nodes = []
        
        for char in self.root.children:
            node:TrieNode = self.root.children[char]
            if node.counter > 1:
                while node.counter > 1 and len(node.children) == 1:
                    node = list(node.children.values())[0]
                common_nodes.append(node)
        
        return common_nodes
    