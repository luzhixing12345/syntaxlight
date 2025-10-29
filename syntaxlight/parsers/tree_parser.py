from .parser import Parser
from ..lexers import TokenType, Token

from enum import Enum

class TreeCSS(Enum):
    DIR = "Dir"
    FILE = "File"
    
class FileCSS(Enum):
    PIC = "Pic" #b4009e
    TAR = "Tar" #e74856
    SH = "Sh"   #16c60c
    LINK = "Link" #61d6d6
    
def add_file_css(token: Token):
    if not token.type == TokenType.ID:
        return
    value_lower = token.value.lower()
    if value_lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg")):
        token.add_css(FileCSS.PIC)
    elif value_lower.endswith((".tar", ".gz", ".zip", ".rar", ".7z", ".bz2", ".xz", ".deb")):
        token.add_css(FileCSS.TAR)
    elif value_lower.endswith((".sh", ".bash", ".zsh", ".iso")):
        token.add_css(FileCSS.SH)

class TreeParser(Parser):
    def __init__(self, lexer, skip_invis_chars=False, skip_space=False):
        super().__init__(lexer, skip_invis_chars, skip_space)

    def parse(self):
        '''
        tree has two display formats, e.g.:
        .
        ├── qemu.txt
        ├── qemu_config.ini
        └── scripts
            ├── badget.py
            └── switch_kernel.sh
            
        .
        |-- LICENSE
        |-- Makefile
        |-- README.md
        |-- chapter2
        |   |-- 01-module
        |   |   |-- Makefile
        |   |   |-- func.c
        |   |   |-- func.h
        |   |   `-- hellox.c
        '''
        depth = 0
        depth_chars = ["\xa0", "─", "├", "└", "│", " ", "|", '-', '`']
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.LF:
                depth = 0
                self.eat()
                continue
            if self.current_token.value in depth_chars:
                depth += 1
            
            if self.current_token.type == TokenType.ID:
                self.current_token.depth = int(depth / 4)

            self.eat()

        dir_chars = ["├", "└", "|"]
        for i, token in enumerate(self.token_list):
            if token.type == TokenType.ID:
                depth = token.depth
                pos = i + 1 + depth * 4 + 1
                if pos < len(self.token_list) and self.token_list[pos].value in dir_chars:
                    token.add_css(TreeCSS.DIR)
                else:
                    token.add_css(TreeCSS.FILE)
                    add_file_css(token)
                    if i + 2 < len(self.token_list):
                        next_token = self.token_list[i + 2]
                        if next_token.type == TokenType.POINT:
                            token.add_css(FileCSS.LINK)