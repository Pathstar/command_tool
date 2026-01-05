from command import CommandNode, ArgumentType, parse_command

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

            print("\n输入:", " ".join(tokens) or "(空)")
            result = parse_command(root, tokens)  # or root.parse_command(tokens)
            print("预览:", result.suggest())
            result.execute(player_dummy)

        print("\n\n------------------------------------------\n\n")

        for tokens in tests:
            if not tokens:
                continue
            result = x.parse_command([tokens[-1]])
            print("预览:", result.suggest())
            result.execute(player_dummy)

    demo()