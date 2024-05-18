def sh_dash_c(commands: list[str], debug: bool = False) -> list[str]:
    if debug:
        commands = ["set -o xtrace"] + commands
    return ["sh", "-c", " && ".join(commands)]
