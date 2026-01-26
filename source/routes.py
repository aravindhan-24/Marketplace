from typing import TypedDict,Literal

Method = Literal["GET","POST","PUT","PATCH","DELETE"]

class RouteDef(TypedDict):
    method: Method
    path: str
    handler: str
    description: str

routes: list[RouteDef] = [
    {
        "method":"GET",
        "path":"/getToken",
        "handler":"source.handlers.auth.authHandler:getToken",
        "description":"Provided JWT token if valid credentials passed",
    },
    {
        "method":"GET",
        "path":"/",
        "handler":"source.handlers.pingHandler:ping",
        "description":"ping handler",
    },
    {
        "method":"POST",
        "path":"/template",
        "handler":"source.handlers.template.templateHandler:uploadTemplate",
        "description": "To upload a template by a marketplace",
    },
    {
        "method":"GET",
        "path":"/template",
        "handler":"source.handlers.template.templateHandler:getTemplate",
        "description": "To fetch the uploaded template"
    },
]

