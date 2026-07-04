from lingshu import LingShu, Request, Response

app = LingShu()


@app.get("/")
async def index(request: Request) -> Response:
    return Response.text("hello")
