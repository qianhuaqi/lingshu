from lingshu.extensions.registry import setup_enabled_extensions, teardown_enabled_extensions
from lingshu.system.lifecycle import ApplicationLifecycle, InFlightRequestTracker, ShutdownCoordinator, install_health_routes
from lingshu.system.tasks import TaskRegistry


def register_lifecycle(app, extension_modules=None):
    extension_modules = list(extension_modules or [])
    lifecycle = getattr(app.ctx, "lifecycle", None)
    if lifecycle is None:
        lifecycle = ApplicationLifecycle()
        app.ctx.lifecycle = lifecycle
    if not hasattr(app.ctx, "in_flight_tracker"):
        app.ctx.in_flight_tracker = InFlightRequestTracker()
    if not hasattr(app.ctx, "task_registry"):
        app.ctx.task_registry = TaskRegistry()
    def new_shutdown_coordinator():
        app.ctx.shutdown_coordinator = ShutdownCoordinator(
            lifecycle,
            shutdown_timeout=25.0,
            cleanup_timeout=8.0,
            in_flight_tracker=app.ctx.in_flight_tracker,
            task_registry=app.ctx.task_registry,
        )

    new_shutdown_coordinator()
    install_health_routes(app, lifecycle)

    async def setup_extensions(app):
        if getattr(app.ctx, "lingshu_startup_failed", False):
            return
        if lifecycle.state.value == "stopped":
            lifecycle.restart_for_server_start()
            if getattr(app.ctx.task_registry, "_closed", False):
                app.ctx.task_registry = TaskRegistry()
            new_shutdown_coordinator()
        try:
            await setup_enabled_extensions(app, extension_modules)
        except Exception:
            app.ctx.lingshu_startup_failed = True
            raise
        if lifecycle.state.value == "starting":
            lifecycle.mark_ready()

    async def teardown_extensions(app):
        app.ctx.shutdown_coordinator.add_cleanup(lambda: teardown_enabled_extensions(app, extension_modules))
        await app.ctx.shutdown_coordinator.shutdown()

    app.ctx.lingshu_startup_listeners = tuple(
        list(getattr(app.ctx, "lingshu_startup_listeners", ())) + [setup_extensions],
    )
    app.ctx.lingshu_stop_listeners = tuple(
        list(getattr(app.ctx, "lingshu_stop_listeners", ())) + [teardown_extensions],
    )

    app.listener("before_server_start")(setup_extensions)
    app.listener("after_server_stop")(teardown_extensions)
