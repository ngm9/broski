from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel

@dataclass
class Competency():
    competency_id: UUID
    scope: str
    proficiency: str
    name: str
    material: str
    created_at: datetime
    language_agnostic: bool
    long_scope: str

    @classmethod
    def from_db_row(cls, row: dict):
        return cls(
            competency_id=UUID(row['competency_id']),
            scope=row['scope'],
            proficiency=row['proficiency'],
            name=row['name'],
            material=row['material'],
            created_at=datetime.fromisoformat(row['created_at']),
            language_agnostic=row['language_agnostic'],
            long_scope=row['long_scope']
        )

    def to_dict(self) -> dict:
        return {
            'competency_id': str(self.competency_id),
            'scope': self.scope,
            'proficiency': self.proficiency,
            'name': self.name,
            'material': self.material,
            'created_at': self.created_at.isoformat(),
            'language_agnostic': self.language_agnostic,
            'long_scope': self.long_scope
        }

class Competencies(BaseModel):
    competencies: List[Competency]
