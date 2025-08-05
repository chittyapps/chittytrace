import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

from claude_integration import ClaudeAnalyzer


class InteractiveTimeline:
    def __init__(self, analyzer: ClaudeAnalyzer):
        self.analyzer = analyzer
        
    def create_timeline(self, events: List[Dict[str, Any]], documents: List[Dict[str, Any]]) -> go.Figure:
        """Create interactive timeline with document links"""
        
        # Prepare event data
        df_events = pd.DataFrame(events)
        if 'date' in df_events.columns:
            df_events['date'] = pd.to_datetime(df_events['date'])
            df_events = df_events.sort_values('date')
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=("Flow of Funds Timeline", "Document Activity")
        )
        
        # Define color scheme for different event types
        color_map = {
            'wire_transfer': '#1f77b4',
            'property_purchase': '#ff7f0e',
            'bank_transaction': '#2ca02c',
            'legal_filing': '#d62728',
            'tax_event': '#9467bd',
            'corporate_event': '#8c564b',
            'other': '#7f7f7f'
        }
        
        # Add events to timeline
        for event_type, color in color_map.items():
            type_events = df_events[df_events['type'] == event_type]
            if not type_events.empty:
                # Main timeline trace
                fig.add_trace(
                    go.Scatter(
                        x=type_events['date'],
                        y=type_events['amount'] if 'amount' in type_events.columns else [1] * len(type_events),
                        mode='markers+text',
                        name=event_type.replace('_', ' ').title(),
                        marker=dict(
                            size=15,
                            color=color,
                            symbol='circle',
                            line=dict(width=2, color='white')
                        ),
                        text=type_events['description'] if 'description' in type_events.columns else '',
                        textposition='top center',
                        hovertemplate='<b>%{text}</b><br>' +
                                     'Date: %{x}<br>' +
                                     'Amount: $%{y:,.2f}<br>' +
                                     '<extra></extra>',
                        customdata=type_events.to_dict('records')
                    ),
                    row=1, col=1
                )
        
        # Add document activity heatmap
        if documents:
            doc_df = pd.DataFrame(documents)
            doc_df['date'] = pd.to_datetime(doc_df['modified_time']).dt.date
            doc_activity = doc_df.groupby(['date', 'category']).size().reset_index(name='count')
            
            # Create heatmap data
            categories = doc_activity['category'].unique()
            dates = pd.date_range(doc_activity['date'].min(), doc_activity['date'].max(), freq='D')
            
            heatmap_data = []
            for category in categories:
                cat_data = doc_activity[doc_activity['category'] == category]
                counts = []
                for date in dates:
                    count = cat_data[cat_data['date'] == date.date()]['count'].sum()
                    counts.append(count if count > 0 else 0)
                heatmap_data.append(counts)
            
            fig.add_trace(
                go.Heatmap(
                    z=heatmap_data,
                    x=dates,
                    y=categories,
                    colorscale='Blues',
                    showscale=True,
                    hovertemplate='Category: %{y}<br>Date: %{x}<br>Documents: %{z}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_xaxes(
            title_text="Date",
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            row=2, col=1
        )
        
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="Category", row=2, col=1)
        
        fig.update_layout(
            height=800,
            title_text="Interactive Flow of Funds Timeline",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    async def extract_timeline_events(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract timeline events from documents using Claude"""
        
        prompt = """Analyze these documents and extract key timeline events including:
        - Wire transfers (with amounts, dates, source, destination)
        - Property purchases
        - Bank transactions over $10,000
        - Legal filings
        - Tax events
        - Corporate events
        
        Return as JSON array with fields: date, type, description, amount (if applicable), 
        source_account, destination_account, supporting_documents"""
        
        # Batch process documents
        events = []
        for doc in documents:
            if doc.get('content'):
                doc_prompt = f"{prompt}\n\nDocument: {doc['file_name']}\nContent: {doc['content'][:2000]}"
                response = await self.analyzer.chat_model.ainvoke([
                    {"role": "user", "content": doc_prompt}
                ])
                
                try:
                    doc_events = json.loads(response.content)
                    for event in doc_events:
                        event['source_document'] = doc['file_name']
                        event['document_path'] = doc['file_path']
                        events.append(event)
                except:
                    pass
        
        return events
    
    def render_timeline_sidebar(self, events: List[Dict[str, Any]], documents: List[Dict[str, Any]]):
        """Render timeline sidebar with event details and document links"""
        
        st.sidebar.subheader("Timeline Events")
        
        # Event filters
        event_types = list(set(e.get('type', 'other') for e in events))
        selected_types = st.sidebar.multiselect("Event Types", event_types, default=event_types)
        
        # Date range filter
        if events:
            dates = [pd.to_datetime(e.get('date')) for e in events if e.get('date')]
            if dates:
                min_date = min(dates).date()
                max_date = max(dates).date()
                date_range = st.sidebar.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
        
        # Display filtered events
        filtered_events = [
            e for e in events 
            if e.get('type', 'other') in selected_types
        ]
        
        st.sidebar.write(f"Showing {len(filtered_events)} events")
        
        for event in filtered_events[:20]:  # Limit display
            with st.sidebar.expander(f"{event.get('date', 'N/A')} - {event.get('type', 'Unknown')}"):
                st.write(f"**Description:** {event.get('description', 'N/A')}")
                if event.get('amount'):
                    st.write(f"**Amount:** ${event['amount']:,.2f}")
                if event.get('source_document'):
                    st.write(f"**Source:** {event['source_document']}")
                    if st.button(f"View Document", key=f"view_{event.get('id', '')}"):
                        return event.get('document_path')
        
        return None