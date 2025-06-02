import pytest

import mock_ai.models.standard_image as sim
from mock_ai.models.standard_image import StandardImageModel
from mock_ai.schemas.image_request import ImageRequest
from mock_ai.utils import check_image_id, parse_dimensions


def test_standard_image_url():
    model = StandardImageModel("test")
    req = ImageRequest(
        prompt="foo", model="bar", n=2, size="32x32", output_format="jpeg"
    )
    resp = model.get_response(req, "url")
    assert len(resp.data) == 2
    for item in resp.data:
        assert item.url.startswith("private/images/")
        assert item.url.endswith(f".{req.output_format}")
        image_id = item.url[len("private/images/") :].split(".")[0]
        assert check_image_id(image_id)


def test_standard_image_b64(monkeypatch):
    width, height = parse_dimensions("64x48")
    model = StandardImageModel("test")
    req = ImageRequest(
        prompt="bar",
        model="baz",
        n=3,
        size="64x48",
        output_format="png",
        response_format="b64_json",
    )

    def fake_noise(key: str, w: int, h: int):
        assert (w, h) == (width, height)
        return f"img_{key}_{w}x{h}"

    def fake_b64(img: str, format: str) -> str:
        return f"{img}|{format}"

    monkeypatch.setattr(sim, "generate_noise_image_from_string", fake_noise)
    monkeypatch.setattr(sim, "img_to_b64", fake_b64)

    resp = model.get_response(req, "b64_json")
    assert len(resp.data) == 3
    for i, item in enumerate(resp.data):
        expected_img = (
            f"img_{req.prompt}{i}_{width}x{height}|{req.output_format}"
        )
        assert item.b64_json == expected_img


def test_standard_image_invalid_format():
    model = StandardImageModel("test")
    req = ImageRequest(prompt="foo", model="bar")
    with pytest.raises(ValueError):
        model.get_response(req, "invalid")
