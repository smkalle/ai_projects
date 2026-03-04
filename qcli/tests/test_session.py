from pathlib import Path

from qcli.session import ChatSession, parse_command


def test_parse_command() -> None:
    assert parse_command("hello") is None
    assert parse_command("/help") == ("help", [])
    assert parse_command("/set temperature 0.2") == ("set", ["temperature", "0.2"])


def test_save_load_roundtrip(tmp_path: Path) -> None:
    session = ChatSession(system_prompt="system test")
    session.add_user("u")
    session.add_assistant("a")

    path = tmp_path / "chat.json"
    session.save(path)

    loaded = ChatSession.load(path)
    assert loaded.system_prompt == "system test"
    assert loaded.messages[-2]["content"] == "u"
    assert loaded.messages[-1]["content"] == "a"


def test_reset_keeps_system_prompt() -> None:
    session = ChatSession(system_prompt="S")
    session.add_user("hello")
    session.reset()
    assert session.messages == [{"role": "system", "content": "S"}]
