#!/usr/bin/env python
from textwrap import dedent
from project_broski.crew import ProjectBroskiCrew
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def run():
    input_directory = input(
        dedent("""
         Enter the directory of inputs:
        """))
    crew = ProjectBroskiCrew(input_directory=input_directory).crew()
    result = crew.kickoff()
    
    with open('result.md', 'w') as file:
      file.write(str(result))
    return result
