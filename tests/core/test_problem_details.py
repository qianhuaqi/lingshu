import pytest

from lingshu.core.errors import FatalScope, RequestError
from lingshu.core.identifiers import RequestId
from lingshu.core.problem import problem_from_exception
from lingshu.http.exceptions import HTTPException


def test_hidden_framework_error_maps_to_generic_problem() -> None:
    error = RequestError(
        "request.internal_contract",
        "internal route contract included private marker",
        fatal_scope=FatalScope.REQUEST,
        safe_details={"internal": "private marker"},
    )

    document = problem_from_exception(error).to_dict()

    assert document == {
        "type": "urn:lingshu:error:internal.error",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "An internal error occurred.",
        "code": "internal.error",
    }
    assert "private marker" not in repr(document)


def test_http_exception_maps_explicit_safe_problem_fields() -> None:
    request_id = RequestId.parse("0" * 32)
    error = HTTPException(404, "Missing widget", code="http.missing_widget")

    document = problem_from_exception(error, request_id=request_id).to_dict()

    assert document == {
        "type": "urn:lingshu:error:http.missing_widget",
        "title": "Missing widget",
        "status": 404,
        "detail": "Missing widget",
        "code": "http.missing_widget",
        "instance": "urn:lingshu:request:00000000000000000000000000000000",
        "request_id": "00000000000000000000000000000000",
    }


def test_problem_mapping_rejects_control_flow_base_exceptions() -> None:
    with pytest.raises(TypeError, match="control-flow BaseException"):
        problem_from_exception(KeyboardInterrupt())
