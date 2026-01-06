from command import CommandNode, ArgumentType, build_registry

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


def tp_executor(tokens, player, params=None, kwargs=None):
    # player, target="", x=None, y=None
    # print(f"✅ TP 执行：{tokens[0]} → {} @ ({}, {})")
    print(f"✅ TP 执行 {tokens}, {player.__dict__}")
    print(f"params {params}, kwargs {kwargs}")
    # raise Exception("模拟 TP 执行报错")


# 用 dict 描述命令树
command_registry_dict = {
    "tp": {
        "name": "tp",
        "aliases": ["teleport", "tpp", "tp_"],
        "lowercase": True,  # 下一层是否使token小写匹配，默认True
        "children": [
            {
                "name": "player",
                "arg": PlayerArg(),
                "executor": tp_executor,
                "children": [
                    {
                        "name": "target",
                        "arg": PlayerArg(),
                        "children": [
                            {
                                "name": "x",
                                "arg": IntArg(),
                                "children": [
                                    {
                                        "name": "y",
                                        "arg": IntArg(),
                                        "rest": True,
                                        "executor": tp_executor,
                                        "params": {"im_a_param": True}
                                    }
                                ]
                            }
                        ],
                    }
                ],
            }
        ],
    },
    "tp2": {
        "name": "tp2",
        "aliases": ["teleport2", "tpp2", "tp_2"],
        "lowercase": True,  # 下一层是否使token小写匹配，默认True]
        "executor": tp_executor,
        "rest": True,
        "children": [
            {
                "name": "-h",
                "executor": tp_executor,
            }
        ]
    }

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
            ["Tpasdasdasd"],
            ["Tp         "],
            ["tp", "Player"],
            ["Tp aasdasdasddas"],
            ["tp", "Steve"],
            ["tp", "Steve", "Alex"],
            ["tp", "Steve", "Alex", "100"],
            ["tp", "Steve", "Alex", "100", "64"],
            ["teleport", "Steve", "Alex", "100", "64"],
            ["tp_", "Steve", "Alex", "100", "64"],
            ["tp", "Steve", "???"],
            ["tp", "Steve", "Alex", "100", "64", "2", "3", "4", "5", "6", "7", "8", "9"],
            ["tp2", "aaaa", "aaa"],
            ["tp2", "-h", "aaa"],
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
            result = root.parse_command(command)
            print("预览:", result.suggest())
            result.execute(player_dummy, wtf_kwarg="wtf_value")

        print("\n\n------------------------------------------\n\n")

        #                                   player target x
        x = root.get_child_node_by_tokens(["tp", 0, 0, 0])
        print(x.name)
        for tokens in tests:
            if not tokens:
                continue
            cmd = tokens[-1]
            print(f"\n输入: {cmd}")
            result2 = x.parse_command(cmd)
            print(result2.node.name)
            print("预览:", result2.suggest())
            result2.execute(player_dummy)


    demo()

# "name": "tp",
# "aliases": ["teleport", "tpp", "tp_"],
# "lowercase": True,  # 下一层是否使token小写匹配，默认True
# "executor": tp_executor,
# "rest": False
# > tp
# 输入: Tp
# 预览: []
# ✅ TP 执行 [], {'name': 'dummy', 'obj_id': 5, 'pos': [0, 0, 0], 'level': 1, 'game_mode': 'Survival'}
# params None, kwargs {'wtf_kwarg': 'wtf_value'}
# tokens为空情况
# 为此加入    if not args:
#               args.append("")
