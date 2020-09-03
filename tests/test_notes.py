import pytest
from httpx import AsyncClient
from app.main import app
from app import db


@pytest.mark.asyncio
async def test_get_note():
    note_id = 1
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await db.connect_databases()
        response = await ac.get(f'/api/notes/{note_id}/')
        await db.disconnect_databases()
    assert response.status_code == 200
    assert response.json().get('id') == 1

