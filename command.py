
from typing import Callable

LITERAL = "literal"
ARGUMENT = "argument"
# ==================================================
# Argument Types
# ==================================================


class ArgumentType:
    def parse(self, token: str):
        raise ValueError

    def suggestions(self) -> list[str]:
        return []


# ==================================================
# Command Node (核心结构)
# ==================================================

class CommandNode:
    def __init__(self, name: str, arg_type: ArgumentType = None):
        self.name = name
        self.arg_type = arg_type  # None = literal

        self.literal_children: dict[str, CommandNode] = {}
        self.argument_children: list[CommandNode] = []

        self.executor: Callable | None = None

    @property
    def is_argument(self) -> bool:
        return self.arg_type is not None

    def add_literal(self, node):
        self.literal_children[node.name] = node
        return node

    def add_argument(self, node):
        self.argument_children.append(node)
        return node


# ==================================================
# Parse Result
# ==================================================

class ParseResult:
    def __init__(self, node: CommandNode, args: list, error: str = None):
        self.node = node
        self.args = args
        self.error = error

    # ==================================================
    # Suggestion
    # ==================================================

    def suggest(self) -> list[str]:
        if self.error:
            return []

        node = self.node
        suggestions = []

        # literal
        suggestions.extend(node.literal_children.keys())

        # argument
        for arg in node.argument_children:
            suggestions.extend(arg.arg_type.suggestions() or [f"<{arg.name}>"])

        return suggestions


    # ==================================================
    # Executor
    # ==================================================

    def execute(self):
        if self.error:
            print("❌ 错误：", self.error)
            return

        node = self.node
        if node.executor:
            try:
                node.executor(*self.args)
            except Exception as e:
                print(e)
                print(node.__dict__)
        else:
            print("⚠️ 命令未完成，缺少参数")

# ==================================================
# Parser (唯一遍历命令树的地方)
# ==================================================

def parse_command(root: CommandNode, tokens: list[str]) -> ParseResult:
    node = root
    args = []

    for token in tokens:
        # 1️⃣ literal 优先（O(1)）
        if token in node.literal_children:
            node = node.literal_children[token]
            continue

        # 2️⃣ argument 顺序匹配
        matched = False
        for arg_node in node.argument_children:
            try:
                value = arg_node.arg_type.parse(token)
                args.append(value)
                node = arg_node
                matched = True
                break
            except ValueError:
                continue

        if not matched:
            return ParseResult(node, args, error=f"无法解析参数: {token}")

    return ParseResult(node, args)



def build(parent, node_spec, command=""):
    node_name = node_spec["name"]
    command += f" {node_name}"
    if node_spec["type"] == "literal":
        node = CommandNode(node_name)
        cur = parent.add_literal(node)
    else:
        arg = node_spec.get("arg", None)
        if arg is None:
            print(f"Waring: {command} 无 argument No parse class")
        node = CommandNode(node_name, arg)
        cur = parent.add_argument(node)

    if "executor" in node_spec:
        node.executor = node_spec["executor"]

    for child in node_spec.get("children", []):
        build(cur, child, command)
    return cur

def build_registry(root, registry: dict):
    for cmd_name, spec in registry.items():
        build(root, spec)










