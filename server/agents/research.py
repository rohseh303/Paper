import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ZeroShotAgent
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()
logging.basicConfig(level=logging.INFO)

class ResearchAgentSystem:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initializes the ResearchAgentSystem with the specified language model.

        Args:
            model_name (str): The name of the OpenAI model to use.
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None

    def _initialize_vectorstore(self, documents):
        """
        Initializes the vector store with provided documents.

        Args:
            documents (List[Document]): List of LangChain Document objects.
        """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)

    def _initialize_tools(self):
        class WebSearchTool(BaseTool):
            name = "web_search"
            description = "Fetches content from a given URL."

            def _run(self, url: str):
                try:
                    loader = WebBaseLoader(url)
                    documents = loader.load()
                    text = "\n\n".join([doc.page_content for doc in documents])
                    return text
                except Exception as e:
                    logging.error(f"Error fetching content from {url}: {e}")
                    return "An error occurred while fetching the content."

            async def _arun(self, url: str):
                raise NotImplementedError("Async not implemented")

        class DocumentRetrievalTool(BaseTool):
            name = "document_retrieval"
            description = "Searches documents for relevant content based on a query."

            def __init__(self, vectorstore):
                self.vectorstore = vectorstore

            def _run(self, query: str):
                try:
                    docs = self.vectorstore.similarity_search(query)
                    return "\n\n".join([doc.page_content for doc in docs])
                except Exception as e:
                    logging.error(f"Error retrieving documents: {e}")
                    return "An error occurred while retrieving documents."

            async def _arun(self, query: str):
                raise NotImplementedError("Async not implemented")

        class SummarizationTool(BaseTool):
            name = "summarize"
            description = "Summarizes the given text."

            def __init__(self, llm):
                self.chain = LLMChain(
                    llm=llm,
                    prompt=PromptTemplate(
                        input_variables=["text"],
                        template="Summarize the following text:\n\n{text}\n\nSummary:"
                    )
                )

            def _run(self, text: str):
                return self.chain.run(text=text)

            async def _arun(self, text: str):
                raise NotImplementedError("Async not implemented")

        class QuestionAnsweringTool(BaseTool):
            name = "qa_tool"
            description = "Answers questions based on the given context."

            def __init__(self, llm):
                self.chain = LLMChain(
                    llm=llm,
                    prompt=PromptTemplate(
                        input_variables=["question", "context"],
                        template="Based on the following context, answer the question.\n\nContext:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
                    )
                )

            def _run(self, question: str, context: str):
                return self.chain.run(question=question, context=context)

            async def _arun(self, question: str, context: str):
                raise NotImplementedError("Async not implemented")

        self.tools = [
            WebSearchTool(),
            DocumentRetrievalTool(self.vectorstore),
            SummarizationTool(self.llm),
            QuestionAnsweringTool(self.llm)
        ]

    def _initialize_agent(self):
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True
        )

    def process_query(self, query: str) -> str:
        """
        Processes the user's query and returns the agent's response.

        Args:
            query (str): The user's query.

        Returns:
            str: The agent's response.
        """
        try:
            response = self.agent.run(input=query)
            return response
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return "An error occurred while processing your query."

if __name__ == "__main__":
    agent_system = ResearchAgentSystem()

    # Example Documents to Index
    from langchain.docstore.document import Document

    documents = [
        Document(page_content="LangChain is a framework for developing applications powered by language models."),
        Document(page_content="OpenAI's GPT models are powerful tools for natural language processing."),
        # Add more documents as needed
    ]

    # Initialize the vector store with documents
    agent_system._initialize_vectorstore(documents)
    # Initialize tools after vectorstore is ready
    agent_system._initialize_tools()
    # Initialize the agent with tools
    agent_system._initialize_agent()

    # Example Queries
    query = "What is LangChain?"
    response = agent_system.process_query(query)
    print("Response:", response)

    query = "Summarize the benefits of using GPT models."
    response = agent_system.process_query(query)
    print("Response:", response)


# Define the ResearchAgentTool
class ResearchAgentTool(BaseTool):
    name = "research_agent"
    description = (
        "Useful for when you need to perform detailed research, answer complex questions, "
        "or gather and summarize information from various sources."
    )

    def __init__(self, research_agent_system):
        self.research_agent_system = research_agent_system

    def _run(self, query: str):
        return self.research_agent_system.process_query(query)

    async def _arun(self, query: str):
        raise NotImplementedError("Async not implemented")

# Define the GeneralAgentSystem
class GeneralAgentSystem:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        self._initialize_tools()
        self._initialize_agent()

    def _initialize_tools(self):
        # Define other tools if necessary
        self.tools = [
            # Other tools...
            self.research_agent_tool
        ]

    def _initialize_agent(self):
        # Create a custom prompt if desired
        prefix = """You are a helpful assistant capable of performing various tasks using the tools available."""
        suffix = """Begin!

{chat_history}
Question: {input}
{agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools=self.tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            agent_kwargs={"prompt": prompt}
        )

    def process_input(self, user_input: str) -> str:
        try:
            response = self.agent.run(input=user_input)
            return response
        except Exception as e:
            logging.error(f"Error processing input: {e}")
            return "An error occurred while processing your request."

if __name__ == "__main__":
    # Instantiate the research agent system
    research_agent_system = ResearchAgentSystem()

    # Initialize vector store and tools for the research agent
    from langchain.docstore.document import Document

    documents = [
        Document(page_content="LangChain is a framework for developing applications powered by language models."),
        Document(page_content="OpenAI's GPT models are powerful tools for natural language processing."),
        # Add more documents as needed
    ]

    research_agent_system._initialize_vectorstore(documents)
    research_agent_system._initialize_tools()
    research_agent_system._initialize_agent()

    # Create the research agent tool
    research_agent_tool = ResearchAgentTool(research_agent_system)

    # Instantiate the general agent system and add the research agent tool
    general_agent_system = GeneralAgentSystem()
    general_agent_system.research_agent_tool = research_agent_tool
    general_agent_system._initialize_tools()
    general_agent_system._initialize_agent()

    # Example input where the general agent might decide to use the research agent
    user_input = "Can you provide a detailed summary of the benefits of using GPT models in natural language processing?"

    response = general_agent_system.process_input(user_input)
    print("Response:", response)
