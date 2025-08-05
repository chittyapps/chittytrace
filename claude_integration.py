import os
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
import logging

from anthropic import Anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import VECTOR_DB_PATH

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize Claude
        self.client = Anthropic(api_key=self.api_key)
        self.chat_model = ChatAnthropic(
            api_key=self.api_key,
            model="claude-3-5-sonnet-20241022",
            temperature=0.0,
            max_tokens=4096
        )
        
        # Initialize embeddings and vector store
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.vector_store = Chroma(
            persist_directory=str(VECTOR_DB_PATH),
            embedding_function=self.embeddings
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index documents into vector store for semantic search"""
        logger.info(f"Indexing {len(documents)} documents...")
        
        # Convert to LangChain documents
        langchain_docs = []
        for doc in documents:
            if doc.get("content"):
                # Split large documents
                chunks = self.text_splitter.split_text(doc["content"])
                for i, chunk in enumerate(chunks):
                    metadata = {
                        "file_path": doc["file_path"],
                        "file_name": doc["file_name"],
                        "category": doc["category"],
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                    langchain_docs.append(
                        Document(page_content=chunk, metadata=metadata)
                    )
        
        # Add to vector store
        if langchain_docs:
            self.vector_store.add_documents(langchain_docs)
            logger.info(f"Indexed {len(langchain_docs)} document chunks")
    
    def search_documents(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant documents using semantic search"""
        return self.vector_store.similarity_search(query, k=k)
    
    async def analyze_with_context(self, query: str, context_docs: Optional[List[Document]] = None) -> str:
        """Analyze query with relevant document context"""
        if context_docs is None:
            context_docs = self.search_documents(query)
        
        # Build context from documents
        context = "\n\n".join([
            f"File: {doc.metadata['file_name']}\n{doc.page_content[:1000]}..."
            for doc in context_docs[:5]
        ])
        
        messages = [
            SystemMessage(content="""You are an expert financial analyst specializing in fund flow analysis, 
            property transactions, and financial documentation. Analyze the provided documents and answer 
            questions with specific references to the source documents."""),
            HumanMessage(content=f"""Based on the following document context, please answer this query: {query}
            
            Document Context:
            {context}
            
            Please provide specific details and cite the source documents.""")
        ]
        
        response = await self.chat_model.ainvoke(messages)
        return response.content
    
    async def generate_package(self, package_type: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a document package based on requirements"""
        prompt = f"""Generate a comprehensive {package_type} package with the following requirements:
        {json.dumps(requirements, indent=2)}
        
        Create a structured package that includes:
        1. Executive summary
        2. Required documents list
        3. Document compilation instructions
        4. Review checklist
        
        Format the response as a JSON structure."""
        
        messages = [
            SystemMessage(content="You are an expert at creating financial and legal document packages."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.chat_model.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"raw_response": response.content}
    
    async def fill_form(self, form_template: str, data: Dict[str, Any]) -> str:
        """Fill out a form template with provided data"""
        prompt = f"""Fill out the following form template with the provided data:
        
        Form Template:
        {form_template}
        
        Data to fill:
        {json.dumps(data, indent=2)}
        
        Return the completed form with all fields filled accurately."""
        
        messages = [
            SystemMessage(content="You are an expert at accurately filling out financial and legal forms."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.chat_model.ainvoke(messages)
        return response.content
    
    async def execute_analysis_command(self, command: str, parameters: Dict[str, Any]) -> Any:
        """Execute complex analysis commands"""
        command_handlers = {
            "trace_funds": self._trace_funds,
            "generate_timeline": self._generate_timeline,
            "analyze_transactions": self._analyze_transactions,
            "create_affidavit": self._create_affidavit,
            "compile_evidence": self._compile_evidence,
            "calculate_penalties": self._calculate_penalties
        }
        
        handler = command_handlers.get(command)
        if handler:
            return await handler(parameters)
        else:
            return {"error": f"Unknown command: {command}"}
    
    async def _trace_funds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trace fund flow from source to destination"""
        source_account = params.get("source_account")
        destination = params.get("destination")
        date_range = params.get("date_range")
        
        # Search for relevant transactions
        query = f"trace funds from {source_account} to {destination}"
        if date_range:
            query += f" between {date_range['start']} and {date_range['end']}"
        
        docs = self.search_documents(query)
        
        prompt = f"""Trace the flow of funds from {source_account} to {destination}.
        Create a detailed fund flow analysis including:
        1. All intermediate transactions
        2. Dates and amounts
        3. Account numbers and institutions
        4. Supporting documentation references
        
        Context documents:
        {[doc.page_content[:500] for doc in docs[:5]]}"""
        
        response = await self.chat_model.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "fund_trace": response.content,
            "source_documents": [doc.metadata["file_name"] for doc in docs[:5]]
        }
    
    async def _generate_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a timeline of events"""
        topic = params.get("topic", "all events")
        date_range = params.get("date_range")
        
        query = f"timeline of {topic}"
        docs = self.search_documents(query, k=20)
        
        prompt = f"""Generate a detailed timeline for: {topic}
        
        Include:
        1. Date and time of each event
        2. Description of what occurred
        3. Supporting document references
        4. Key participants or entities involved
        
        Format as a chronological list."""
        
        response = await self.chat_model.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "timeline": response.content,
            "source_documents": list(set([doc.metadata["file_name"] for doc in docs]))
        }
    
    async def _analyze_transactions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transactions based on criteria"""
        account = params.get("account")
        criteria = params.get("criteria", {})
        
        query = f"transactions for {account}"
        docs = self.search_documents(query)
        
        prompt = f"""Analyze transactions for account: {account}
        
        Criteria: {json.dumps(criteria, indent=2)}
        
        Provide:
        1. Transaction summary
        2. Patterns identified
        3. Anomalies or notable transactions
        4. Statistical analysis
        5. Supporting documentation"""
        
        response = await self.chat_model.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "analysis": response.content,
            "source_documents": [doc.metadata["file_name"] for doc in docs[:10]]
        }
    
    async def _create_affidavit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an affidavit based on facts"""
        affiant = params.get("affiant")
        facts = params.get("facts", [])
        purpose = params.get("purpose")
        
        prompt = f"""Create a legal affidavit for:
        Affiant: {affiant}
        Purpose: {purpose}
        
        Facts to include:
        {json.dumps(facts, indent=2)}
        
        Format as a proper legal affidavit with:
        1. Header and affiant information
        2. Numbered statements of fact
        3. Jurat (notary section)
        4. Signature blocks"""
        
        response = await self.chat_model.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "affidavit": response.content,
            "metadata": {
                "affiant": affiant,
                "purpose": purpose,
                "fact_count": len(facts),
                "created_date": datetime.now().isoformat()
            }
        }
    
    async def _compile_evidence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compile evidence for a specific claim or purpose"""
        claim = params.get("claim")
        evidence_types = params.get("evidence_types", [])
        
        # Search for relevant evidence
        docs = self.search_documents(claim, k=30)
        
        prompt = f"""Compile evidence to support: {claim}
        
        Required evidence types: {', '.join(evidence_types)}
        
        For each piece of evidence, provide:
        1. Document name and location
        2. Relevant excerpt
        3. How it supports the claim
        4. Strength of evidence (strong/moderate/weak)
        5. Any gaps or additional evidence needed"""
        
        response = await self.chat_model.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "evidence_compilation": response.content,
            "documents_reviewed": len(docs),
            "source_files": list(set([doc.metadata["file_name"] for doc in docs]))
        }
    
    async def _calculate_penalties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate tax penalties and interest"""
        tax_year = params.get("tax_year")
        amount_owed = params.get("amount_owed")
        payment_date = params.get("payment_date")
        
        prompt = f"""Calculate IRS penalties and interest for:
        Tax Year: {tax_year}
        Amount Owed: ${amount_owed}
        Payment Date: {payment_date}
        
        Include:
        1. Failure to file penalty (if applicable)
        2. Failure to pay penalty
        3. Interest calculations
        4. Total amount due
        5. Penalty abatement eligibility analysis"""
        
        response = await self.chat_model.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "penalty_calculation": response.content,
            "parameters": params
        }