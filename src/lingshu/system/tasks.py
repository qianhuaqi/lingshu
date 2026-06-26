from __future__ import annotations

import asyncio
import contextvars
import time
from collections import OrderedDict
from dataclasses import dataclass
from itertools import count

from lingshu.system.execution import current_execution_context
from lingshu.system.errors import NoRequestContextError


@dataclass
class TaskRecord:
    id: str
    name: str
    owner: str
    scope: str
    created_at: float
    state: str
    shutdown_policy: str
    task: asyncio.Task | None
    request_id: str | None = None
    trace_id: str | None = None
    operation_id: str | None = None
    deadline: float | None = None
    raw_request: object | None = None
    exception_type: str | None = None
    exception_message: str | None = None
    cancel_reason: str | None = None
    result: object | None = None

    @property
    def exception(self):
        return self.exception_message


@dataclass(frozen=True)
class TaskShutdownResult:
    records: list[TaskRecord]
    unfinished: list[TaskRecord]
    timed_out: bool = False


class TaskRegistry:
    def __init__(self, *, max_history: int = 256):
        if max_history <= 0:
            raise ValueError("max_history must be greater than zero")
        self.max_history = max_history
        self._records: dict[str, TaskRecord] = {}
        self._history: OrderedDict[str, TaskRecord] = OrderedDict()
        self._counter = count(1)
        self._closed = False

    @property
    def history_size(self) -> int:
        return len(self._history)

    def spawn(
        self,
        coro,
        *,
        name: str,
        owner: str,
        scope: str = "application",
        shutdown_policy: str = "wait",
    ) -> str:
        if not owner:
            coro.close()
            raise ValueError("Task owner is required")
        if scope not in {"request", "application", "operation"}:
            coro.close()
            raise ValueError("scope must be request, application or operation")
        if shutdown_policy not in {"wait", "cancel"}:
            coro.close()
            raise ValueError("shutdown_policy must be wait or cancel")
        if self._closed:
            coro.close()
            raise RuntimeError("TaskRegistry is closed")

        task_id = f"task-{next(self._counter)}"
        request_id = trace_id = operation_id = None
        deadline = None
        task_context = None
        try:
            execution = current_execution_context()
            request_id = execution.request_id
            trace_id = execution.trace_id
            operation_id = execution.operation_id
            deadline = execution.deadline
            if scope == "request":
                task_context = contextvars.copy_context()
        except NoRequestContextError:
            if scope == "request":
                coro.close()
                raise ValueError("request scoped task requires an active request execution context") from None

        if scope in {"application", "operation"}:
            task_context = contextvars.Context()

        task = asyncio.create_task(coro, name=name, context=task_context)
        record = TaskRecord(
            id=task_id,
            name=name,
            owner=owner,
            scope=scope,
            created_at=time.monotonic(),
            state="running",
            shutdown_policy=shutdown_policy,
            task=task,
            request_id=request_id,
            trace_id=trace_id,
            operation_id=operation_id,
            deadline=deadline,
        )
        self._records[task_id] = record
        task.add_done_callback(lambda done_task, record_id=task_id: self._complete(record_id, done_task))
        return task_id

    def _complete(self, task_id: str, task: asyncio.Task):
        record = self._records.pop(task_id, None)
        if record is None:
            return
        try:
            result = task.result()
            if result is None or isinstance(result, (str, int, float, bool)):
                record.result = result
            record.state = "done"
        except asyncio.CancelledError as exc:
            record.exception_type = type(exc).__name__
            record.exception_message = str(exc)
            record.state = "cancelled"
        except BaseException as exc:  # task exception must be consumed
            record.exception_type = type(exc).__name__
            record.exception_message = str(exc)
            record.state = "failed"
        record.task = None
        self._remember(record)

    def _remember(self, record: TaskRecord):
        self._history[record.id] = record
        self._history.move_to_end(record.id)
        while len(self._history) > self.max_history:
            self._history.popitem(last=False)

    def list(self) -> list[TaskRecord]:
        return list(self._records.values())

    def get_record(self, task_id: str) -> TaskRecord:
        if task_id in self._records:
            return self._records[task_id]
        return self._history[task_id]

    def get_result(self, task_id: str):
        return self.get_record(task_id).result

    def forget(self, task_id: str):
        if task_id in self._records:
            raise RuntimeError("Cannot forget a running task")
        del self._history[task_id]

    async def cancel(self, task_id: str, reason: str = "manual"):
        record = self._records.get(task_id)
        if record is None or record.task is None:
            return
        record.cancel_reason = reason
        record.task.cancel()
        await asyncio.gather(record.task, return_exceptions=True)

    async def cancel_all(self, reason: str = "manual"):
        await asyncio.gather(
            *(self.cancel(task_id, reason=reason) for task_id in list(self._records)),
            return_exceptions=True,
        )

    async def finish_request(self, request_id: str, timeout: float):
        tasks = [
            record.task
            for record in self._records.values()
            if record.scope == "request" and record.request_id == request_id and record.task is not None
        ]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=timeout)

    async def shutdown_and_wait(self, timeout: float) -> TaskShutdownResult:
        self._closed = True
        deadline = time.monotonic() + max(0.0, timeout)
        for record in list(self._records.values()):
            if record.shutdown_policy == "cancel" and record.task is not None:
                record.cancel_reason = "shutdown"
                record.task.cancel()

        wait_tasks = [record.task for record in self._records.values() if record.task is not None]
        timed_out = False
        if wait_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*wait_tasks, return_exceptions=True),
                    timeout=max(0.0, deadline - time.monotonic()),
                )
            except TimeoutError:
                timed_out = True
        unfinished = [record for record in self._records.values() if record.task is not None and not record.task.done()]
        return TaskShutdownResult(records=list(self._history.values()) + list(self._records.values()), unfinished=unfinished, timed_out=timed_out)
