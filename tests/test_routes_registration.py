from fastapi import FastAPI
from unittest.mock import MagicMock
import source.register as register_module
from source.routes import routes


def test_routes_registered(monkeypatch):
    app = FastAPI()

    monkeypatch.setattr(
        register_module,
        "loadHandler",
        lambda _: MagicMock()
    )

    register_module.registerRoutes(app)

    registered = {(r.path, tuple(r.methods)) for r in app.routes}

    for r in routes:
        assert (r["path"], (r["method"],)) in registered
