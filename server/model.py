import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, initialize_agent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dataclasses import dataclass

load_dotenv()

# Debug prints
print("Environment variables:")
print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")
print(f"OPENAI_API_KEY value: {os.getenv('OPENAI_API_KEY')[:5]}...") # Shows first 5 chars only for security

logging.basicConfig(level=logging.ERROR)

class FeedbackAgentSystem:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initializes the FeedbackAgentSystem with the specified language model.

        Args:
            model_name (str): The name of the OpenAI model to use.
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        self._initialize_tools()
        self._initialize_agent()
        self.name = "FeedbackAgentSystem"
        self.description = "A helpful writing assistant that provides feedback and suggestions."
    
    def _initialize_tools(self):
        def create_tool(name, description, prompt_template, input_variables):

            self.name = name
            self.description = description
            prompt = PromptTemplate(
                input_variables=input_variables,
                template=prompt_template,
            )
            chain = LLMChain(prompt=prompt, llm=self.llm)
            
            @dataclass
            class CustomTool(BaseTool):
                name: str = self.name
                description: str = self.description
                 
                def _run(self, **kwargs):
                    try:
                        result = chain.run(kwargs)
                        return result
                    except Exception as e:
                        logging.error(f"Error in {self.name}: {e}")
                        return "An error occurred while processing your request."
                
                async def _arun(self, **kwargs):
                    try:
                        result = await chain.arun(kwargs)
                        return result
                    except Exception as e:
                        logging.error(f"Async error in {self.name}: {e}")
                        return "An error occurred while processing your request."
            
            return CustomTool()
        
        self.tools = [
            create_tool(
                name="correct_grammar",
                description="Corrects grammatical errors in the text.",
                prompt_template="Correct the grammatical errors in the following text:\n\n{text}\n\nCorrected text:",
                input_variables=["text"],
            ),
            create_tool(
                name="modify_tone",
                description="Modifies the tone of the text to the specified tone.",
                prompt_template="Modify the following text to have a {tone} tone:\n\n{text}\n\nModified text:",
                input_variables=["text", "tone"],
            ),
            # Add other tools similarly
        ]

    def _initialize_agent(self):
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template=(
                "You are a helpful writing assistant that provides feedback and suggestions. "
                "Use the tools available to you to assist the user.\n\n"
                "User input: {input}\n\n"
                "{agent_scratchpad}"
            ),
        )
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True,
            prompt=prompt,
        )
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

    def process_user_input(self, text: str, desired_changes: Optional[str] = None) -> str:
        """
        Processes the user's input text and applies desired changes.

        Args:
            text (str): The input text from the user.
            desired_changes (Optional[str]): Instructions for desired changes.

        Returns:
            str: The agent's output after processing.
        """
        input_message = f"Please help with this text: {text}"
        if desired_changes:
            input_message += f"\nDesired changes: {desired_changes}"
        try:
            response = self.agent_executor({"input": input_message})
            return response["output"]
        except Exception as e:
            logging.error(f"Error processing user input: {e}")
            return "An error occurred while processing your request."

if __name__ == "__main__":
    agent_system = FeedbackAgentSystem()

    # Test Grammar Correction
    user_input = "She don't know nothing about it."
    print("Original Text:", user_input)
    response = agent_system.process_user_input(user_input)
    print("Corrected Text:", response)

    # Test Tone Modification
    user_input = "Hey guys, what's up?"
    desired_tone = "professional"
    print("\nOriginal Text:", user_input)
    response = agent_system.process_user_input(user_input, desired_changes=f"Change tone to {desired_tone}")
    print("Modified Text:", response)
