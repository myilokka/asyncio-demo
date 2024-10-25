from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    birth_year: Optional[str] = None
    eye_color: Optional[str] = None
    films: Optional[str] = None
    gender: Optional[str] = None
    hair_color: Optional[str] = None
    height: Optional[str] = None
    homeworld: Optional[str] = None
    mass: Optional[str] = None
    name: Optional[str] = None
    skin_color: Optional[str] = None
    species: Optional[str] = None
    starships: Optional[str] = None
    vehicles: Optional[str] = None
