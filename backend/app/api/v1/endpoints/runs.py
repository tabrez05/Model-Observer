import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.run_repo import run_repo
from app.db.session import get_db
from app.schemas.run import RunCreate, RunListResponse, RunRead, RunUpdate

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunRead, status_code=status.HTTP_201_CREATED)
async def create_run(payload: RunCreate, db: AsyncSession = Depends(get_db)):
    run = await run_repo.create(db, payload)
    return run


@router.get("", response_model=RunListResponse)
async def list_runs(
    status_filter: str | None = Query(None, alias="status"),
    tags: list[str] | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    total, items = await run_repo.list_runs(
        db,
        status=status_filter,
        tags=tags,
        search=search,
        limit=limit,
        offset=offset,
    )
    return RunListResponse(total=total, items=items)


@router.get("/{run_id}", response_model=RunRead)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    run = await run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


@router.patch("/{run_id}", response_model=RunRead)
async def update_run(
    run_id: uuid.UUID,
    payload: RunUpdate,
    db: AsyncSession = Depends(get_db),
):
    run = await run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    run = await run_repo.update(db, run, payload)
    return run


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    run = await run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    await run_repo.delete(db, run)
