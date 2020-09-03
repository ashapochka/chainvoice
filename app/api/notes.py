from typing import List
from fastapi import (Depends, APIRouter)
from ..deps import get_db
from ..services.notes import notes_service
from ..schemas.notes import (NoteIn, Note)


router = APIRouter()


# noinspection PyTypeChecker
@router.get("/", response_model=List[Note])
async def read_notes(db = Depends(get_db), skip: int = 0, take: int = 20):
    return await notes_service.get_all(db, skip, take)


@router.get("/{note_id}/", response_model=Note)
async def read_notes(*, db = Depends(get_db), note_id: int):
    return await notes_service.get_one(db, note_id)


@router.post("/", response_model=Note)
async def create_note(*, db = Depends(get_db), note: NoteIn):
    last_record_id = await notes_service.create(db, note)
    return {**note.dict(), "id": last_record_id}


@router.put("/{note_id}/", response_model=Note)
async def update_note(*, db = Depends(get_db), note_id: int, note: NoteIn):
    await notes_service.update(db, note_id, note)
    return {**note.dict(), "id": note_id}


@router.delete("/{note_id}/")
async def delete_note(*, db = Depends(get_db), note_id: int):
    await notes_service.delete(db, note_id)
    return {"message": "Note with id: {} deleted successfully!".format(note_id)}
