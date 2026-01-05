from command import CommandNode, ArgumentType, parse_command, ParseResult

# Minecraft tp 示例 （只是演示，并非按照原tp命令实现）

root = CommandNode("root")


class PlayerArg(ArgumentType):
    def parse(self, token: str):
        if token.startswith("@") or token.isalpha():
            return token
        raise ValueError("非法玩家")

    def suggestions(self):
        return ["@p", "@a", "Steve", "Alex"]


class IntArg(ArgumentType):
    def parse(self, token: str):
        # 字符串正负数数字化数字
        if token.lstrip("-").isdigit():
            return int(token)
        raise ValueError("不是整数")


def tp_executor(tokens, a_player):
    # player, target="", x=None, y=None
    # print(f"✅ TP 执行：{tokens[0]} → {} @ ({}, {})")
    print(f"✅ TP 执行 {tokens}, {a_player.__dict__}")
    # raise Exception("模拟 TP 执行报错")


# ==================================================
# Build Command Tree example 2
# ==================================================
# /tp <player> <target> <x> <y>

tp = root.add_literal(CommandNode("tp"))
root.add_literal_aliases(["teleport", "tpp", "tp_"], tp)
player = tp.add_argument(CommandNode("player", PlayerArg()))
target = player.add_argument(CommandNode("target", PlayerArg()))
x = target.add_argument(CommandNode("x", IntArg()))
y: CommandNode = x.add_argument(CommandNode("y", IntArg()))
y.consume_rest = True
y.executor = tp_executor
player.executor = tp_executor

if __name__ == "__main__":
    # ==================================================
    # Demo
    # ==================================================
    def demo():
        tests = [
            [],
            ["tp"],
            ["tp", "Steve"],
            ["tp", "Steve", "Alex"],
            ["tp", "Steve", "Alex", "100"],
            ["tp", "Steve", "Alex", "100", "64"],
            ["teleport", "Steve", "Alex", "100", "64"],
            ["tp_", "Steve", "Alex", "100", "64"],
            ["tp", "Steve", "???"],
            ["tp", "Steve", "Alex", "100", "64", "2", "3", "4", "5", "6", "7", "8", "9"],
        ]

        class PlayerEntity:
            def __init__(self, name):
                self.name = name
                self.obj_id = len(name)
                self.pos = [0, 0, 0]
                self.level = 1
                self.game_mode = "Survival"

        player_dummy = PlayerEntity("dummy")

        for tokens in tests:
            command = " ".join(tokens)
            print("\n输入:", command or "(空)")
            result = parse_command(root, command)  # or root.parse_command(tokens)
            print("预览:", result.suggest())
            result.execute(player_dummy)

        print("\n\n------------------------------------------\n\n")

        print(x.name)
        for tokens in tests:
            if not tokens:
                continue
            cmd = tokens[-1]
            print(f"\n输入: {cmd}")
            result2: ParseResult = x.parse_command(cmd)
            print("预览:", result2.suggest())
            if result2.is_success:
                result2.execute(player_dummy)
            else:
                print(f"❌ 报错： {result2.error}")


    demo()
