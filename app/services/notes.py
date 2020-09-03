from ..db import notes
from ..schemas.notes import (NoteIn, Note)


class NotesService:
    async def get_all(self, database, offset: int, limit: int):
        query = notes.select().offset(offset).limit(limit)
        return await database.fetch_all(query)

    async def get_one(self, database, id: int):
        query = notes.select().where(notes.c.id == id)
        return await database.fetch_one(query)

    async def create(self, database, note: NoteIn):
        query = notes.insert().values(text=note.text,
                                      completed=note.completed)
        return await database.execute(query)

    async def update(self, database, note_id: int, note: NoteIn):
        query = notes.update().where(notes.c.id == note_id).values(
            text=note.text, completed=note.completed)
        return await database.execute(query)

    async def delete(self, database, note_id: int):
        query = notes.delete().where(notes.c.id == note_id)
        await database.execute(query)


notes_service = NotesService()
