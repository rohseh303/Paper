import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.tools import BaseTool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType, AgentExecutor, create_openai_functions_agent
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage

load_dotenv()

class FeedbackAgentSystem:
    def __init__(self):
        # Initialize the language model
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0)

        # Initialize all tools and the agent
        self._initialize_tools()
        self._initialize_agent()

    def _initialize_tools(self):
        # Define prompt templates and chains for each tool
        # 1. Grammar Correction Agent
        grammar_prompt = PromptTemplate(
            input_variables=["text"],
            template="Correct the grammatical errors in the following text:\n\n{text}\n\nCorrected text:",
        )
        self.grammar_correction_chain = grammar_prompt | self.llm

        # 2. Tone Modification Agent
        tone_prompt = PromptTemplate(
            input_variables=["text", "tone"],
            template="Modify the following text to have a {tone} tone:\n\n{text}\n\nModified text:",
        )
        self.tone_modification_chain = tone_prompt | self.llm

        # 4. Autocompletion Agent
        autocomplete_prompt = PromptTemplate(
            input_variables=["text"],
            template="Continue writing the following text in the same style:\n\n{text}\n\nContinued text:",
        )
        self.autocomplete_chain = autocomplete_prompt | self.llm

        # 5. Unblocking Agent
        unblock_prompt = PromptTemplate(
            input_variables=["text"],
            template="Provide suggestions for structure and flow to help the writer get unblocked based on the following:\n\n{text}\n\nSuggestions:",
        )
        self.unblocking_chain = unblock_prompt | self.llm

        # Define the functions that each tool will perform
        def correct_grammar(text):
            result = self.grammar_correction_chain.invoke({"text": text})
            return result.content

        def modify_tone(text, tone):
            result = self.tone_modification_chain.invoke({"text": text, "tone": tone})
            return result.content

        def autocomplete(text):
            result = self.autocomplete_chain.invoke({"text": text})
            return result.content

        def provide_guidance(text):
            result = self.unblocking_chain.invoke({"text": text})
            return result.content

        # Create custom tools for each agent
        class CorrectGrammarTool(BaseTool):
            name: str = "correct_grammar"
            description: str = "Corrects grammatical errors in the text."
            def _run(self, text: str):
                return correct_grammar(text)
            def _arun(self, text: str):
                raise NotImplementedError("Async not implemented")

        class ModifyToneTool(BaseTool):
            name: str = "modify_tone"
            description: str = "Modifies the tone of the text to the specified tone."
            def _run(self, text: str, tone: str):
                return modify_tone(text, tone)
            def _arun(self, text: str, tone: str):
                raise NotImplementedError("Async not implemented")

        class AutocompleteTool(BaseTool):
            name: str = "autocomplete"
            description: str = "Completes the text provided by the user."
            def _run(self, text: str):
                return autocomplete(text)
            def _arun(self, text: str):
                raise NotImplementedError("Async not implemented")

        class ProvideGuidanceTool(BaseTool):
            name: str = "provide_guidance"
            description: str = "Provides suggestions to help the writer get unblocked."
            def _run(self, text: str):
                return provide_guidance(text)
            def _arun(self, text: str):
                raise NotImplementedError("Async not implemented")

        # Initialize the tools
        self.tools = [
            CorrectGrammarTool(),
            ModifyToneTool(),
            AutocompleteTool(),
            ProvideGuidanceTool()
        ]

    def _initialize_agent(self):
        # Create a prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful writing assistant that provides feedback and suggestions."),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])

        # Create the agent
        self.agent = create_openai_functions_agent(self.llm, self.tools, prompt)

        # Create the executor
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

    def process_user_input(self, text, desired_changes=None):
        # Construct the input message
        input_message = f"Please help with this text: {text}"
        if desired_changes:
            input_message += f"\nDesired changes: {desired_changes}"

        # Run the agent executor
        response = self.agent_executor.invoke({"input": input_message})
        print("Agent response:", response)
        print("Agent output:", response["output"])
        return response["output"]

# if __name__ == "__main__":
#     agent_system = FeedbackAgentSystem()

#     # Test Grammar Correction
#     user_input = "She don't know nothing about it."
#     print("Original Text:", user_input)
#     response = agent_system.process_user_input(user_input)
#     print("Corrected Text:", response)

#     # Test Tone Modification
#     user_input = "Hey guys, what's up?"
#     desired_tone = "professional"
#     print("\nOriginal Text:", user_input)
#     response = agent_system.process_user_input(user_input, desired_changes=f"Change tone to {desired_tone}")
#     print("Modified Text:", response)
