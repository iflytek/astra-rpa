from rpa_executor.flow.syntax.token import Token, TokenType


class Lexer:
    """词法分析，主要是将flow转换成token, 并过滤flow没用的信息"""

    def __init__(self, flow_list: list, flow_to_token, child_process_flow_list):
        self.flow_to_token = flow_to_token
        self.child_process_flow_list = child_process_flow_list

        self.flow_list: list = flow_list  # list dict
        self.position: int = 0
        self.read_position: int = 0
        self.flow: dict = {}

        self.read_flow()  # 初始化

    def read_flow(self):
        """词法分析核心"""

        if self.read_position >= len(self.flow_list):
            self.flow = None
        else:
            self.flow = self.flow_list[self.read_position]
            # 如果token是执行子流程 会动态加载flow_list
            if self.child_process_flow_list:
                new_flow_list = self.child_process_flow_list(self.flow, self.flow_list, self.read_position)
                if new_flow_list:
                    self.flow_list = new_flow_list
        self.position = self.read_position
        self.read_position += 1

    def next_token(self) -> Token:
        """词法分析nex_token"""

        if self.flow is None:
            token = Token(TokenType.EOF.value)
        else:
            token = self.flow_to_token(self.flow)
            if token is None:
                # 如果token为空就过滤掉
                self.read_flow()
                return self.next_token()
        self.read_flow()
        return token
