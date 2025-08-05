import streamlit as st
import asyncio
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
from typing import Dict, List, Any, Optional

from document_processor import DocumentProcessor
from claude_integration import ClaudeAnalyzer
from package_generator import PackageGenerator
from form_filler import FormFiller
from command_executor import CommandExecutor
from config import DOCUMENT_CATEGORIES, BASE_DIR

# Page configuration
st.set_page_config(
    page_title="ChittyTrace",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'processor' not in st.session_state:
    st.session_state.processor = DocumentProcessor()
if 'package_generator' not in st.session_state:
    st.session_state.package_generator = None
if 'form_filler' not in st.session_state:
    st.session_state.form_filler = None
if 'command_executor' not in st.session_state:
    st.session_state.command_executor = None
if 'indexed' not in st.session_state:
    st.session_state.indexed = False

# Sidebar
with st.sidebar:
    st.title("🔍 ChittyTrace")
    
    # API Key setup
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        help="Enter your Anthropic API key to enable Claude integration"
    )
    
    if api_key and not st.session_state.analyzer:
        try:
            st.session_state.analyzer = ClaudeAnalyzer(api_key)
            st.session_state.package_generator = PackageGenerator(st.session_state.analyzer)
            st.session_state.form_filler = FormFiller(st.session_state.analyzer)
            st.session_state.command_executor = CommandExecutor(st.session_state.analyzer)
            st.success("✅ Claude integration initialized")
        except Exception as e:
            st.error(f"Failed to initialize Claude: {e}")
    
    st.divider()
    
    # Document scanning
    if st.button("🔍 Scan Documents", type="primary", use_container_width=True):
        with st.spinner("Scanning documents..."):
            st.session_state.documents = st.session_state.processor.scan_documents()
            st.success(f"Found {len(st.session_state.documents)} documents")
    
    # Index documents
    if st.session_state.documents and st.session_state.analyzer:
        if st.button("📇 Index Documents", use_container_width=True):
            with st.spinner("Indexing documents for search..."):
                st.session_state.analyzer.index_documents(st.session_state.documents)
                st.session_state.indexed = True
                st.success("Documents indexed successfully")
    
    # Document statistics
    if st.session_state.documents:
        st.divider()
        st.subheader("📊 Document Statistics")
        
        df = pd.DataFrame(st.session_state.documents)
        
        # Category breakdown
        category_counts = df['category'].value_counts()
        st.metric("Total Documents", len(df))
        
        for category, count in category_counts.items():
            st.metric(category.replace('_', ' ').title(), count)

# Main content area
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Query & Analysis",
    "📦 Package Creator",
    "📝 Form Filler",
    "⚡ Command Executor",
    "📊 Visualizations",
    "📁 Document Browser"
])

# Tab 1: Query & Analysis
with tab1:
    st.header("Intelligent Document Analysis")
    
    if not st.session_state.analyzer:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to enable analysis")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_area(
                "Enter your query",
                placeholder="e.g., Trace all funds from USAA account to Colombia property purchase",
                height=100
            )
        
        with col2:
            st.write("")
            st.write("")
            search_k = st.number_input("Documents to search", min_value=1, max_value=50, value=10)
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if query and st.session_state.indexed:
                with st.spinner("Analyzing..."):
                    # Search for relevant documents
                    relevant_docs = st.session_state.analyzer.search_documents(query, k=search_k)
                    
                    # Get analysis
                    response = asyncio.run(
                        st.session_state.analyzer.analyze_with_context(query, relevant_docs)
                    )
                    
                    # Display results
                    st.subheader("Analysis Results")
                    st.write(response)
                    
                    # Show source documents
                    with st.expander("📄 Source Documents"):
                        for doc in relevant_docs[:5]:
                            st.write(f"**{doc.metadata['file_name']}**")
                            st.text(doc.page_content[:300] + "...")
                            st.divider()
            elif not st.session_state.indexed:
                st.error("Please index documents first using the sidebar button")

# Tab 2: Package Creator
with tab2:
    st.header("Document Package Generator")
    
    if not st.session_state.package_generator:
        st.warning("⚠️ Please initialize Claude integration first")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            package_type = st.selectbox(
                "Package Type",
                ["IRS Penalty Abatement", "Property Purchase Documentation", 
                 "Fund Flow Evidence", "Litigation Support", "Tax Filing Package",
                 "Corporate Formation", "Wire Transfer Documentation"]
            )
            
            recipient = st.text_input("Recipient/Purpose")
        
        with col2:
            deadline = st.date_input("Deadline", value=None)
            priority_items = st.multiselect(
                "Priority Items",
                ["Bank Statements", "Wire Transfers", "Property Documents",
                 "Tax Returns", "Corporate Documents", "Supporting Evidence"]
            )
        
        requirements = st.text_area(
            "Additional Requirements",
            placeholder="Specify any special requirements or instructions..."
        )
        
        if st.button("📦 Generate Package", type="primary"):
            with st.spinner("Generating package..."):
                package_data = {
                    "type": package_type,
                    "recipient": recipient,
                    "deadline": str(deadline) if deadline else None,
                    "priority_items": priority_items,
                    "requirements": requirements
                }
                
                result = asyncio.run(
                    st.session_state.analyzer.generate_package(package_type, package_data)
                )
                
                st.subheader("Generated Package")
                
                if isinstance(result, dict) and "raw_response" not in result:
                    # Display structured package
                    if "executive_summary" in result:
                        st.subheader("Executive Summary")
                        st.write(result["executive_summary"])
                    
                    if "required_documents" in result:
                        st.subheader("Required Documents")
                        for doc in result["required_documents"]:
                            st.checkbox(doc, key=f"doc_{doc}")
                    
                    if "instructions" in result:
                        st.subheader("Compilation Instructions")
                        st.write(result["instructions"])
                    
                    # Download button
                    package_json = json.dumps(result, indent=2)
                    st.download_button(
                        "📥 Download Package Specification",
                        package_json,
                        f"{package_type.lower().replace(' ', '_')}_package.json",
                        "application/json"
                    )
                else:
                    st.write(result.get("raw_response", result))

# Tab 3: Form Filler
with tab3:
    st.header("Automated Form Filling")
    
    if not st.session_state.form_filler:
        st.warning("⚠️ Please initialize Claude integration first")
    else:
        # Form template input
        form_template = st.text_area(
            "Form Template",
            placeholder="""Enter form template with placeholders, e.g.:
            
AFFIDAVIT OF [FULL_NAME]

I, [FULL_NAME], residing at [ADDRESS], hereby declare under penalty of perjury:

1. On [DATE], I transferred $[AMOUNT] from [SOURCE_ACCOUNT] to [DESTINATION_ACCOUNT]
2. The purpose of this transfer was [PURPOSE]
3. All funds were legally obtained through [SOURCE_OF_FUNDS]

Signed: ________________
Date: [SIGNATURE_DATE]""",
            height=300
        )
        
        # Data input
        st.subheader("Form Data")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name")
            address = st.text_area("Address", height=80)
            date = st.date_input("Transaction Date")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        
        with col2:
            source_account = st.text_input("Source Account")
            destination_account = st.text_input("Destination Account")
            purpose = st.text_input("Purpose")
            source_of_funds = st.text_input("Source of Funds")
        
        if st.button("📝 Fill Form", type="primary"):
            form_data = {
                "FULL_NAME": full_name,
                "ADDRESS": address,
                "DATE": str(date),
                "AMOUNT": f"{amount:,.2f}",
                "SOURCE_ACCOUNT": source_account,
                "DESTINATION_ACCOUNT": destination_account,
                "PURPOSE": purpose,
                "SOURCE_OF_FUNDS": source_of_funds,
                "SIGNATURE_DATE": datetime.now().strftime("%B %d, %Y")
            }
            
            with st.spinner("Filling form..."):
                filled_form = asyncio.run(
                    st.session_state.analyzer.fill_form(form_template, form_data)
                )
                
                st.subheader("Completed Form")
                st.text_area("", filled_form, height=400)
                
                # Download button
                st.download_button(
                    "📥 Download Filled Form",
                    filled_form,
                    f"filled_form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "text/plain"
                )

# Tab 4: Command Executor
with tab4:
    st.header("Command Execution Center")
    
    if not st.session_state.command_executor:
        st.warning("⚠️ Please initialize Claude integration first")
    else:
        command = st.selectbox(
            "Select Command",
            ["trace_funds", "generate_timeline", "analyze_transactions",
             "create_affidavit", "compile_evidence", "calculate_penalties"]
        )
        
        st.subheader("Command Parameters")
        
        if command == "trace_funds":
            col1, col2 = st.columns(2)
            with col1:
                source = st.text_input("Source Account")
                destination = st.text_input("Destination")
            with col2:
                start_date = st.date_input("Start Date", value=None)
                end_date = st.date_input("End Date", value=None)
            
            params = {
                "source_account": source,
                "destination": destination,
                "date_range": {
                    "start": str(start_date) if start_date else None,
                    "end": str(end_date) if end_date else None
                }
            }
        
        elif command == "generate_timeline":
            topic = st.text_input("Timeline Topic", value="all events")
            params = {"topic": topic}
        
        elif command == "analyze_transactions":
            account = st.text_input("Account to Analyze")
            min_amount = st.number_input("Minimum Amount", value=0.0)
            transaction_type = st.selectbox("Transaction Type", ["All", "Deposits", "Withdrawals"])
            
            params = {
                "account": account,
                "criteria": {
                    "min_amount": min_amount,
                    "type": transaction_type
                }
            }
        
        elif command == "create_affidavit":
            affiant = st.text_input("Affiant Name")
            purpose = st.text_input("Purpose")
            facts = st.text_area("Facts (one per line)").split('\n')
            
            params = {
                "affiant": affiant,
                "purpose": purpose,
                "facts": [f.strip() for f in facts if f.strip()]
            }
        
        elif command == "compile_evidence":
            claim = st.text_area("Claim to Support")
            evidence_types = st.multiselect(
                "Evidence Types",
                ["Bank Statements", "Wire Transfers", "Contracts", 
                 "Communications", "Tax Documents", "Corporate Records"]
            )
            
            params = {
                "claim": claim,
                "evidence_types": evidence_types
            }
        
        elif command == "calculate_penalties":
            col1, col2 = st.columns(2)
            with col1:
                tax_year = st.number_input("Tax Year", min_value=2000, max_value=2024, value=2023)
                amount_owed = st.number_input("Amount Owed", min_value=0.0)
            with col2:
                payment_date = st.date_input("Payment Date")
            
            params = {
                "tax_year": tax_year,
                "amount_owed": amount_owed,
                "payment_date": str(payment_date)
            }
        
        if st.button(f"⚡ Execute {command.replace('_', ' ').title()}", type="primary"):
            with st.spinner(f"Executing {command}..."):
                result = asyncio.run(
                    st.session_state.analyzer.execute_analysis_command(command, params)
                )
                
                st.subheader("Execution Results")
                
                if isinstance(result, dict):
                    for key, value in result.items():
                        if key == "source_documents":
                            with st.expander("📄 Source Documents"):
                                for doc in value:
                                    st.write(f"• {doc}")
                        else:
                            st.subheader(key.replace('_', ' ').title())
                            if isinstance(value, (list, dict)):
                                st.json(value)
                            else:
                                st.write(value)
                else:
                    st.write(result)

# Tab 5: Visualizations
with tab5:
    st.header("Data Visualizations")
    
    if st.session_state.documents:
        df = pd.DataFrame(st.session_state.documents)
        
        # Document distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Documents by Category")
            category_counts = df['category'].value_counts()
            fig_pie = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Document Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Documents by Type")
            type_counts = df['file_type'].value_counts()
            fig_bar = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="File Type Distribution",
                labels={'x': 'File Type', 'y': 'Count'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Timeline visualization
        st.subheader("Document Timeline")
        df['modified_date'] = pd.to_datetime(df['modified_time']).dt.date
        timeline_data = df.groupby(['modified_date', 'category']).size().reset_index(name='count')
        
        fig_timeline = px.scatter(
            timeline_data,
            x='modified_date',
            y='category',
            size='count',
            title="Document Activity Timeline",
            labels={'modified_date': 'Date', 'category': 'Category'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # File size distribution
        st.subheader("File Size Analysis")
        df['size_mb'] = df['file_size'] / (1024 * 1024)
        fig_box = px.box(
            df,
            x='category',
            y='size_mb',
            title="File Size Distribution by Category",
            labels={'size_mb': 'Size (MB)', 'category': 'Category'}
        )
        fig_box.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("📊 Scan documents first to see visualizations")

# Tab 6: Document Browser
with tab6:
    st.header("Document Browser")
    
    if st.session_state.documents:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + list(DOCUMENT_CATEGORIES.keys())
            )
        
        with col2:
            selected_type = st.selectbox(
                "Filter by File Type",
                ["All"] + list(set(doc['file_type'] for doc in st.session_state.documents))
            )
        
        with col3:
            search_term = st.text_input("Search in filename")
        
        # Filter documents
        filtered_docs = st.session_state.documents
        
        if selected_category != "All":
            filtered_docs = [d for d in filtered_docs if d['category'] == selected_category]
        
        if selected_type != "All":
            filtered_docs = [d for d in filtered_docs if d['file_type'] == selected_type]
        
        if search_term:
            filtered_docs = [d for d in filtered_docs if search_term.lower() in d['file_name'].lower()]
        
        # Display documents
        st.write(f"Showing {len(filtered_docs)} of {len(st.session_state.documents)} documents")
        
        for doc in filtered_docs[:50]:  # Limit display
            with st.expander(f"📄 {doc['file_name']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Path:** {doc['relative_path']}")
                    st.write(f"**Category:** {doc['category']}")
                    st.write(f"**Modified:** {doc['modified_time']}")
                    st.write(f"**Size:** {doc['file_size'] / 1024:.1f} KB")
                
                with col2:
                    if st.button("View Content", key=f"view_{doc['file_name']}"):
                        st.text_area(
                            "Content Preview",
                            doc['content'][:2000] + "..." if len(doc['content']) > 2000 else doc['content'],
                            height=300
                        )
    else:
        st.info("📁 Scan documents first to browse them")