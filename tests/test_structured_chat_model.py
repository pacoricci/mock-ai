import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.modules.pop("mock_ai", None)
sys.modules.pop("mock_ai.models", None)
sys.modules.pop("mock_ai.schemas", None)
sys.modules.pop("mock_ai.schemas.chat_completion_request", None)

from mock_ai.models.structured_chat import StructuredChatModel  # noqa: E402
from mock_ai.schemas.chat_completion_request import ModelSettings  # noqa: E402


def test_structured_chat_json_object():
    model = StructuredChatModel()
    settings = ModelSettings(
        messages=[{"role": "user", "content": "ciao"}],
        response_format={"type": "json_object"},
    )
    resp = model.get_response(settings, False)
    data = json.loads(resp.choices[0].message.content)
    assert isinstance(data, dict)


def test_structured_chat_json_schema_stream():
    model = StructuredChatModel()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }
    settings = ModelSettings(
        messages=[{"role": "user", "content": "foo"}],
        response_format={"type": "json_schema", "json_schema": schema},
    )
    chunks = list(model.get_response(settings, True))
    content = "".join(c.choices[0].delta.content or "" for c in chunks)
    data = json.loads(content)
    assert set(data.keys()) == {"name", "age"}
