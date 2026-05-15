from fastapi import Request
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
scope = {"type": "http", "method": "GET"}
request = Request(scope)

try:
    print("Calling TemplateResponse")
    res = templates.TemplateResponse(request=request, name="index.html")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
