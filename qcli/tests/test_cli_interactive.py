"""Test the CLI end-to-end with real imports — no mocks."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from qcli.cli import _apply_set, _handle_command, build_parser
from qcli.session import ChatSession, GenerationConfig, parse_command


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_default_args():
    args = build_parser().parse_args([])
    assert args.model == "Qwen/Qwen3.5-2B"
    assert args.temperature == 0.7
    assert args.top_p == 0.9
    assert args.max_new_tokens == 512
    assert args.quantized == "none"
    assert args.device == "auto"
    assert args.dtype == "auto"
    assert args.no_stream is False
    assert args.trust_remote_code is False
    assert args.history_file is None


def test_all_args():
    args = build_parser().parse_args([
        "--model", "my/model",
        "--temperature", "0.3",
        "--top-p", "0.5",
        "--max-new-tokens", "128",
        "--system", "Be brief.",
        "--device", "cpu",
        "--dtype", "float16",
        "--quantized", "4bit",
        "--trust-remote-code",
        "--history-file", "/tmp/h.json",
        "--no-stream",
    ])
    assert args.model == "my/model"
    assert args.temperature == 0.3
    assert args.top_p == 0.5
    assert args.max_new_tokens == 128
    assert args.system == "Be brief."
    assert args.device == "cpu"
    assert args.dtype == "float16"
    assert args.quantized == "4bit"
    assert args.trust_remote_code is True
    assert args.history_file == "/tmp/h.json"
    assert args.no_stream is True


def test_quantized_choices():
    for choice in ("none", "4bit", "8bit"):
        args = build_parser().parse_args(["--quantized", choice])
        assert args.quantized == choice

    with pytest.raises(SystemExit):
        build_parser().parse_args(["--quantized", "16bit"])


# ---------------------------------------------------------------------------
# parse_command
# ---------------------------------------------------------------------------

def test_parse_command_not_a_command():
    assert parse_command("hello") is None
    assert parse_command("") is None
    assert parse_command("hello /world") is None


def test_parse_command_basic():
    assert parse_command("/help") == ("help", [])
    assert parse_command("/exit") == ("exit", [])


def test_parse_command_with_args():
    assert parse_command("/set temperature 0.2") == ("set", ["temperature", "0.2"])
    assert parse_command("/save /tmp/out.json") == ("save", ["/tmp/out.json"])
    assert parse_command("/system Be concise.") == ("system", ["Be", "concise."])


# ---------------------------------------------------------------------------
# _apply_set
# ---------------------------------------------------------------------------

def test_apply_set_temperature():
    session = ChatSession()
    result = _apply_set(session, "temperature", "0.3")
    assert session.config.temperature == 0.3
    assert "0.3" in result


def test_apply_set_top_p():
    session = ChatSession()
    result = _apply_set(session, "top_p", "0.5")
    assert session.config.top_p == 0.5
    assert "0.5" in result


def test_apply_set_max_new_tokens():
    session = ChatSession()
    result = _apply_set(session, "max_new_tokens", "128")
    assert session.config.max_new_tokens == 128
    assert "128" in result


def test_apply_set_unknown_key():
    session = ChatSession()
    with pytest.raises(ValueError, match="unknown key"):
        _apply_set(session, "bogus", "1")


def test_apply_set_bad_value():
    session = ChatSession()
    with pytest.raises(ValueError):
        _apply_set(session, "temperature", "not_a_number")


# ---------------------------------------------------------------------------
# _handle_command
# ---------------------------------------------------------------------------

def test_handle_exit():
    session = ChatSession()
    assert _handle_command(session, "exit", []) is True


def test_handle_quit():
    session = ChatSession()
    assert _handle_command(session, "quit", []) is True


def test_handle_help():
    session = ChatSession()
    assert _handle_command(session, "help", []) is False


def test_handle_clear():
    session = ChatSession()
    session.add_user("hi")
    session.add_assistant("hey")
    assert len(session.messages) == 3  # system + user + assistant
    _handle_command(session, "clear", [])
    assert len(session.messages) == 1  # only system prompt left
    assert session.messages[0]["role"] == "system"


def test_handle_save(tmp_path):
    session = ChatSession(system_prompt="test sys")
    session.add_user("hello")
    session.add_assistant("world")
    path = str(tmp_path / "out.json")

    _handle_command(session, "save", [path])
    assert Path(path).exists()

    data = json.loads(Path(path).read_text())
    assert data["system_prompt"] == "test sys"
    assert len(data["messages"]) == 3


def test_handle_save_no_args():
    session = ChatSession()
    assert _handle_command(session, "save", []) is False


def test_handle_load(tmp_path):
    # save a session to disk
    original = ChatSession(system_prompt="loaded sys")
    original.add_user("q1")
    original.add_assistant("a1")
    path = str(tmp_path / "saved.json")
    original.save(path)

    # load into a fresh session
    session = ChatSession()
    _handle_command(session, "load", [path])
    assert session.system_prompt == "loaded sys"
    assert session.messages[-2]["content"] == "q1"
    assert session.messages[-1]["content"] == "a1"


def test_handle_load_no_args():
    session = ChatSession()
    assert _handle_command(session, "load", []) is False


def test_handle_system():
    session = ChatSession()
    _handle_command(session, "system", ["Be", "concise."])
    assert session.system_prompt == "Be concise."
    # reset clears history but keeps new system prompt
    assert len(session.messages) == 1
    assert session.messages[0]["content"] == "Be concise."


def test_handle_system_no_args():
    session = ChatSession()
    assert _handle_command(session, "system", []) is False


def test_handle_set():
    session = ChatSession()
    _handle_command(session, "set", ["temperature", "0.1"])
    assert session.config.temperature == 0.1


def test_handle_set_bad_args():
    session = ChatSession()
    assert _handle_command(session, "set", []) is False
    assert _handle_command(session, "set", ["only_one"]) is False


def test_handle_set_invalid_key():
    session = ChatSession()
    # should not crash
    assert _handle_command(session, "set", ["nope", "1"]) is False


def test_handle_unknown_command():
    session = ChatSession()
    assert _handle_command(session, "xyzzy", []) is False


# ---------------------------------------------------------------------------
# ChatSession
# ---------------------------------------------------------------------------

def test_session_init_default():
    s = ChatSession()
    assert s.system_prompt == "You are a helpful assistant."
    assert len(s.messages) == 1
    assert s.messages[0] == {"role": "system", "content": "You are a helpful assistant."}


def test_session_init_custom():
    s = ChatSession(system_prompt="Custom.")
    assert s.messages[0]["content"] == "Custom."


def test_session_add_messages():
    s = ChatSession()
    s.add_user("hi")
    s.add_assistant("hello")
    assert len(s.messages) == 3
    assert s.messages[1] == {"role": "user", "content": "hi"}
    assert s.messages[2] == {"role": "assistant", "content": "hello"}


def test_session_reset():
    s = ChatSession(system_prompt="S")
    s.add_user("a")
    s.add_assistant("b")
    s.reset()
    assert s.messages == [{"role": "system", "content": "S"}]


def test_session_set_system_prompt():
    s = ChatSession()
    s.add_user("old msg")
    s.set_system_prompt("New prompt")
    assert s.system_prompt == "New prompt"
    assert len(s.messages) == 1  # history wiped
    assert s.messages[0]["content"] == "New prompt"


def test_session_save_load_roundtrip(tmp_path):
    s = ChatSession(system_prompt="rt test")
    s.config.temperature = 0.42
    s.config.top_p = 0.88
    s.config.max_new_tokens = 256
    s.add_user("question")
    s.add_assistant("answer")

    path = tmp_path / "session.json"
    s.save(path)

    loaded = ChatSession.load(path)
    assert loaded.system_prompt == "rt test"
    assert loaded.config.temperature == 0.42
    assert loaded.config.top_p == 0.88
    assert loaded.config.max_new_tokens == 256
    assert len(loaded.messages) == 3
    assert loaded.messages[1]["content"] == "question"
    assert loaded.messages[2]["content"] == "answer"


def test_session_save_load_empty(tmp_path):
    s = ChatSession()
    path = tmp_path / "empty.json"
    s.save(path)

    loaded = ChatSession.load(path)
    assert len(loaded.messages) == 1
    assert loaded.messages[0]["role"] == "system"


def test_generation_config_defaults():
    c = GenerationConfig()
    assert c.temperature == 0.7
    assert c.top_p == 0.9
    assert c.max_new_tokens == 512
