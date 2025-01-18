#!/usr/bin/env python
import os
import sys
from textwrap import dedent
from project_broski.crew import ProjectBroskiCrew
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run():
    skill = input(
        dedent("""
         What is the skill you want to learn about?
        """))
    inputs = {
        'skill': skill
    }
    result = ProjectBroskiCrew().crew().kickoff(inputs=inputs)
    with open('result.md', 'w') as file:
      file.write(str(result))
    return result
