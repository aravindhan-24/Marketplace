from source.handlers.pingHandler import ping

def test_ping():
    assert ping() == {"message": "ok"}