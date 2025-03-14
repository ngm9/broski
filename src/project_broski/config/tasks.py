from crewai import Task
from typing import List
from project_broski.models.questions import Questions
from project_broski.tools.question_tool import QuestionsTool
from project_broski.config.agents import technical_lead
from pathlib import Path

def load_text_file(file_path: Path) -> str:
    """Load content from a text file"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path) as f:
        return f.read().strip()

def create_question_generation_tasks(input_directory: Path) -> List[Task]:
    """Create all tasks for question generation from input files"""
    
    try:
        # Load required inputs
        company_context = load_text_file(input_directory / "company-context.txt")
        roles_responsibilities = load_text_file(input_directory / "roles.txt")
        competencies = load_text_file(input_directory / "competencies.txt")
        
        # Load optional inputs with defaults
        question_type = load_text_file(input_directory / "question-type.txt")
        question_format = load_text_file(input_directory / "question-format.txt")
            
        # Load instructions and examples
        instructions = load_text_file(input_directory / "instructions.txt")
        prompt = load_text_file(input_directory / "prompt.txt")
        
    except FileNotFoundError as e:
        print(f"Missing required input file: {e}")
        raise FileNotFoundError(f"Missing required input file: {e}")

    # Create tasks
    context_task = Task(
        description=f"""
            Analyze and summarize the company context and role requirements.
            
            Company Context:
            {company_context}
            
            Roles and Responsibilities:
            {roles_responsibilities}
            
            Provide a clear summary of:
            1. The company's main business and culture
            2. Key responsibilities for the role
            3. Required skills and experience level
        """,
        expected_output="A comprehensive summary of the company and role requirements.",
        agent=technical_lead,
        output_file="context_analysis.txt"
    )

    requirements_task = Task(
        description=f"""
            Review the previous context analysis: {{context_analysis.txt}}
            
            Instructions:
            {instructions}
            
            Competencies:
            {competencies}
            
            Question Type:
            {question_type}
            
            Question Format:
            {question_format}

            Based on this understanding and the provided instructions and competencies, analyze what kind of questions need to be generated.        
        """,
        expected_output="A detailed analysis of question requirements and competency alignment.",
        agent=technical_lead,
        context=[context_task],
        output_file="requirements_analysis.txt"
    )

    good_examples_task = Task(
        description=f"""
            Use the QuestionsTool to get a list of 10 questions that are relevant to {competencies}.

            If there are multiple competencies, then call the QuestionsTool with a combination of competency name and proficiency level, individually and collect the results for each competency.
        """,
        expected_output="A list of questions that are relevant to the competency.",
        agent=technical_lead,
        context=[context_task, requirements_task],
        output_file="examples.txt"
    )

    # TODO: Add bad examples
    questions_task = Task(
        description=f"""
            Review all previous analyses:
            
            Context Analysis: {{context_analysis.txt}}
            
            Requirements Analysis: {{requirements_analysis.txt}}
            
            Example Analysis: {{examples.txt}}
            
            Keeping in mind the above analysis, use the following prompt to generate the questions. Remember to use the same format as the examples. Ensure you include code snippets and scenarios in the questions.
            {prompt}
        """,
        expected_output="A JSON array of questions following the specified format",
        agent=technical_lead,
        context=[context_task, requirements_task, good_examples_task],
        tools=[QuestionsTool()],
        output_pydantic=Questions,
        output_file="generated_questions.json"
    )

    return [context_task, requirements_task, good_examples_task, questions_task]

#requirements_creation = Task(
#    description="""
#        Talk to the customer and create a list of technical requirements for a given role. 
#        The customer's requirements can be vague and unclear. Summarizing the requirements into a list of technical requirements is the goal.
#        From the given inputs, if it is not clear what tasks should a person in the required role be required to perform, then ask the customer for clarification on the command line.
#        From the given inputs, if it is not clear what technical skills and concepts should a candidate have mastery over, ask the customer for clarification on the command line.
#        From the given inputs, if it is not clear what tools and technologies should a candidate be proficient in, ask the customer for clarification on the command line.
#        From the given inputs, if it is not clear what experience level should a candidate have, ask the customer for clarification on the command line.
#        From the given inputs, if it is not clear what location should a candidate be based in, ask the customer for clarification on the command line.
#        From the given inputs, if it is not clear what the pay range for the required role is, ask the customer for clarification on the command line.
#    """,
#    expected_output="""
#        A list of technical requirements for a given role. This list of technical requirements should be distilled and concise.
#        E.g. 
#        ["should be able to write backend nodejs code including route management", 
#        "should be able to write and maintain beautiful web pages using frontend frameworks",
#        "should be comfortable with pay in the range of $100k-$150k and is based out of Bangalore"]
#    """,
#    agent=talent_coordinator,
#    tools=["CompetenciesTool", "QuestionsTool"],
#    output_file="requirements.json"
#)

#competency_definitions = Task(
#    description="""
#        Given a list of technical requirements, create a list of technical competencies, define scope, proficiency and experience from a given list of technical requirements. 
#        The proficiency should be either of "BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED", "EXPERT"
#        STEPS to execute this task:
#        1. From the given list of technical requirements, create a list of technical competencies e.g. "Python - Backend Development - BASIC", "NodeJS - Backend Development - INTERMEDIATE", "ReactJS - Frontend Development - ADVANCED"
#        2. For each such competency, use the CompetenciesTool to check if similar competenices exist in the database. If the existing competency scope look like they will cover the given technical requirements, then use that competency.
#        3. If the existing competency scope does not cover the given technical requirements, then create a new competency.
#        4. For each such new competency, create the UUID, name, proficiency, scope and detailed scope. 
#        5. Use the following guidelines to create the detailed scope. The output of this should be stored in a variable called "detailed_scope". Substitute <NAME OF COMPETENCY> with the name of the competency. The prompt is:
#          - The detailed scope must answer the following prompt: "You are a helpful assistant to a Technical Architect who is helping him create a competency matrix by defining competency scopes across levels of proficiency. I am looking to define the scope of <NAME OF COMPETENCY> as a competency. There are 5 proficiency levels - BEGINNER, BASIC, INTERMEDIATE, ADVANCED, EXPERT. 
#            The scope must contain what someone with that proficiency level in that competency should be able to accomplish, some idea about tasks, outcomes, tools used to perform those tasks, demonstrate mastery over concepts, technical expertise, designing complex systems or processes, operating, troubleshooting, explaining and or improving existing systems with that competency.
#             For lower levels of proficiency - BEGINNER, BASIC and INTERMEDIATE, it is far more important to have fundamentals correct and concepts clear in terms of applying foundational principles. For higher levels of proficiency - ADVANCED and EXPERT, it is important to have depth and expertise in fundamentals clear but also a breadth of knowledge around lesser known facts, concepts and frameworks.
#             What all should be a part of the scope for an INTERMEDIATE proficiency level? This person usually ends having 3-5 years of experience with <NAME OF COMPETENCY> as a competency. They are not as good as an EXPERT (10+ years of experience) proficiency level or an ADVANCED (6-10 years experience) but they are better than a person who has BASIC (1-2 years) or BEGINNER (0 years experience) proficiency in <NAME OF COMPETENCY>"
#         5. For the scope, use the following prompt to create the scope from the output of the detailed scope. The output of this should be stored in a variable called "scope". The prompt is: 
#             "The previous detailed scope will be used to generate questions to assess someone's level of proficiency. Can you restructure your above answer to be concise and short within 10-12 sentences. The focus is not on grammatically correct, but being exhaustive in its content. 
#             Please make it a paragraph and ensure you don't miss any technical concepts, tools, libraries, frameworks etc that you identified above."
#     """,
#     expected_output="""
#         A list of technical competencies with their scope and proficiency levels.
#     """,
#     agent=technical_architect,
#     tools=[CompetenciesTool],
#     context=[requirements_creation],
#     output_pydantic=Competencies,
#     output_file="competencies.json"
# )


# 
# def generate_input_based_questions(
#   prompt,
#   company_context,
#   roles_and_responsibilities,
#   competency_list,
#   question_type,
#   question_format,
#   instructions,
#   good_example,
#   bad_example
# ):
#   model = "gpt-4o"  # Specified model version
  
#   try:
#     # 1. Initial system prompt
#     messages = [{
#       "role": "system", 
#       "content": "You are a helpful assistant to a technical leader who is looking to generate 30 questions that will be used in assessing candidates."
#     }]
    
#     # 2. Context prompt
#     context_prompt = f"""
#     Let me provide you with some context about the company and role:
    
#     Company Context:
#     {company_context}
    
#     Roles and Responsibilities:
#     {roles_and_responsibilities}
    
#     Based on this information, could you summarize what you understand about the company and role requirements?
#     """
    
#     messages.append({"role": "user", "content": context_prompt})
#     response = openai_client.chat.completions.create(
#        model=model,
#        messages=messages
#     )
#     messages.append({"role": "assistant", "content": response.choices[0].message.content})
#     logger.info("=== Context Prompt===")
#     logger.info(f"Context Prompt: {context_prompt}")
#     logger.info("=== Context prompt response ===")
#     logger.info(f"Context prompt response: {response.choices[0].message.content}")

#     # 3. Instructions prompt
#     instruction_prompt = f"""
#     Now let me explain what kind of questions we need:  
    
#     Instructions:
#     {instructions}

#     Competencies:
#     {competency_list}

#     Question Type:
#     {question_type}
    
#     Question Format:
#     {question_format}
    
#     Could you summarize your understanding of what kind of questions you need to generate?
#     """
    
#     messages.append({"role": "user", "content": instruction_prompt})
#     response = openai_client.chat.completions.create(
#       model=model,
#       messages=messages
#     )
#     messages.append({"role": "assistant", "content": response.choices[0].message.content})
#     logger.info("=== Instruction Prompt===")
#     logger.info(f"Instruction Prompt: {instruction_prompt}")
#     logger.info("=== Instruction prompt response ===")
#     logger.info(f"Instruction prompt response: {response.choices[0].message.content}")

    
#     # 3.5 Competency clarification prompt
#     competency_prompt = f"""
#     Let me clarify the core competencies we are hiring for:
    
#     Competencies for generating the questions
#     {competency_list}
    
#     Could you explain how you'll ensure the questions target and evaluate these specific competencies?
#     """
    
#     messages.append({"role": "user", "content": competency_prompt})
#     response = openai_client.chat.completions.create(
#       model=model,
#       messages=messages
#     )
#     messages.append({"role": "assistant", "content": response.choices[0].message.content})
#     logger.info("=== Competency Prompt===")
#     logger.info(f"Competency Prompt: {competency_prompt}")
#     logger.info("=== Competency prompt response ===")
#     logger.info(f"Competency prompt response: {response.choices[0].message.content}")

    
#     # 4. Examples prompt
#     examples_prompt = f"""
#     Here are examples to guide you:
    
#     Good Question Example:
#     {good_example}
    
#     Bad Question Example:
#     {bad_example}
    
#     Based on these examples, what have you understood about what makes a good question versus a bad question?
#     """
    
#     messages.append({"role": "user", "content": examples_prompt})
#     response = openai_client.chat.completions.create(
#       model=model,
#       messages=messages
#     )
#     messages.append({"role": "assistant", "content": response.choices[0].message.content})
#     logger.info("=== Examples Prompt===")
#     logger.info(f"Examples Prompt: {examples_prompt}")
#     logger.info("=== Examples prompt response ===")
#     logger.info(f"Examples prompt response: {response.choices[0].message.content}")
    
#     # 5. Final generation prompt
#     final_prompt = f"""
#     Now, based on all the context, instructions, and examples provided, please generate a list of questions in pure JSON format, without any extra text. Ensure your output matches the OUTPUT FORMAT mentioned above.
    
#     Here is the prompt you MUST adhere to for creating the questions:         
#     {prompt}
#     """
    
#     messages.append({"role": "user", "content": final_prompt})
#     response = openai_client.chat.completions.create(
#       model=model,
#       messages=messages
#     )
#     content = response.choices[0].message.content.strip()
#     logger.info("=== Final Prompt===")
#     logger.info(f"Final Prompt: {final_prompt}")
#     logger.info("=== Final prompt response ===")
#     logger.info(f"Final prompt response: {response.choices[0].message.content}")
    
#     # logger.info conversation history in human readable format
#     logger.info("=== Conversation History ===")
#     for i, msg in enumerate(messages):
#       logger.info(f"\n[{msg['role'].upper()}] Message {i+1}:")
#       logger.info(f"{msg['content']}\n")
#     logger.info("=== End Conversation History ===\n")
#   except openai.OpenAIError as e:
#       return {"error": str(e)}
#   return messages, content



# question_generation = Task(
#     description="""
#         Given a list of technical competencies - {competency}, generate a list of 10 questions, complete with scenarios and code snippets, adheres to format mentioned to assess a candidate's skill and fundamental understanding of given technical competencies. Uses existing examples to learn from.

#     INSTRUCTIONS:
#     1. First use the QuestionsTool to get a list of 10 questions that are relevant to {competency}.
#     2. Use these as a golden set of questions to learn from.

#     3. Some types of codeScenario questions are as follows. Pick one of these:
#         - Identify Bugs: Provide code with a subtle bug and ask the reader to identify issues.
#         - Identify Inefficiencies: Provide code with an inefficiency and ask the reader to explain how they would address it.
#         - Suggest Optimizations: Show code with room for optimization, asking for suggested improvements.
#         - Present a scenario, show the code and ask for approach to measure performance
#         - Show code and show output scenario, ask for the approach to reach there
#         - Show code and show failure output and ask for debugging approach
    
    
#     """,
#     expected_output="""
#         A list of 10 questions, complete with scenarios and code snippets, adheres to format mentioned to assess a candidate's skill and fundamental understanding of given technical competencies.
        
#     """,
#     agent=technical_lead,
#     tools=[QuestionsTool()],
#     output_pydantic=Questions,
#     output_file="questions.json"
# )