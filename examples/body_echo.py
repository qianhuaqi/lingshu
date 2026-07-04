from lingshu import LingShu, Request, Response

app = LingShu()


@app.post("/echo")
async def echo(request: Request) -> Response:
    body = await request.body.read()
    return Response.bytes(body)
