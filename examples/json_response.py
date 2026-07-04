from lingshu import LingShu, Request, Response

app = LingShu()


@app.get("/status")
async def status(request: Request) -> Response:
    return Response.json({"ok": True})
