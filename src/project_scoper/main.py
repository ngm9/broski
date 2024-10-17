#!/usr/bin/env python
import os
import sys
from textwrap import dedent
from project_scoper.crew import ProjectScoperCrew
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run():

    repo = input(
        dedent("""
         What is the github repo you want to analyze?
        """))
    inputs = {
        'repo': repo
    }
    result = ProjectScoperCrew().crew().kickoff(inputs=inputs)
    with open('result.md', 'w') as file:
      file.write(str(result))
    return result
