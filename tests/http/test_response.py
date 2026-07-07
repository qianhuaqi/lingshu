from __future__ import annotations

import math

import pytest
from lingshu.core import LifecycleError
from lingshu.core.errors import LingShuError
from lingshu.http import Response, ResponseState, normalize_response


def test_response_factories_prepare_commit_and_complete() -> None:
    response = Response.text("hello")
    assert response.state == ResponseState.NEW
    assert response.headers.get("content-type") == "text/plain; charset=utf-8"

    head = response.prepare()
    assert response.state.value == ResponseState.PREPARED.value
    assert head.headers.get("content-length") == "5"

    response.write(b"!")
    assert response.state == ResponseState.NEW
    head = response.commit()
    assert head.headers.get("content-length") == "6"
    assert response.state.value == ResponseState.COMMITTED.value

    with pytest.raises(LifecycleError) as duplicate:
        response.commit()
    assert duplicate.value.code == "response.invalid_state"
    with pytest.raises(LifecycleError):
        response.set_header("x-test", "value")
    response.complete()
    assert response.state.value == ResponseState.COMPLETED.value
    with pytest.raises(LifecycleError):
        response.abort()


def test_json_response_factory_sets_deterministic_body_and_headers() -> None:
    response = Response.json({"message": "你好", "ok": True}, status=201)

    assert response.status == 201
    assert response.body == b'{"message":"\xe4\xbd\xa0\xe5\xa5\xbd","ok":true}'
    assert response.headers.get("content-type") == "application/json; charset=utf-8"

    head = response.commit()
    assert head.status == 201
    assert head.headers.get("content-type") == "application/json; charset=utf-8"
    assert head.headers.get("content-length") == str(len(response.body))


def test_json_response_factory_preserves_custom_content_type_and_headers() -> None:
    response = Response.json(
        {"ok": True},
        headers=(
            ("content-type", "application/vnd.example+json"),
            ("x-trace", "abc"),
        ),
    )

    assert response.body == b'{"ok":true}'
    assert response.headers.get("content-type") == "application/vnd.example+json"
    assert response.headers.get("x-trace") == "abc"


def test_json_response_rejects_non_serializable_values() -> None:
    with pytest.raises(TypeError):
        Response.json(object())


def test_json_response_rejects_non_finite_floats() -> None:
    with pytest.raises(ValueError):
        Response.json({"value": math.nan})


def test_abort_is_terminal_and_idempotent() -> None:
    response = Response.bytes(b"payload", status=202)
    assert response.abort()
    assert not response.abort()
    assert response.state is ResponseState.ABORTED
    with pytest.raises(LifecycleError):
        response.write(b"later")


def test_return_normalization_is_exactly_once() -> None:
    assert normalize_response("hello").body == b"hello"
    assert normalize_response(bytearray(b"bytes")).body == b"bytes"
    assert normalize_response(memoryview(b"view")).body == b"view"

    response = Response.bytes(b"ok")
    assert normalize_response(response) is response
    with pytest.raises(LingShuError) as duplicate:
        normalize_response(response)
    assert duplicate.value.code == "handler.return_already_normalized"


@pytest.mark.parametrize("value", [None, ("body", 200), iter([b"body"]), object()])
def test_invalid_return_values_fail_explicitly(value: object) -> None:
    with pytest.raises(LingShuError) as captured:
        normalize_response(value)
    assert captured.value.code == "handler.invalid_return"
