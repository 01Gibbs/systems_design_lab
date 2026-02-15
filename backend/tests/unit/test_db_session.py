"""Test db session management: init_db and get_db"""
import pytest
import types
from app.infrastructure.db import session as db_session

class DummyAsyncSession:
    pass

class DummySessionMaker:
    def __init__(self): self.called = False
    def __call__(self):
        class DummyCtx:
            async def __aenter__(self): return DummyAsyncSession()
            async def __aexit__(self, exc_type, exc, tb): pass
        return DummyCtx()

def test_init_db_sets_globals(monkeypatch):
    called = {}
    def fake_create_engine(url, echo):
        called['url'] = url
        return 'engine'
    def fake_async_sessionmaker(engine, class_, expire_on_commit):
        called['engine'] = engine
        return 'maker'
    monkeypatch.setattr(db_session, 'create_async_engine', fake_create_engine)
    monkeypatch.setattr(db_session, 'async_sessionmaker', fake_async_sessionmaker)
    db_session.init_db('sqlite+aiosqlite:///:memory:')
    assert db_session.engine == 'engine'
    assert db_session.async_session_maker == 'maker'

def test_get_db_raises_if_not_initialized():
    import asyncio
    db_session.async_session_maker = None
    async def run():
        with pytest.raises(RuntimeError):
            _ = [s async for s in db_session.get_db()]
    asyncio.run(run())

def test_get_db_yields_session(monkeypatch):
    maker = DummySessionMaker()
    db_session.async_session_maker = maker
    async def run():
        result = [s async for s in db_session.get_db()]
        assert isinstance(result[0], DummyAsyncSession)
    import asyncio; asyncio.run(run())
