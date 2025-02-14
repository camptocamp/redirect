from typing import Any


def setup(env: dict[str, Any]) -> None:
    """Set up the pshell environment."""
    request = env["request"]

    # start a transaction
    request.tm.begin()

    # inject some vars into the shell builtins
    env["tm"] = request.tm
    env["dbsession"] = request.dbsession
