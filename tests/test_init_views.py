from txsentinel import create_app

def test_readiness():
    """Test test_readiness returns 200."""
    app = create_app()
    client = app.test_client()
    rv = client.get('/health')
    assert rv.data


def test_liveness():
    """Test liveness returns 200."""
    app = create_app()
    client = app.test_client()
    rv = client.get('/liveness')
    assert rv.data
