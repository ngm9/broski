import os
from typing import Type, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from supabase import create_client, Client
from project_broski.models.questions import Question
from project_broski.models.competencies import Competency
from crewai.tools import BaseTool

class QuestionsToolInput(BaseModel):
    """Input schema for QuestionsTool."""
    competency: str = Field(..., description="The competency string to use to create questions for")

class QuestionsTool(BaseTool):
    """
    Fetches existing questions from Kaushalya's database as a way to check what good questions look like
    """
    supabase: Client = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )

    def __init__(self):
        super().__init__(
            name="QuestionsTool",
            description="Fetches existing questions from Kaushalya's database as a way to check what good questions look like",
        )
        self.args_schema: Type[BaseModel] = QuestionsToolInput
        
        # Load Supabase credentials from environment variables
        supabase_url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        supabase_key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials are missing. Set SUPABASE_URL and SUPABASE_KEY.")

        self.supabase: Client = create_client(supabase_url, supabase_key)

    def get_competencies(self, competency: str, proficiency: str) -> List[Competency]:
        """Fetches competencies with selected fields."""
        print(f"Getting competencies for {competency} and proficiency: {proficiency}")
        response = self.supabase.table("competencies").select("*").ilike("material", f"%{competency}%").eq("proficiency", f"{proficiency}").execute()
        print(f"Found {len(response.data)} competencies for {competency} and proficiency: {proficiency}")
        if response.data:
            competencies = []
            for competency in response.data:
                competencies.append(Competency.from_db_row(competency))
            return competencies
        return []

    def get_sample_questions_by_competency(self, competency: str, proficiency: str) -> List[Question]:
        """Fetches questions for a specific competency name."""
        competencies = self.get_competencies(competency=competency, proficiency=proficiency)
        if not competencies:
            print(f"No competencies found for {competency}")
            return []
        
        print(f"Found {len(competencies)} competencies for {competency}")
        questions = []
        if len(competencies) > 1:
            competency_ids = [str(competency.competency_id) for competency in competencies]
            print(f"Competency IDs: {competency_ids}")
            for competency_id in competency_ids:
                try:
                    response = self.supabase.rpc("get_questions_by_competency", {"competency_id": competency_id, "num_questions": 10}).execute()
                    print(f"Found {len(response.data)} questions for competency: {competency}")
                    print(f"Response: {response.data}")
                    questions.extend([Question.from_db_row(row) for row in response.data])
                except Exception as e:
                    print(f"Error fetching questions for competency {competency_id}: {e}")
                    continue
        return questions

    def _run(self, competency: str, proficiency: str) -> Any:
        """Handles incoming requests from agents to search and learn from existing questions."""
        print(f"Getting questions for competency: {competency} and proficiency: {proficiency}")
        return {"questions": [q.to_dict() for q in self.get_sample_questions_by_competency(competency=competency, proficiency=proficiency)]}