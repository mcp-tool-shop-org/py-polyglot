"""Tests for the ollama module (pure logic, no network)."""

from pypolyglot.ollama import (
    OllamaClient,
    OllamaGenerateRequest,
    OllamaGenerateResponse,
    OllamaModel,
    _try_command,
)


def test_generate_request_defaults():
    req = OllamaGenerateRequest(model="test", prompt="hello")
    assert req.stream is False
    assert req.temperature is None
    assert req.num_predict is None
    assert req.top_p is None


def test_generate_response_fields():
    resp = OllamaGenerateResponse(
        model="test", response="world", done=True,
        total_duration=1000, eval_count=10,
    )
    assert resp.model == "test"
    assert resp.response == "world"
    assert resp.done is True
    assert resp.total_duration == 1000


def test_ollama_model():
    m = OllamaModel(name="translategemma:12b", size=8100000000, digest="abc123")
    assert m.name == "translategemma:12b"
    assert m.size == 8100000000


def test_client_default_url():
    client = OllamaClient()
    assert client.base_url == "http://localhost:11434"


def test_client_custom_url():
    client = OllamaClient("http://remote:11434")
    assert client.base_url == "http://remote:11434"


def test_try_command_nonexistent():
    assert _try_command("definitely_not_a_real_command_xyz") is False
