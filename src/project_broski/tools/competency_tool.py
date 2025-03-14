import os
from supabase import create_client, Client
from typing import List, Dict
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Type, Any
from crewai.tools import BaseTool

from project_broski.models.competencies import Competency


class CompetenciesToolInput(BaseModel):
    """Input schema for CompetenciesTool."""
    competency_id: UUID = Field(..., description="uuid of the competency")
    competency_name: str = Field(..., description="name of the competency")

class CompetenciesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="CompetenciesTool",
            description="Fetches existing competency definitions from Kaushalya's database",
        )
        self.args_schema: Type[BaseModel] = CompetenciesToolInput
        # Load Supabase credentials from environment variables
        supabase_url = os.getenv("APTITUDETESTS_")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials are missing. Set SUPABASE_URL and SUPABASE_KEY.")

        self.supabase: Client = create_client(supabase_url, supabase_key)

    def get_competencies_by_name(self, competency_name: str) -> List[Competency]:
        """Fetches competencies with selected fields."""
        response = self.supabase.table("competencies").select(
            "name, scope, proficiency, competency_id"
        ).eq("name", competency_name).execute()
        print(f"Found {len(response.data)} competencies for {competency_name}")
        if response.data:
            return [Competency.from_db_row(row) for row in response.data]
        return []

    def get_competencies(self, competency_ids: List[UUID]) -> List[Competency]:
        """Fetches competencies by their IDs."""
        response = self.supabase.table("competencies").select("*").in_("competency_id", competency_ids).execute()
        print(f"Found {len(response.data)} competencies")
        return [Competency.from_db_row(row) for row in response.data] if response.data else []

    def run(self, **kwargs: Any,) -> Dict:
        """Handles incoming requests from agents to search and learn from existing competencies."""
        if kwargs.get("competency_name"):
            competencies = self.get_competencies_by_name(kwargs.get("competency_name"))
            return {
                "competencies": [comp.to_dict() for comp in competencies]
            }
        elif kwargs.get("competency_ids"):
            return {"competencies": [comp.to_dict() for comp in self.get_competencies(kwargs.get("competency_ids"))]}
        else:
            return {"error": "Invalid query. Use 'search_by_competency_name' or 'get_competencies'."}
