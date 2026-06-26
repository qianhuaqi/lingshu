import asyncio
import gc
import weakref
from types import SimpleNamespace

import pytest
from sanic import Sanic

from lingshu import request
from lingshu.lifecycle import register_lifecycle
from lingshu.response import json_response
from lingshu.router import compile_route_policies
from lingshu.system.errors import NoRequestContextError
from lingshu.system.execution import current_execution_context
from lingshu.system import sanic_adapter
from lingshu.system.lifecycle import (
    ApplicationLifecycle,
    InFlightRequestTracker,
    LifecycleState,
    ShutdownCoordinator,
    install_health_routes,
)
from lingshu.system.policy import RoutePolicyCompiler, RoutePolicyDefinition, RoutePolicyError, set_route_policy
from lingshu.system.tasks import TaskRegistry


async def _run_startup(app):
    for listener in getattr(app.ctx, "lingshu_startup_listeners", ()):
        await listener(app)


async def _run_stop(app):
    for listener in getattr(app.ctx, "lingshu_stop_listeners", ()):
        await listener(app)


def test_create_app_lifecycle_remains_starting_until_startup(monkeypatch):
    from lingshu.app import create_app

    monkeypatch.setenv("MYSQL_ENABLED", "false")
    monkeypatch.setenv("REDIS_ENABLED", "false")
    monkeypatch.setenv("MONGO_ENABLED", "false")

    app = create_app()

    assert app.ctx.lifecycle.state == LifecycleState.STARTING
    asyncio.run(_run_startup(app))
    assert app.ctx.lifecycle.state == LifecycleState.READY


def test_startup_failure_keeps_app_not_ready_and_business_returns_503():
    app = Sanic("startup-failure")

    class BadExtension:
        @staticmethod
        async def setup(app):
            raise RuntimeError("dependency down")

    register_lifecycle(app, [BadExtension])

    @app.get("/business", name="business")
    async def business(request):
        return json_response({"ok": True})

    compile_route_policies(app)

    async def scenario():
        with pytest.raises(RuntimeError, match="dependency down"):
            await _run_startup(app)
        assert app.ctx.lifecycle.state == LifecycleState.STARTING
        _, response = await app.asgi_client.get("/business")
        assert response.status == 503

    asyncio.run(scenario())


def test_missing_compiled_policy_fails_closed_for_dynamic_route():
    app = Sanic("missing-policy")
    sanic_adapter.install_context_middleware(app)
    register_lifecycle(app, [])

    @app.get("/known", name="known")
    async def known(request):
        return json_response({"ok": True})

    compile_route_policies(app)

    @app.get("/dynamic", name="dynamic")
    async def dynamic(request):
        return json_response({"ok": True})

    app.ctx.lifecycle.mark_ready()

    async def scenario():
        _, response = await app.asgi_client.get("/dynamic")
        assert response.status == 500
        assert response.json["code"] == 990001

    asyncio.run(scenario())


def test_route_policy_compiler_rejects_empty_and_duplicate_route_names():
    app = Sanic("bad-policy-names")

    @app.get("/a", name="same")
    async def a(request):
        return None

    @app.get("/b", name="same")
    async def b(request):
        return None

    with pytest.raises(RoutePolicyError, match="Duplicate"):
        RoutePolicyCompiler().compile_app(app)

    empty_app = Sanic("empty-policy-name")

    @empty_app.get("/empty", name="empty")
    async def empty(request):
        return None

    next(iter(empty_app.router.routes_all.values())).name = ""
    with pytest.raises(RoutePolicyError, match="empty"):
        RoutePolicyCompiler().compile_app(empty_app)


def test_health_routes_have_explicit_public_compiled_policy():
    app = Sanic("health-policy")
    lifecycle = ApplicationLifecycle()
    install_health_routes(app, lifecycle)
    compiled = compile_route_policies(app)

    for name in ("lingshu.live", "lingshu.ready", "lingshu.health"):
        policy = compiled.for_route(name)
        assert policy.public is True
        assert policy.auth_required is False
        assert policy.maintenance_check is False
        assert policy.timeout <= 2.0
        assert policy.audit_level == "none"


def test_application_task_created_in_request_uses_clean_context():
    async def scenario():
        registry = TaskRegistry()
        seen = {}

        async def job():
            for key, accessor in {
                "raw": lambda: request.raw,
                "user": lambda: request.user,
                "execution": lambda: request.execution,
                "current_execution": current_execution_context,
            }.items():
                try:
                    accessor()
                except NoRequestContextError:
                    seen[key] = "clean"
                else:
                    seen[key] = "leaked"

        context = current_execution_context
        with pytest.raises(NoRequestContextError):
            context()

        from lingshu.system.execution import RequestExecutionContext, bind_execution_context
        from lingshu.system.policy import CompiledRoutePolicy

        execution = RequestExecutionContext(
            request_id="rid-clean",
            trace_id="trace-clean",
            route_policy=CompiledRoutePolicy("probe", True, False, False, 1.0, None, "none"),
            deadline=999.0,
            lifecycle_state="ready",
        )
        with bind_execution_context(execution):
            task_id = registry.spawn(job(), name="clean", owner="application", scope="application")

        await registry.shutdown_and_wait(timeout=1.0)
        assert registry.get_record(task_id).request_id == "rid-clean"
        assert seen == {
            "raw": "clean",
            "user": "clean",
            "execution": "clean",
            "current_execution": "clean",
        }

    asyncio.run(scenario())


def test_request_task_can_access_context_but_is_cancelled_at_request_end():
    async def scenario():
        registry = TaskRegistry()
        started = asyncio.Event()
        cleaned = asyncio.Event()

        async def job():
            try:
                assert request.execution.request_id == "rid-request-task"
                started.set()
                await asyncio.Event().wait()
            finally:
                cleaned.set()

        from lingshu.system.execution import RequestExecutionContext, bind_execution_context
        from lingshu.system.policy import CompiledRoutePolicy

        execution = RequestExecutionContext(
            request_id="rid-request-task",
            trace_id="trace-request-task",
            route_policy=CompiledRoutePolicy("probe", True, False, False, 1.0, None, "none"),
            deadline=999.0,
            lifecycle_state="ready",
        )
        with bind_execution_context(execution):
            registry.spawn(job(), name="request-task", owner="request", scope="request")
            await started.wait()
            await registry.finish_request("rid-request-task", timeout=1.0)

        assert cleaned.is_set()
        assert registry.list() == []

    asyncio.run(scenario())


def test_task_registry_history_is_bounded_and_forget_releases_records():
    async def scenario():
        registry = TaskRegistry(max_history=3)

        class BigResult:
            pass

        big = BigResult()
        ref = weakref.ref(big)

        async def return_big(value):
            return value

        registry.spawn(return_big(big), name="big", owner="application", scope="application")
        big = None
        last = None
        for index in range(10):
            last = registry.spawn(return_big(index), name=f"short-{index}", owner="application", scope="application")
        await registry.shutdown_and_wait(timeout=1.0)
        await asyncio.sleep(0)
        gc.collect()
        assert ref() is None
        assert registry.history_size <= 3

        registry.forget(last)
        with pytest.raises(KeyError):
            registry.get_record(last)

    asyncio.run(scenario())


def test_shutdown_coordinator_uses_total_deadline_and_concurrent_callers_share_result():
    async def scenario():
        lifecycle = ApplicationLifecycle()
        lifecycle.mark_ready()
        order = []

        async def slow(name):
            order.append(name)
            await asyncio.Event().wait()

        coordinator = ShutdownCoordinator(lifecycle, shutdown_timeout=0.05, cleanup_timeout=1.0)
        coordinator.add_cleanup(lambda: slow("first"))
        coordinator.add_cleanup(lambda: slow("second"))

        result1, result2 = await asyncio.gather(coordinator.shutdown(), coordinator.shutdown())

        assert result1 is result2
        assert result1.timed_out is True
        assert result1.state == LifecycleState.STOPPED
        assert order == ["second"]

    asyncio.run(scenario())


def test_shutdown_waits_for_inflight_requests_and_reports_timeout():
    async def scenario():
        lifecycle = ApplicationLifecycle()
        lifecycle.mark_ready()
        tracker = InFlightRequestTracker()
        release = asyncio.Event()

        async def request_work():
            async with tracker.track():
                await release.wait()

        request_task = asyncio.create_task(request_work())
        await asyncio.sleep(0)

        coordinator = ShutdownCoordinator(
            lifecycle,
            shutdown_timeout=0.05,
            cleanup_timeout=0.01,
            in_flight_tracker=tracker,
        )
        result = await coordinator.shutdown()
        release.set()
        await request_task

        assert result.timed_out is True
        assert result.unfinished_requests == 1
        assert lifecycle.state == LifecycleState.STOPPED

    asyncio.run(scenario())


def test_sanic_stop_listener_runs_shutdown_coordinator_and_cleanup():
    app = Sanic("listener-shutdown")
    cleanup_called = asyncio.Event()

    class Extension:
        @staticmethod
        async def teardown(app):
            cleanup_called.set()

    sanic_adapter.install_context_middleware(app)
    register_lifecycle(app, [Extension])
    compile_route_policies(app)

    async def scenario():
        _, response = await app.asgi_client.get("/live")
        assert response.status == 200
        assert cleanup_called.is_set()
        assert app.ctx.lifecycle.state == LifecycleState.STOPPED
        assert app.ctx.shutdown_coordinator._result.state == LifecycleState.STOPPED

    asyncio.run(scenario())


def test_request_deadline_returns_stable_timeout_and_runs_finally():
    app = Sanic("deadline-boundary")
    sanic_adapter.install_context_middleware(app)
    register_lifecycle(app, [])
    finalized = asyncio.Event()

    @app.get("/slow", name="slow")
    async def slow(request):
        try:
            await asyncio.Event().wait()
        finally:
            finalized.set()

    set_route_policy(slow, RoutePolicyDefinition(public=True, auth_required=False, timeout=0.01))
    compile_route_policies(app)
    app.ctx.lifecycle.mark_ready()

    async def scenario():
        _, response = await app.asgi_client.get("/slow")
        assert response.status == 504
        assert response.json["code"] == 990002
        assert finalized.is_set()
        with pytest.raises(NoRequestContextError):
            current_execution_context()

    asyncio.run(scenario())


def test_multi_app_runtime_state_is_isolated():
    app_a = Sanic("app-a")
    app_b = Sanic("app-b")
    sanic_adapter.install_context_middleware(app_a)
    sanic_adapter.install_context_middleware(app_b)
    register_lifecycle(app_a, [])
    register_lifecycle(app_b, [])

    @app_a.get("/a", name="a")
    async def route_a(request):
        return json_response({"request_id": current_execution_context().request_id})

    @app_b.get("/b", name="b")
    async def route_b(request):
        return json_response({"request_id": current_execution_context().request_id})

    compile_route_policies(app_a)
    compile_route_policies(app_b)
    app_a.ctx.lifecycle.mark_ready()
    app_b.ctx.lifecycle.mark_ready()

    assert app_a.ctx.lifecycle is not app_b.ctx.lifecycle
    assert app_a.ctx.route_policies is not app_b.ctx.route_policies
    assert app_a.ctx.task_registry is not app_b.ctx.task_registry
    assert app_a.ctx.in_flight_tracker is not app_b.ctx.in_flight_tracker

    async def scenario():
        _, response_a = await app_a.asgi_client.get("/a", headers={"X-Request-ID": "a"})
        _, response_b = await app_b.asgi_client.get("/b", headers={"X-Request-ID": "b"})

        assert response_a.json["data"]["request_id"] == "a"
        assert response_b.json["data"]["request_id"] == "b"

        assert app_b.ctx.lifecycle.state == LifecycleState.STOPPED
        app_b.ctx.lifecycle.restart_for_server_start()
        app_b.ctx.lifecycle.mark_ready()

        await app_a.ctx.shutdown_coordinator.shutdown()
        assert app_a.ctx.lifecycle.state == LifecycleState.STOPPED
        assert app_b.ctx.lifecycle.state == LifecycleState.READY

    asyncio.run(scenario())
