from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel

@dataclass
class Question():
    question_id: UUID
    created_at: datetime | None = None
    question_blob_en: dict | None = None  # For JSONB
    criterias: dict | None = None  # For JSONB
    type: str | None = None
    language_agnostic: bool | None = None

    @classmethod
    def from_db_row(cls, row: dict):
        print(f"Row: {row}")
        return cls(
            question_id=UUID(row['question_id']),
            created_at=row.get('created_at'),
            question_blob_en=row.get('question_blob_en'),
            criterias=row.get('criterias'),
            type=row.get('type'),
            language_agnostic=row.get('language_agnostic')
        )

    def to_dict(self) -> dict:
        return {
            'question_id': str(self.question_id),
            'created_at': str(self.created_at) if self.created_at else None,
            'question_blob_en': self.question_blob_en,
            'criterias': self.criterias,
            'type': self.type,
            'language_agnostic': self.language_agnostic
        }

class Questions(BaseModel):
    questions: List[Question]