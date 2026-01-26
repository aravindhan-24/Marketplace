from source.model.template import MarketPlaceTemplate 

template = {}
def uploadTemplate(req: MarketPlaceTemplate):
        global template
        template = req.model_dump(exclude_none=True)
        return {"message": req.templateName}
    

def getTemplate():
    return template