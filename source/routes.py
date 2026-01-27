from typing import TypedDict,Literal
from source.constants import ENDPOINT

Method = Literal["GET","POST","PUT","PATCH","DELETE"]

class RouteDef(TypedDict):
    method: Method
    path: str
    handler: str
    description: str

routes: list[RouteDef] = [
    {
        "method":"GET",
        "path": ENDPOINT+"/getToken",
        "handler":"source.handlers.authHandler:getToken",
        "description":"Provided JWT token if valid credentials passed",
    },
    {
        "method":"GET",
        "path":ENDPOINT,
        "handler":"source.handlers.pingHandler:ping",
        "description":"Endpoint to check server is alive",
    },
    {
        "method":"POST",
        "path":ENDPOINT+"/template",
        "handler":"source.handlers.templateHandler:uploadTemplate",
        "description": "To upload a template by a marketplace",
    },
    {
        "method":"GET",
        "path":ENDPOINT+"/template",
        "handler":"source.handlers.templateHandler:getTemplate",
        "description": "To fetch the uploaded template"
    },
    {
        "method":"POST",
        "path": ENDPOINT + "/uploadfile",
        "handler":"source.handlers.csvhandler:uploadfile",
        "description": "Endpoint to upload a csv file which will return discovered columns names, sample rows and row count"
    },
    {
        "method":"POST",
        "path": ENDPOINT + "/sellermapping",
        "handler":"source.handlers.mappingHandler:mapper",
        "description": "Endpoint to upload a mapping json by seller"
    },
    {
        "method":"GET",
        "path": ENDPOINT + "/sellermapping",
        "handler":"source.handlers.mappingHandler:get_mapping",
        "description": "Endpoint to view a mapping json by seller"
    },
    {
        "method":"GET",
        "path": ENDPOINT + "/sellermapping/{mapping_id}",
        "handler":"source.handlers.mappingHandler:get_mapping_by_id",
        "description": "Endpoint to view a mapping json by seller"
    },
]

