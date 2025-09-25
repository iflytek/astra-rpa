from typing import Optional, Union

from rpa_executor.error import *
from rpa_executor.flow.syntax.ast import (
    IF,
    Atomic,
    AtomicExist,
    AtomicFor,
    Block,
    Break,
    ChildProgram,
    Component,
    Continue,
    For,
    Node,
    Program,
    Try,
    While,
)
from rpa_executor.flow.syntax.lexer import Lexer
from rpa_executor.flow.syntax.token import (
    Token,
    TokenType,
    exist_atomic_dict,
    for_atomic_dict,
    special_token_type_end,
    token_type_key_dict,
)


class Parser:
    def __init__(
        self,
        lexer: Lexer,
        end_tag: str = "{}End",
    ):
        # 词法分析
        self.lexer: Lexer = lexer

        # block的结束符标签 eg:if ifEnd
        self.end_tag: str = end_tag

        # 内部变量
        self.errors: list = []
        self.cur_token: Union[Token, None] = None
        self.peek_token: Union[Token, None] = None
        self.prefix_parse_fns: dict = {}

        # 初始化
        self.next_token()
        self.next_token()

        # 注册解析器
        self.break_and_continue_in_loop = 0
        self.register_prefix(TokenType.Break, self.__parse_break__)
        self.register_prefix(TokenType.Continue, self.__parse_continue__)
        self.register_prefix(TokenType.While, self.__parse_while__)
        self.register_prefix(TokenType.If, self.__parse_if__)
        self.register_prefix(TokenType.ForStep, self.__parse_for__)
        self.register_prefix(TokenType.ForList, self.__parse_for__)
        self.register_prefix(TokenType.ForDict, self.__parse_for__)
        self.register_prefix(TokenType.Try, self.__parse_try__)
        self.register_prefix(TokenType.Process, self.__parse_child_process__)
        self.register_prefix(TokenType.Component, self.__parse_component__)

    def register_prefix(self, token_type: TokenType, fn):
        """注入token处理程序"""
        self.prefix_parse_fns[token_type.value] = fn

    def next_token(self):
        """语法分析next_token"""
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self) -> Optional[Node]:
        """语法分析 解析入口"""
        program = Program()
        program.token = self.cur_token
        program.statements = []
        while self.cur_token.type != TokenType.EOF.value:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()
        return program

    def parse_block(self) -> Optional[Node]:
        """语法分析 解析Block块"""
        block = Block()
        block.token = self.cur_token
        block.statements = []

        self.next_token()

        end_list = [self.end_tag.format(block.token.type)]
        if block.token.type in special_token_type_end:
            end_list = special_token_type_end[block.token.type]
        elif block.token.type in exist_atomic_dict:
            end_list = special_token_type_end[TokenType.If.value]
        elif block.token.type in for_atomic_dict:
            end_list = special_token_type_end[TokenType.ForStep.value]

        while self.cur_token.type not in end_list and self.cur_token.type != TokenType.EOF.value:
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()
        return block

    def parse_statement(self) -> Optional[Node]:
        """语法分析 解析"""
        if self.cur_token.type in self.prefix_parse_fns:
            prefix = self.prefix_parse_fns[self.cur_token.type]
            res = prefix()
        else:
            if self.cur_token.type in token_type_key_dict:
                self.errors.append(NO_ATOMIC_FORMAT.format(self.cur_token.type))
                return
            res = self.parse_atomic()
        return res

    def parse_atomic(self) -> Optional[Node]:
        if self.cur_token.type in exist_atomic_dict:
            stmt = AtomicExist()
            stmt.token = self.cur_token
            stmt.consequence = self.parse_block()
            if self.cur_token.type == TokenType.ElseIf.value:
                stmt.conditions_and_blocks = []
                while self.cur_token.type == TokenType.ElseIf.value:
                    el_stem = IF()
                    el_stem.token = self.cur_token
                    el_stem.consequence = self.parse_block()
                    stmt.conditions_and_blocks.append(el_stem)
            if self.cur_token.type == TokenType.Else.value:
                stmt.alternative = self.parse_block()
            return stmt
        if self.cur_token.type in for_atomic_dict:
            self.break_and_continue_in_loop += 1
            stmt = AtomicFor()
            stmt.token = self.cur_token
            stmt.body = self.parse_block()
            self.break_and_continue_in_loop -= 1
            return stmt
        else:
            stmt = Atomic()
            stmt.token = self.cur_token
            return stmt

    def __parse_component__(self) -> Optional[Node]:
        program = Component()
        program.token = self.cur_token
        program.statements = []

        self.next_token()

        end_list = [self.end_tag.format(program.token.type)]
        if program.token.type in special_token_type_end:
            end_list = special_token_type_end[program.token.type]
        elif program.token.type in exist_atomic_dict:
            end_list = special_token_type_end[TokenType.If.value]
        elif program.token.type in for_atomic_dict:
            end_list = special_token_type_end[TokenType.ForStep.value]

        while self.cur_token.type not in end_list and self.cur_token.type != TokenType.EOF.value:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()
        return program

    def __parse_child_process__(self) -> Optional[Node]:
        program = ChildProgram()
        program.token = self.cur_token
        program.statements = []

        self.next_token()

        end_list = [self.end_tag.format(program.token.type)]
        if program.token.type in special_token_type_end:
            end_list = special_token_type_end[program.token.type]
        elif program.token.type in exist_atomic_dict:
            end_list = special_token_type_end[TokenType.If.value]
        elif program.token.type in for_atomic_dict:
            end_list = special_token_type_end[TokenType.ForStep.value]

        while self.cur_token.type not in end_list and self.cur_token.type != TokenType.EOF.value:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()
        return program

    def __parse_break__(self) -> Optional[Node]:
        if self.break_and_continue_in_loop <= 0:
            self.errors.append(BreakSyntaxError)
        stmt = Break()
        stmt.token = self.cur_token
        return stmt

    def __parse_continue__(self) -> Optional[Node]:
        if self.break_and_continue_in_loop <= 0:
            self.errors.append(BreakSyntaxError)
        stmt = Continue()
        stmt.token = self.cur_token
        return stmt

    def __parse_while__(self) -> Optional[Node]:
        self.break_and_continue_in_loop += 1
        stmt = While()
        stmt.token = self.cur_token
        stmt.body = self.parse_block()
        self.break_and_continue_in_loop -= 1
        return stmt

    def __parse_for__(self) -> Optional[Node]:
        self.break_and_continue_in_loop += 1
        stmt = For()
        stmt.token = self.cur_token
        stmt.body = self.parse_block()
        self.break_and_continue_in_loop -= 1
        return stmt

    def __parse_if__(self) -> Optional[Node]:
        stmt = IF()
        stmt.token = self.cur_token
        stmt.consequence = self.parse_block()

        if self.cur_token.type == TokenType.ElseIf.value:
            stmt.conditions_and_blocks = []
            while self.cur_token.type == TokenType.ElseIf.value:
                el_stem = IF()
                el_stem.token = self.cur_token
                el_stem.consequence = self.parse_block()
                stmt.conditions_and_blocks.append(el_stem)
        if self.cur_token.type == TokenType.Else.value:
            stmt.alternative = self.parse_block()
        return stmt

    def __parse_try__(self) -> Optional[Node]:
        stmt = Try()
        stmt.token = self.cur_token
        stmt.body = self.parse_block()

        if self.cur_token.type == TokenType.Catch.value:
            catch_block_list = []
            while self.cur_token.type == TokenType.Catch.value:
                catch_block_list.append(self.parse_block())
            if len(catch_block_list) > 1:
                self.errors.append("only one catch can be retained.")
                return
            if len(catch_block_list) > 0:
                stmt.catch_block = catch_block_list[0]

        if self.cur_token.type == TokenType.Finally.value:
            stmt.finally_block = self.parse_block()
        return stmt
