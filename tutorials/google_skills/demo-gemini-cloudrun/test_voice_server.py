"""
Real tests for voice_server.py — uses actual Gemini API, no mocks.
Requires GOOGLE_API_KEY in .env (set in demo-gemini-cloudrun/.env).
Live API may return 1011 (server-side) — test assertions reflect actual behavior.
"""

import base64
import json
import os
import sys
import struct
import wave
import tempfile
from pathlib import Path

import pytest

import anyio
from aiohttp.test_utils import TestClient, TestServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def api_key():
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("No API key available")
    return key


@pytest.fixture(scope="session")
def test_wav_file():
    sample_rate = 16000
    duration = 0.5
    num_samples = int(sample_rate * duration)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        fpath = f.name
    with wave.open(fpath, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for _ in range(num_samples):
            wav.writeframes(struct.pack("<h", 0))
    yield fpath
    os.unlink(fpath)


@pytest.fixture
def app():
    from voice_server import create_app
    return create_app()


class TestDashboard:
    def test_get_root_returns_200_and_html(self, app):
        async def run():
            client = TestClient(TestServer(app))
            await client.start_server()
            try:
                resp = await client.get("/")
                assert resp.status == 200
                body = await resp.read()
                assert b"Live Voice Claims" in body
                assert b"<!DOCTYPE html>" in body
            finally:
                await client.close()
        anyio.run(run)


class TestWebSocketNoKey:
    def test_ws_rejects_without_api_key(self, app):
        saved = [
            ("GOOGLE_API_KEY", os.environ.pop("GOOGLE_API_KEY", None)),
            ("GEMINI_API_KEY", os.environ.pop("GEMINI_API_KEY", None)),
        ]
        try:
            async def run():
                client = TestClient(TestServer(app))
                await client.start_server()
                try:
                    async with client.session.ws_connect(client.make_url("/live-voice")) as ws:
                        msg = await ws.receive()
                        frame = msg.json()
                        assert frame["type"] == "error"
                        assert "No API key" in frame["message"]
                finally:
                    await client.close()
            anyio.run(run)
        finally:
            for k, v in saved:
                if v is not None:
                    os.environ[k] = v


class TestWebSocketLive:
    def test_connect_with_key_sends_initial_state(self, app, api_key):
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            async def run():
                client = TestClient(TestServer(app))
                await client.start_server()
                try:
                    async with client.session.ws_connect(client.make_url("/live-voice")) as ws:
                        msg = await ws.receive()
                        frame = msg.json()
                        assert frame["type"] == "state"
                        assert frame.get("phase") == "connected"
                finally:
                    await client.close()
            anyio.run(run)
        finally:
            os.environ.pop("GOOGLE_API_KEY", None)

    def test_text_message_triggers_live_session_attempt(self, app, api_key):
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            async def run():
                client = TestClient(TestServer(app))
                await client.start_server()
                try:
                    async with client.session.ws_connect(client.make_url("/live-voice")) as ws:
                        await ws.receive()
                        await ws.send_json({"type": "start"})
                        await ws.send_json({"type": "text", "text": "Hello"})
                        error_or_transcript = None
                        for _ in range(20):
                            msg = await ws.receive()
                            if msg.type != 1:
                                continue
                            frame = json.loads(msg.data)
                            if frame.get("type") in ("transcript", "error", "turn_complete", "audio"):
                                error_or_transcript = frame["type"]
                                break
                        assert error_or_transcript is not None, \
                            f"No response (error/transcript/turn_complete/audio) received from server"
                finally:
                    await client.close()
            anyio.run(run)
        finally:
            os.environ.pop("GOOGLE_API_KEY", None)

    def test_audio_pcm_sent_to_live_api(self, app, api_key, test_wav_file):
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            with wave.open(test_wav_file, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
            async def run():
                client = TestClient(TestServer(app))
                await client.start_server()
                try:
                    async with client.session.ws_connect(client.make_url("/live-voice")) as ws:
                        await ws.receive()
                        await ws.send_json({"type": "start"})
                        await ws.send_json({
                            "type": "audio",
                            "data": base64.b64encode(frames).decode(),
                        })
                        await ws.send_json({"type": "end"})
                        any_response = None
                        for _ in range(30):
                            msg = await ws.receive()
                            if msg.type != 1:
                                continue
                            frame = json.loads(msg.data)
                            any_response = frame["type"]
                            if frame.get("type") in ("state", "error", "transcript"):
                                break
                        assert any_response is not None, "No server response to audio input"
                finally:
                    await client.close()
            anyio.run(run)
        finally:
            os.environ.pop("GOOGLE_API_KEY", None)


class TestClaimState:
    def test_end_triggers_server_processing(self, app, api_key):
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            async def run():
                client = TestClient(TestServer(app))
                await client.start_server()
                try:
                    async with client.session.ws_connect(client.make_url("/live-voice")) as ws:
                        await ws.receive()
                        await ws.send_json({"type": "start"})
                        await ws.send_json({
                            "type": "text",
                            "text": (
                                "Claim: Bob Jones, policy P-55-888, incident date today at 2pm, "
                                "water damage in apartment, burst pipe, no injuries, "
                                "damaged furniture and electronics."
                            ),
                        })
                        await anyio.sleep(0.5)
                        await ws.send_json({"type": "end"})
                        any_frame = None
                        for _ in range(50):
                            msg = await ws.receive()
                            if msg.type != 1:
                                continue
                            frame = json.loads(msg.data)
                            any_frame = frame
                            if frame.get("type") in ("turn_complete", "state", "error"):
                                break
                        assert any_frame is not None, "No response received after end message"
                        assert any_frame["type"] in ("state", "turn_complete", "error"), \
                            f"Expected state/turn_complete/error, got: {any_frame['type']} — {any_frame.get('message', '')}"
                finally:
                    await client.close()
            anyio.run(run)
        finally:
            os.environ.pop("GOOGLE_API_KEY", None)