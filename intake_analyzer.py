import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from collections import defaultdict, Counter
import numpy as np

from claude_integration import ClaudeAnalyzer
from document_processor import DocumentProcessor


class IntakeAnalyzer:
    def __init__(self, analyzer: ClaudeAnalyzer):
        self.analyzer = analyzer
        self.fact_patterns = {
            'financial': r'\$[\d,]+\.?\d*|USD|EUR|GBP|payment|transfer|wire|deposit|withdrawal',
            'temporal': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|january|february|march|april|may|june|july|august|september|october|november|december|\d{4}',
            'entity': r'[A-Z][a-z]+\s+[A-Z][a-z]+|LLC|Inc|Corp|Ltd|Bank|Account',
            'location': r'[A-Z][a-z]+,?\s*[A-Z]{2}|Colombia|United States|USA|address|property',
            'legal': r'case\s*no|docket|plaintiff|defendant|court|judge|filing|motion|order',
            'communication': r'email|call|meeting|conversation|letter|memo|@[\w.]+',
        }
        
    async def analyze_intake(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive intake analysis of documents"""
        
        # Extract key facts and entities
        facts = await self.extract_facts(documents)
        entities = await self.extract_entities(documents)
        
        # Perform relationship analysis
        relationships = self.analyze_relationships(entities, facts)
        
        # Create fact groups
        fact_groups = self.group_facts(facts)
        
        # Generate summary statistics
        stats = self.generate_statistics(documents, facts, entities)
        
        # Create timeline data
        timeline_data = self.extract_timeline_data(facts)
        
        return {
            'facts': facts,
            'entities': entities,
            'relationships': relationships,
            'fact_groups': fact_groups,
            'statistics': stats,
            'timeline_data': timeline_data
        }
    
    async def extract_facts(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract key facts from documents using pattern matching and AI"""
        facts = []
        
        for doc in documents:
            content = doc.get('content', '')
            if not content:
                continue
                
            # Pattern-based fact extraction
            doc_facts = []
            
            # Financial facts
            financial_matches = re.findall(r'\$[\d,]+\.?\d*', content)
            for match in financial_matches:
                amount = float(match.replace('$', '').replace(',', ''))
                if amount > 100:  # Filter small amounts
                    doc_facts.append({
                        'type': 'financial',
                        'value': amount,
                        'text': match,
                        'category': 'transaction'
                    })
            
            # Date extraction
            date_patterns = [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
            ]
            
            for pattern in date_patterns:
                date_matches = re.findall(pattern, content, re.IGNORECASE)
                for match in date_matches:
                    doc_facts.append({
                        'type': 'temporal',
                        'value': match,
                        'category': 'date'
                    })
            
            # Add document metadata
            for fact in doc_facts:
                fact['source_document'] = doc['file_name']
                fact['document_path'] = doc['file_path']
                fact['confidence'] = 0.9
                facts.append(fact)
        
        # AI-based fact extraction for complex patterns
        if facts:
            enhanced_facts = await self.enhance_facts_with_ai(facts, documents)
            facts.extend(enhanced_facts)
        
        return facts
    
    async def extract_entities(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract entities (people, organizations, accounts) from documents"""
        entities = []
        entity_map = defaultdict(lambda: {'count': 0, 'documents': set(), 'contexts': []})
        
        for doc in documents:
            content = doc.get('content', '')
            if not content:
                continue
            
            # Person names (simple pattern)
            person_pattern = r'(?:[A-Z][a-z]+\s+){1,3}[A-Z][a-z]+'
            person_matches = re.findall(person_pattern, content)
            
            for match in person_matches:
                if len(match.split()) >= 2:  # At least first and last name
                    entity_map[match]['count'] += 1
                    entity_map[match]['documents'].add(doc['file_name'])
                    entity_map[match]['type'] = 'person'
            
            # Organizations
            org_patterns = [
                r'[\w\s]+(?:LLC|Inc|Corp|Ltd|Bank|Company|Group)',
                r'[A-Z]{3,}'  # Acronyms
            ]
            
            for pattern in org_patterns:
                org_matches = re.findall(pattern, content)
                for match in org_matches:
                    if len(match) > 3:
                        entity_map[match]['count'] += 1
                        entity_map[match]['documents'].add(doc['file_name'])
                        entity_map[match]['type'] = 'organization'
            
            # Account numbers
            account_pattern = r'(?:Account|Acct\.?)\s*(?:No\.?|#)?\s*:?\s*(\d{4,})'
            account_matches = re.findall(account_pattern, content, re.IGNORECASE)
            
            for match in account_matches:
                entity_map[f"Account {match}"]["count"] += 1
                entity_map[f"Account {match}"]["documents"].add(doc['file_name'])
                entity_map[f"Account {match}"]["type"] = 'account'
        
        # Convert to list format
        for name, data in entity_map.items():
            entities.append({
                'name': name,
                'type': data.get('type', 'unknown'),
                'count': data['count'],
                'documents': list(data['documents']),
                'importance_score': data['count'] * len(data['documents'])
            })
        
        return sorted(entities, key=lambda x: x['importance_score'], reverse=True)
    
    def analyze_relationships(self, entities: List[Dict[str, Any]], facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze relationships between entities based on co-occurrence"""
        relationships = []
        
        # Build document-entity matrix
        doc_entity_map = defaultdict(set)
        for entity in entities:
            for doc in entity['documents']:
                doc_entity_map[doc].add(entity['name'])
        
        # Find co-occurrences
        entity_pairs = defaultdict(int)
        for doc, doc_entities in doc_entity_map.items():
            entity_list = list(doc_entities)
            for i in range(len(entity_list)):
                for j in range(i + 1, len(entity_list)):
                    pair = tuple(sorted([entity_list[i], entity_list[j]]))
                    entity_pairs[pair] += 1
        
        # Create relationship records
        for (entity1, entity2), count in entity_pairs.items():
            if count > 1:  # Only significant relationships
                relationships.append({
                    'source': entity1,
                    'target': entity2,
                    'weight': count,
                    'type': 'co-occurrence'
                })
        
        return relationships
    
    def group_facts(self, facts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group facts by type, theme, and relevance"""
        groups = defaultdict(list)
        
        # Group by type
        for fact in facts:
            groups[f"type_{fact['type']}"].append(fact)
        
        # Group by value ranges (for financial facts)
        financial_facts = [f for f in facts if f['type'] == 'financial']
        if financial_facts:
            # Define value ranges
            ranges = [
                (0, 1000, 'small_transactions'),
                (1000, 10000, 'medium_transactions'),
                (10000, 100000, 'large_transactions'),
                (100000, float('inf'), 'major_transactions')
            ]
            
            for fact in financial_facts:
                value = fact['value']
                for min_val, max_val, label in ranges:
                    if min_val <= value < max_val:
                        groups[label].append(fact)
                        break
        
        # Group by time periods (for temporal facts)
        temporal_facts = [f for f in facts if f['type'] == 'temporal']
        if temporal_facts:
            # Group by year/month
            year_groups = defaultdict(list)
            for fact in temporal_facts:
                try:
                    # Extract year from various date formats
                    year_match = re.search(r'20\d{2}', str(fact['value']))
                    if year_match:
                        year = year_match.group()
                        year_groups[f"year_{year}"].append(fact)
                except:
                    pass
            
            groups.update(year_groups)
        
        return dict(groups)
    
    def generate_statistics(self, documents: List[Dict[str, Any]], 
                          facts: List[Dict[str, Any]], 
                          entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive statistics about the intake"""
        
        # Document statistics
        doc_stats = {
            'total_documents': len(documents),
            'total_pages': sum(doc.get('page_count', 1) for doc in documents),
            'file_types': Counter(doc['file_type'] for doc in documents),
            'categories': Counter(doc['category'] for doc in documents),
            'date_range': self.get_date_range(documents)
        }
        
        # Fact statistics
        fact_stats = {
            'total_facts': len(facts),
            'facts_by_type': Counter(fact['type'] for fact in facts),
            'financial_summary': self.get_financial_summary(facts),
            'temporal_distribution': self.get_temporal_distribution(facts)
        }
        
        # Entity statistics
        entity_stats = {
            'total_entities': len(entities),
            'entities_by_type': Counter(entity['type'] for entity in entities),
            'top_entities': entities[:10],  # Already sorted by importance
            'entity_document_coverage': self.calculate_entity_coverage(entities, documents)
        }
        
        return {
            'documents': doc_stats,
            'facts': fact_stats,
            'entities': entity_stats
        }
    
    def get_financial_summary(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize financial facts"""
        financial_facts = [f for f in facts if f['type'] == 'financial']
        if not financial_facts:
            return {}
        
        values = [f['value'] for f in financial_facts]
        return {
            'total_amount': sum(values),
            'average_amount': np.mean(values),
            'median_amount': np.median(values),
            'max_amount': max(values),
            'min_amount': min(values),
            'transaction_count': len(values)
        }
    
    def get_temporal_distribution(self, facts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of temporal facts"""
        temporal_facts = [f for f in facts if f['type'] == 'temporal']
        year_counts = defaultdict(int)
        
        for fact in temporal_facts:
            year_match = re.search(r'20\d{2}', str(fact['value']))
            if year_match:
                year_counts[year_match.group()] += 1
        
        return dict(year_counts)
    
    def calculate_entity_coverage(self, entities: List[Dict[str, Any]], 
                                documents: List[Dict[str, Any]]) -> float:
        """Calculate what percentage of documents contain key entities"""
        if not documents or not entities:
            return 0.0
        
        # Get top 10 entities
        top_entities = entities[:10]
        covered_docs = set()
        
        for entity in top_entities:
            covered_docs.update(entity['documents'])
        
        return len(covered_docs) / len(documents)
    
    def get_date_range(self, documents: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Get the date range of documents"""
        dates = []
        for doc in documents:
            if 'modified_time' in doc:
                try:
                    dates.append(pd.to_datetime(doc['modified_time']))
                except:
                    pass
        
        if dates:
            return (min(dates).strftime('%Y-%m-%d'), max(dates).strftime('%Y-%m-%d'))
        return ('Unknown', 'Unknown')
    
    def extract_timeline_data(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract timeline data from facts for visualization"""
        timeline_events = []
        
        # Process financial facts with dates
        for fact in facts:
            if fact['type'] == 'financial':
                # Look for associated date in the same document
                doc_facts = [f for f in facts if f['source_document'] == fact['source_document']]
                date_facts = [f for f in doc_facts if f['type'] == 'temporal']
                
                if date_facts:
                    # Use the closest date fact
                    timeline_events.append({
                        'date': str(date_facts[0]['value']),
                        'amount': fact['value'],
                        'description': f"${fact['value']:,.2f} transaction",
                        'type': 'financial',
                        'source': fact['source_document']
                    })
        
        return timeline_events
    
    async def enhance_facts_with_ai(self, facts: List[Dict[str, Any]], 
                                   documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AI to extract more complex facts and relationships"""
        enhanced_facts = []
        
        # Sample documents for AI analysis
        sample_docs = documents[:5]  # Limit for performance
        
        prompt = """Analyze these documents and extract additional facts including:
        - Complex financial relationships (e.g., "X paid Y for Z")
        - Legal claims and allegations
        - Property transfers and ownership
        - Business relationships
        - Causation and timeline connections
        
        Return as JSON array with fields: type, description, entities_involved, date (if any), amount (if any)"""
        
        for doc in sample_docs:
            if doc.get('content'):
                doc_prompt = f"{prompt}\n\nDocument: {doc['file_name']}\nContent: {doc['content'][:1500]}"
                try:
                    response = await self.analyzer.chat_model.ainvoke([
                        {"role": "user", "content": doc_prompt}
                    ])
                    
                    ai_facts = json.loads(response.content)
                    for fact in ai_facts:
                        fact['source_document'] = doc['file_name']
                        fact['extraction_method'] = 'ai'
                        fact['confidence'] = 0.8
                        enhanced_facts.append(fact)
                except:
                    pass
        
        return enhanced_facts
    
    def create_relationship_graph(self, relationships: List[Dict[str, Any]]) -> go.Figure:
        """Create an interactive relationship graph"""
        G = nx.Graph()
        
        # Add edges with weights
        for rel in relationships:
            G.add_edge(rel['source'], rel['target'], weight=rel['weight'])
        
        # Calculate layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = G[edge[0]][edge[1]]['weight']
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=weight, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                size=20,
                color='#1f77b4',
                line=dict(color='white', width=2)
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        fig.update_layout(
            title="Entity Relationship Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        return fig