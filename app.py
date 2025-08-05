import streamlit as st
import asyncio
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
import logging
import traceback
from typing import Dict, List, Any, Optional

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from document_processor import DocumentProcessor
    from claude_integration import ClaudeAnalyzer
    from package_generator import PackageGenerator
    from form_filler import FormFiller
    from command_executor import CommandExecutor
    from config import DOCUMENT_CATEGORIES, BASE_DIR
    logger.info("All modules imported successfully")
except ImportError as e:
    logger.error(f"Import error: {e}")
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="ChittyTrace",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved styling
st.markdown("""
<style>
    .custom-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #4b6cb7 0%, #18284a 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .custom-header h1 {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .tagline {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        letter-spacing: 0.5px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f0f4f8 0%, #d9e2ec 100%);
    }
    .sidebar .sidebar-content .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .sidebar .sidebar-content .stButton>button {
        width: 100%;
        height: 45px;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .sidebar .sidebar-content .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .sidebar .sidebar-content .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .feature-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid #e0e0e0;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    .feature-card .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #4CAF50; /* Default icon color, can be themed */
    }
    .metric-card, .status-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid;
    }
    .metric-card h4, .status-card h4 {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-card p, .status-card p {
        color: #555;
        font-size: 0.95rem;
    }
    .stTabs .stTabs-tabs .stTabs-tab {
        font-weight: 500;
        color: var(--text-secondary);
    }
    .stTabs .stTabs-tabs .stTabs-tab:hover {
        color: var(--primary-color);
    }
    .stTabs .stTabs-tabs .stTabs-tab--selected {
        color: var(--primary-color);
        font-weight: 700;
        border-bottom: 2px solid var(--primary-color);
    }
    .badge {
        display: inline-block;
        padding: 0.4em 0.75em;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.35rem;
        margin: 0.2rem;
        color: #fff;
    }
    .badge-info { background-color: #17a2b8; }
    .badge-success { background-color: #28a745; }
    .badge-warning { background-color: #ffc107; color: #212529; }

    /* Specific overrides for Streamlit elements */
    .stButton>button[data-testid="primaryButton"] {
        background-color: #007bff; /* Primary blue */
        border-color: #007bff;
        color: white;
    }
    .stButton>button[data-testid="primaryButton"]:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .stTextArea>div>textarea {
        border-radius: 8px;
    }
    .stNumberInput>div>div>input {
        border-radius: 8px;
    }
    .stSelectbox>div>div {
        border-radius: 8px;
    }
    .stDateInput>div>div>input {
        border-radius: 8px;
    }
    .stFileUploader>div>section>div>input {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with error handling
try:
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'processor' not in st.session_state:
        st.session_state.processor = DocumentProcessor()
        logger.info("DocumentProcessor initialized")
    if 'package_generator' not in st.session_state:
        st.session_state.package_generator = None
    if 'form_filler' not in st.session_state:
        st.session_state.form_filler = None
    if 'command_executor' not in st.session_state:
        st.session_state.command_executor = None
    if 'indexed' not in st.session_state:
        st.session_state.indexed = False
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
except Exception as e:
    logger.error(f"Error initializing session state: {e}")
    st.error(f"Initialization error: {e}")
    st.stop()

# Sidebar with improved styling
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">🏛️ Control Panel</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">ChittyTrace Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # API Key input with better styling
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        help="Enter your Anthropic API key for Claude integration",
        placeholder="sk-ant-..."
    )

    if api_key and not st.session_state.analyzer:
        try:
            st.session_state.analyzer = ClaudeAnalyzer(api_key)
            st.session_state.package_generator = PackageGenerator(st.session_state.analyzer)
            st.session_state.form_filler = FormFiller(st.session_state.analyzer)
            st.session_state.command_executor = CommandExecutor(st.session_state.analyzer)
            st.success("✅ Claude integration initialized")
            logger.info("Claude integration initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude: {e}")
            st.error(f"Failed to initialize Claude: {e}")
            st.text(f"Full error: {traceback.format_exc()}")

    # Debug mode toggle
    st.session_state.debug_mode = st.checkbox("🐛 Debug Mode", value=st.session_state.debug_mode)
    
    if st.session_state.debug_mode:
        st.info("Debug mode enabled - Check console for detailed logs")
        st.json({
            "Documents loaded": len(st.session_state.documents),
            "Analyzer initialized": st.session_state.analyzer is not None,
            "Indexed": st.session_state.indexed,
            "Session state keys": list(st.session_state.keys())
        })

    st.divider()

    # Document upload and scanning with improved styling
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📁</div>
        <h3 style="text-align: center; color: var(--text-primary); margin-bottom: 1rem;">Document Management</h3>
    </div>
    """, unsafe_allow_html=True)

    # File uploader with enhanced styling
    uploaded_files = st.file_uploader(
        "📤 Upload Documents",
        accept_multiple_files=True,
        type=['pdf', 'xlsx', 'xls', 'csv', 'txt', 'docx', 'doc', 'eml', 'msg', 'zip', 'tar', 'gz'],
        help="Drag & drop or browse to upload financial documents, statements, legal files, emails, or archives"
    )

    if uploaded_files:
        with st.spinner("Processing uploaded files..."):
            st.session_state.documents.extend(st.session_state.processor.process_uploaded_files(uploaded_files))
            st.success(f"Added {len(uploaded_files)} files to the session.")

    # Scan Directory Button
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🗂️</div>
        <h3 style="text-align: center; color: var(--text-primary); margin-bottom: 1rem;">Directory Scanner</h3>
    </div>
    """, unsafe_allow_html=True)

    scan_directory = st.text_input(
        "📂 Directory Path",
        placeholder="/path/to/documents",
        help="Enter path to recursively scan for documents"
    )

    if st.button("Scan Directory", type="secondary", use_container_width=True):
        if scan_directory:
            with st.spinner(f"Scanning directory: {scan_directory}..."):
                try:
                    found_docs = st.session_state.processor.scan_directory(scan_directory)
                    st.session_state.documents.extend(found_docs)
                    st.success(f"Found and added {len(found_docs)} documents from {scan_directory}.")
                except Exception as e:
                    st.error(f"Error scanning directory: {e}")
        else:
            st.warning("Please provide a directory path to scan.")

    st.divider()

    # Document scanning button
    if st.button("🔍 Scan All Documents", type="primary", use_container_width=True):
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
    
    # Status display with improved metrics
    if st.session_state.documents:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: var(--success-color); margin-bottom: 0.5rem;">✅ Document Status</h4>
            <p style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);">{} documents indexed</p>
        </div>
        """.format(len(st.session_state.documents)), unsafe_allow_html=True)

        # Document statistics with badges
        categories = {}
        for doc in st.session_state.documents:
            cat = doc.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        if categories:
            st.markdown("**📊 Document Categories:**")
            badge_html = ""
            for category, count in categories.items():
                badge_html += f'<span class="badge badge-info">{category.title()}: {count}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card" style="border-left: 4px solid var(--warning-color);">
            <h4 style="color: var(--warning-color); margin-bottom: 0.5rem;">📋 Getting Started</h4>
            <p style="color: var(--text-secondary);">Upload documents or scan a directory to begin analysis</p>
        </div>
        """, unsafe_allow_html=True)


# Main content area with improved tab styling
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Query & Analysis",
    "📦 Package Creator", 
    "📝 Form Filler",
    "⚡ Command Executor",
    "📊 Visualizations",
    "🗄️ Document Browser"
])

# Custom header with improved styling
st.markdown("""
<div class="custom-header">
    <h1>🔍 ChittyTrace</h1>
    <p class="tagline">AI-Powered Financial Forensics & Court Exhibit Generation</p>
    <p class="tagline" style="font-size: 1rem; margin-top: 0;">Specialized for Cook County Circuit Court</p>
</div>
""", unsafe_allow_html=True)

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
            st.write("") # Spacer
            st.write("") # Spacer
            search_k = st.number_input("Documents to search", min_value=1, max_value=50, value=10)

        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if query and st.session_state.indexed:
                try:
                    with st.spinner("Analyzing..."):
                        logger.info(f"Starting analysis for query: {query}")
                        
                        # Search for relevant documents
                        relevant_docs = st.session_state.analyzer.search_documents(query, k=search_k)
                        logger.info(f"Found {len(relevant_docs)} relevant documents")

                        # Get analysis
                        response = asyncio.run(
                            st.session_state.analyzer.analyze_with_context(query, relevant_docs)
                        )
                        logger.info("Analysis completed successfully")

                        # Display results
                        st.subheader("Analysis Results")
                        st.write(response)

                        # Show source documents
                        with st.expander("📄 Source Documents"):
                            for doc in relevant_docs[:5]:
                                st.write(f"**{doc.metadata['file_name']}**")
                                st.text(doc.page_content[:300] + "...")
                                st.divider()
                                
                        if st.session_state.debug_mode:
                            with st.expander("🐛 Debug Info"):
                                st.json({
                                    "query": query,
                                    "search_k": search_k,
                                    "docs_found": len(relevant_docs),
                                    "response_length": len(str(response))
                                })
                                
                except Exception as e:
                    logger.error(f"Analysis failed: {e}")
                    logger.error(traceback.format_exc())
                    st.error(f"Analysis failed: {e}")
                    if st.session_state.debug_mode:
                        st.code(traceback.format_exc())
            elif not st.session_state.indexed:
                st.error("Please index documents first using the sidebar button")
            elif not query:
                st.warning("Please enter a query to analyze")

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