from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import SerperDevTool, ScrapeWebsiteTool, YoutubeVideoSearchTool
from crewai_tools import SerplyWebpageToMarkdownTool, SerplyWebSearchTool


@CrewBase
class ProjectBroskiCrew():
	"""Project Broski Crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def tech_lead(self) -> Agent:
		return Agent(
			config=self.agents_config['tech_lead'],
			tools=[SerperDevTool(), ScrapeWebsiteTool(),
		  			SerplyWebpageToMarkdownTool(), SerplyWebSearchTool(), YoutubeVideoSearchTool()],
			verbose=True,
			memory=False
		) 
	
	@task
	def finding_resources_task(self) -> Task:
		return Task(
			config=self.tasks_config['finding_resources_task'],
			agent=self.tech_lead()
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates the Finding Resources crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks= self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			#planning=True,
			verbose=True,
			output_log_file='output.log',
			log_file='crewai_logs.txt'
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
