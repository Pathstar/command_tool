# const
NAME = "name"
ALIASES = "aliases"
ARG = "arg"
REST = "rest"
EXECUTOR = "executor"
CHILDREN = "children"
LOWERCASE = "lowercase"
PARAMS = "params"

LITERAL = "literal"
ARGUMENT = "argument"

DEFAULT_is_lowercase = True
is_allow_rest = True
sep = " "


class ArgumentType:
    def parse(self, token: str):
        raise ValueError

    def suggestions(self) -> list[str]:
        return []


# ==================================================
# Parse Result
# ==================================================

class ParseResult:
    def __init__(self, node, args: dict, error: str = None):
        self.node = node
        self.args = args
        self.error = error

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_incomplete(self) -> bool:
        return not self.is_success and self.node.executor is None

    # ==================================================
    # Suggestion
    # ==================================================

    def suggest(self, suggestions: list[str] = None) -> list[str]:
        if self.error:
            return []

        if suggestions is None:
            suggestions = []

        node = self.node

        # literal
        suggestions.extend(node.literal_children.keys())

        # argument
        for arg_node in node.argument_children:
            suggestions.extend(arg_node.arg_type.suggestions() or [f"<{arg_node.name}>"])

        return suggestions

    # ==================================================
    # Executor
    # ==================================================

    def execute(self, *args, **kwargs):
        if self.error:
            print("❌ 错误：", self.error)
            return

        node = self.node
        if node.executor:
            try:
                params = node.params
                call_kwargs = {}
                if params:
                    call_kwargs["params"] = params
                if kwargs:
                    call_kwargs["kwargs"] = kwargs
                # 位置参数每个函数都要一致，关键词参数可统一写与不写
                node.executor(self.args, *args, **call_kwargs)
            except Exception as e:
                print(f"❌ 执行executor错误: {e}")
                print(node.__dict__)
        else:
            print("⚠️ 命令未完成，缺少参数")


class CommandNode:
    def __init__(self, name: str, arg_type: ArgumentType = None):
        self.name = name
        self.arg_type = arg_type  # None = literal

        self.literal_children: dict[str, CommandNode] = {}
        self.argument_children: list[CommandNode] = []

        self.consume_rest: bool = False
        self.is_lowercase: bool = DEFAULT_is_lowercase

        self.executor: callable = None
        self.params: dict = {}

    @property
    def is_argument(self) -> bool:
        return self.arg_type is not None

    def add_literal(self, node):
        name = node.name
        if name in self.literal_children:
            print(f"Warning: duplicated literal key: {name}")
        self.literal_children[name] = node
        return node

    def add_literal_aliases(self, names: list[str], node):
        for n in names:
            self.literal_children[n] = node
        return node

    def add_argument(self, node):
        self.argument_children.append(node)
        return node

    def parse_command(self, command_str: str) -> ParseResult:
        return parse_command(self, command_str)

    def parse_and_execute(self, command_str: str, *args, **kwargs) -> bool:
        """
        :param command_str:
        :param args:
        :param kwargs:
        :return: is success execute
        """
        result: ParseResult = self.parse_command(command_str)
        # print("预览:", result.suggest())
        if result.is_success:
            result.execute(*args, **kwargs)
            return True
        else:
            return False

    def build_registry(self, registry: dict):
        build_registry(self, registry)

    def remove_literal(self, node) -> int:
        to_del = [k for k, v in self.literal_children.items() if v is node]
        for k in to_del:
            del self.literal_children[k]
        return len(to_del)

    def remove_argument(self, node) -> bool:
        for i, child in enumerate(self.argument_children):
            if child is node:
                self.argument_children.pop(i)
                return True
        return False

    def remove_literal_by_name(self, name: str) -> bool:
        return self.literal_children.pop(name, None) is not None

    def get_literal_by_name(self, name: str, default=None):
        return self.literal_children.get(name, default)

    def get_argument_by_index(self, i: int, default=None):
        if i < len(self.argument_children):
            return self.argument_children[i]
        return default

    def get_argument_by_name(self, name: str, default=None):
        for node in self.argument_children:
            if node.name == name:
                return node
        return default

    def get_child_node_by_tokens(self, tokens: list[str | int], default=None, return_last=False):
        node = self
        for token in tokens:
            if isinstance(token, int):
                child_node = node.get_argument_by_index(token, None)
                if child_node is None:
                    if return_last:
                        return node
                    return default
                node = child_node
            else:
                child_node = node.get_literal_by_name(token, None)
                if child_node is None:
                    if return_last:
                        return node
                    return default
                node = child_node
        return node


# ==================================================
# Parser (遍历命令树，解析列表命令)
# ==================================================

def next_token(s: str, sep_: str = sep):
    """
    从 s 中取出下一个 token 和 rest（剩余字符串）。
    - 自动跳过开头连续分隔符
    - sep_ 为单个分隔符字符串（如 " "、","、"|" 等）
    """
    if not sep_:
        raise ValueError("sep 不能为空")
    s = s.lstrip(sep_)
    if not s:
        return None, None
    idx = s.find(sep_)
    if idx == -1:
        return s, ""
    return s[:idx], s[idx + len(sep_):]


def parse_command(root: CommandNode, command_str: str, sep_: str = sep) -> ParseResult:
    node = root
    args = {
        LITERAL: [],
        ARGUMENT: [],
    }

    rest = command_str
    while True:
        token, rest = next_token(rest, sep_)
        if token is None:
            break

        if node.is_lowercase:
            token = token.lower()

        # 1️⃣ literal 优先
        if token in node.literal_children:
            node = node.literal_children[token]
            args[LITERAL].append(token)
            continue

        # 2️⃣ argument 顺序匹配
        matched = False
        for node_arg in node.argument_children:
            try:
                value = node_arg.arg_type.parse(token)
                args[ARGUMENT].append(value)
                node = node_arg
                matched = True
                break
            except ValueError:
                continue
            except Exception as e:
                print(f"{node_arg.name} parse argument error: {e}")

        if not matched:
            # 如果当前节点设置了 consume_rest，说明这个 token 应该被吞掉
            if node.consume_rest:
                args[REST] = f"{token}{sep_}{rest}" if rest else token
                break
            return ParseResult(node, args, error=f"无法解析参数: {token}")

        # 如果 consume_rest 为 True，但我们成功匹配了当前 token，就继续循环
        if node.consume_rest and not rest:
            break

    return ParseResult(node, args)


def build(parent, node_spec, command: list[str] = None):
    node_name = node_spec[NAME]

    if ARG in node_spec:
        # --- argument ---
        command_name = f"<{node_name}>"
        if command is None:
            command = [command_name]
        else:
            command.append(command_name)

        arg_type = node_spec.get(ARG, None)
        if isinstance(arg_type, ArgumentType):
            node = CommandNode(node_name, arg_type)
            cur = parent.add_argument(node)
        else:
            raise TypeError(f"argument {command} has no parse method")
    else:
        # --- literal ---
        if command is None:
            command = [node_name]
        else:
            command.append(node_name)
        node = CommandNode(node_name)
        cur = parent.add_literal(node)
        aliases = node_spec.get(ALIASES, None)
        if aliases:
            # add_literal 可能覆写对node有包装，使用cur
            parent.add_literal_aliases(aliases, cur)

    executor_func = node_spec.get(EXECUTOR, None)
    if executor_func:
        cur.executor = executor_func

    cur.is_lowercase = node_spec.get(LOWERCASE, DEFAULT_is_lowercase)
    cur.params = node_spec.get(PARAMS, {})

    children = node_spec.get(CHILDREN, None)
    if children:
        cur.consume_rest = node_spec.get(REST, False)
        for child in node_spec.get(CHILDREN, []):
            build(cur, child, command)
    else:
        cur.consume_rest = node_spec.get(REST, is_allow_rest)

    return cur


def build_registry(root, registry: dict):
    for cmd_name, spec in registry.items():
        build(root, spec)
