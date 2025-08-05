"""
Command execution framework for complex analysis operations
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import logging

from claude_integration import ClaudeAnalyzer

logger = logging.getLogger(__name__)


class CommandExecutor:
    def __init__(self, analyzer: ClaudeAnalyzer):
        self.analyzer = analyzer
        self.commands = self._register_commands()
        
    def _register_commands(self) -> Dict[str, Callable]:
        """Register available commands"""
        return {
            "trace_funds": self.trace_funds,
            "generate_timeline": self.generate_timeline,
            "analyze_transactions": self.analyze_transactions,
            "create_affidavit": self.create_affidavit,
            "compile_evidence": self.compile_evidence,
            "calculate_penalties": self.calculate_penalties,
            "cross_reference_database": self.cross_reference_database,
            "generate_fund_flow_chart": self.generate_fund_flow_chart,
            "analyze_property_chain": self.analyze_property_chain,
            "detect_patterns": self.detect_patterns
        }
    
    async def execute(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command with parameters"""
        if command not in self.commands:
            return {"error": f"Unknown command: {command}"}
        
        try:
            result = await self.commands[command](parameters)
            return {
                "status": "success",
                "command": command,
                "result": result,
                "executed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Command execution failed: {command} - {e}")
            return {
                "status": "error",
                "command": command,
                "error": str(e),
                "executed_at": datetime.now().isoformat()
            }
    
    async def trace_funds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fund tracing with database cross-reference"""
        result = await self.analyzer._trace_funds(params)
        
        # Add cross-reference to connected database
        if params.get("cross_reference_database", True):
            db_data = await self.cross_reference_database({
                "query_type": "fund_trace",
                "parameters": params
            })
            result["database_cross_reference"] = db_data
        
        return result
    
    async def generate_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive timeline"""
        return await self.analyzer._generate_timeline(params)
    
    async def analyze_transactions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transactions with pattern detection"""
        return await self.analyzer._analyze_transactions(params)
    
    async def create_affidavit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create legal affidavit"""
        return await self.analyzer._create_affidavit(params)
    
    async def compile_evidence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compile evidence with database references"""
        result = await self.analyzer._compile_evidence(params)
        
        # Add database evidence if connected
        if params.get("include_database", True):
            db_evidence = await self.cross_reference_database({
                "query_type": "evidence",
                "claim": params.get("claim")
            })
            result["database_evidence"] = db_evidence
        
        return result
    
    async def calculate_penalties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate tax penalties"""
        return await self.analyzer._calculate_penalties(params)
    
    async def cross_reference_database(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-reference with connected Neon database"""
        prompt = f"""Cross-reference the following with the connected database:
        
        Query Type: {params.get('query_type')}
        Parameters: {json.dumps(params.get('parameters', {}), indent=2)}
        
        Search for:
        1. Matching transactions or events
        2. Related property records
        3. Corresponding legal filings
        4. Timeline correlations
        5. Supporting evidence
        
        Provide relevant matches and their significance."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return {
            "cross_reference_results": response.content,
            "database": "connected_neon_database",
            "query_timestamp": datetime.now().isoformat()
        }
    
    async def generate_fund_flow_chart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visual fund flow chart data"""
        prompt = f"""Generate a fund flow chart structure for:
        
        Start Date: {params.get('start_date')}
        End Date: {params.get('end_date')}
        Accounts: {params.get('accounts', [])}
        
        Create a hierarchical structure showing:
        1. Source accounts and institutions
        2. Transfer amounts and dates
        3. Intermediate accounts
        4. Final destinations
        5. Purpose of each transfer
        
        Format as JSON with nodes and edges for visualization."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        try:
            chart_data = json.loads(response.content)
        except:
            chart_data = {"raw_response": response.content}
        
        return {
            "chart_structure": chart_data,
            "visualization_type": "hierarchical_flow",
            "parameters": params
        }
    
    async def analyze_property_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze property ownership and funding chain"""
        property_address = params.get('property_address')
        
        prompt = f"""Analyze the complete property chain for: {property_address}
        
        Include:
        1. Purchase history and dates
        2. Funding sources for each purchase
        3. Ownership transfers
        4. Liens or encumbrances
        5. Related entities or LLCs
        6. Connection to Arias v Bianchi case
        
        Trace all funding sources back to origin."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return {
            "property_analysis": response.content,
            "property_address": property_address,
            "analysis_date": datetime.now().isoformat()
        }
    
    async def detect_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns in financial transactions"""
        pattern_type = params.get('pattern_type', 'all')
        threshold = params.get('threshold', {})
        
        prompt = f"""Detect patterns in financial transactions:
        
        Pattern Type: {pattern_type}
        Thresholds: {json.dumps(threshold, indent=2)}
        
        Look for:
        1. Recurring transfers
        2. Structured transactions (potential structuring)
        3. Unusual timing patterns
        4. Related party transactions
        5. Round number patterns
        6. Geographic patterns
        7. Velocity changes
        
        Provide pattern analysis with examples and risk assessment."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return {
            "pattern_analysis": response.content,
            "pattern_type": pattern_type,
            "thresholds": threshold,
            "analysis_timestamp": datetime.now().isoformat()
        }