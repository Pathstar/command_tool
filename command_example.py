from command import CommandNode, ArgumentType, build_registry, parse_command

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




# ==================================================
# Build Command Tree example 1
# ==================================================
# /tp <player> <target> <x> <y>



def tp_executor(args):
    # player, target="", x=None, y=None
    print(f"✅ TP 执行：{args[0]} → {args[1]} @ ({args[2]}, {args[3]})")

# 用 dict 描述命令树
command_registry_dict = {
    "tp": {
        "type": "literal",
        "name": "tp",
        "children": [
            {
                "type": "argument",
                "name": "player",
                "arg": PlayerArg(),
                "executor": tp_executor,
                "children": [
                    {
                        "type": "argument",
                        "name": "target",
                        "arg": PlayerArg(),
                        "children": [
                            {
                                "type": "argument",
                                "name": "x",
                                "arg": IntArg(),
                                "children": [
                                    {
                                        "type": "argument",
                                        "name": "y",
                                        "arg": IntArg(),
                                        "executor": tp_executor,  # ✅ 绑定在叶子节点
                                    }
                                ]
                            }
                        ],
                    }
                ],
            }
        ],
    },
    # "cmd2...": {
    #
    # }

}

build_registry(root, command_registry_dict)








# ==================================================
# Build Command Tree example 2
# ==================================================
# /tp <player> <target> <x> <y>

# tp = root.add_literal(CommandNode("tp"))
# player = tp.add_argument(CommandNode("player", PlayerArg()))
# target = player.add_argument(CommandNode("target", PlayerArg()))
# x = target.add_argument(CommandNode("x", IntArg()))
# y = x.add_argument(CommandNode("y", IntArg()))
# y.executor = tp_executor

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
            ["tp", "Steve", "???"],
        ]

        for tokens in tests:
            print("\n输入:", " ".join(tokens) or "(空)")
            result = parse_command(root, tokens)
            print("预览:", result.suggest())
            result.execute()



    demo()
