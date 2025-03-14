from crewai import Crew, Process
from pathlib import Path
from project_broski.config.agents import technical_lead
from project_broski.config.tasks import create_question_generation_tasks

class ProjectBroskiCrew:
	"""Project Broski Crew"""

	def __init__(self, input_directory: str | Path):
		self.input_directory = Path(input_directory)

	def crew(self) -> Crew:
		"""Creates the Question Generation crew"""
		
		return Crew(
			agents=[technical_lead],
			tasks=create_question_generation_tasks(self.input_directory),
			process=Process.sequential,
			planning=True,
			verbose=True,
			output_log_file='output.log',
			log_file='crewai_logs.txt'
			#process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
