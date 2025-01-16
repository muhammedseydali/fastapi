from enum import Enum
from pydantic import BaseModel, validator
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class GenreURLChoices(Enum):
    ROCK = 'rock'
    ELECTRONIC = 'electronic'
    METAL = 'metal'
    HIP_HOP = 'hip-hop'

class AlbumBase(SQLModel):
    title: str
    release_date: date
    band_id: int | None = Field(foreign_key="bandwithid.id")  # Use the actual table name

class Albums(AlbumBase, table=True):
    id: int = Field(default=None, primary_key=True)
    band: Optional["BandWithId"] = Relationship(back_populates="albums")

class BandBase(SQLModel):
    name: str
    genre: str

class BandCreate(BandBase):
    albums: Optional[List[AlbumBase]] = None

    @validator('genre', pre=True)
    def validate_genre(cls, value):
        if value.lower() not in [genre.value for genre in GenreURLChoices]:
            raise ValueError(f"Invalid genre: {value}")
        return value.lower()

class BandWithId(BandBase, table=True):
    id: int = Field(default=None, primary_key=True)
    albums: List[Albums] = Relationship(back_populates="band")
