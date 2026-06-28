from __future__ import annotations

from lingshu.core import RequestId, RevisionId, WorkerId
from lingshu.record import (
    BoundedRecordQueue,
    RecordBudgets,
    RecordPolicy,
    reserve_runtime_record,
)


def test_best_effort_drop_preserves_written_event_accounting() -> None:
    queue = BoundedRecordQueue(max_items=2, max_bytes=4096)
    record = reserve_runtime_record(
        queue,
        request_id=RequestId.parse("a" * 32),
        worker_id=WorkerId.parse("b" * 32),
        revision_id=RevisionId.parse("c" * 64),
        policy=RecordPolicy.BEST_EFFORT,
        budgets=RecordBudgets(
            max_event_bytes=2048,
            max_events_per_record=1,
            max_record_bytes=2048,
        ),
    )

    assert record.append("request.first", component="record", outcome="success")
    assert record.append("request.second", component="record", outcome="dropped") is None
    assert record.event_count == 1
    assert record.dropped_events == 1
    assert record.incomplete
    assert len(queue) == 1
