from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db


router = APIRouter(prefix="/team", tags=["team"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=schemas.TeamMember, status_code=status.HTTP_201_CREATED)
def create_member(member: schemas.TeamMemberCreate, db: DatabaseSession):
    """Create, commit, and refresh a team member.

    Args:
        member: Member data used to construct the database model.
        db: SQLAlchemy session used to persist and refresh the member.

    Returns:
        models.TeamMember: The committed and refreshed member instance.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: If a session operation fails.
    """
    db_member = models.TeamMember(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.get("/", response_model=list[schemas.TeamMember])
def list_members(db: DatabaseSession):
    return db.scalars(select(models.TeamMember)).all()


@router.get("/by-team/{team_name}", response_model=list[schemas.TeamMember])
def list_members_by_team(team_name: str, db: DatabaseSession):
    members = db.scalars(
        select(models.TeamMember).where(models.TeamMember.team == team_name)
    ).all()
    if not members:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No members found for this team",
        )
    return members