
import streamlit as st
import logging
import sys
import traceback
from typing import Any, Dict

logger = logging.getLogger(__name__)

def debug_info(message: str, data: Any = None):
    """Log debug information"""
    if st.session_state.get('debug_mode', False):
        logger.debug(f"{message}: {data}" if data else message)
        if data:
            st.sidebar.text(f"DEBUG: {message}")
            with st.sidebar.expander("Debug Data"):
                st.json(data if isinstance(data, dict) else str(data))

def handle_error(func):
    """Decorator to handle errors with debugging"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if st.session_state.get('debug_mode', False):
                st.error(error_msg)
                st.text("Full traceback:")
                st.code(traceback.format_exc())
            else:
                st.error(f"An error occurred: {str(e)}")
            
            return None
    return wrapper

def check_dependencies():
    """Check if all required modules are available"""
    required_modules = [
        'streamlit', 'pandas', 'plotly', 'asyncio',
        'pathlib', 'json', 'os', 'datetime'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        st.error(f"Missing required modules: {', '.join(missing)}")
        return False
    
    return True

def system_info():
    """Display system information for debugging"""
    if st.session_state.get('debug_mode', False):
        with st.sidebar.expander("System Info"):
            st.text(f"Python version: {sys.version}")
            st.text(f"Streamlit version: {st.__version__}")
            try:
                import pandas as pd
                st.text(f"Pandas version: {pd.__version__}")
            except:
                st.text("Pandas: Not available")
            
            # Additional debug info
            st.text(f"Working directory: {os.getcwd()}")
            st.text(f"Session state keys: {list(st.session_state.keys())}")
            
            # Check module imports
            modules_status = {}
            required_modules = [
                'document_processor', 'claude_integration', 
                'package_generator', 'form_filler', 'command_executor'
            ]
            
            for module in required_modules:
                try:
                    __import__(module)
                    modules_status[module] = "✅ Loaded"
                except ImportError as e:
                    modules_status[module] = f"❌ Error: {str(e)}"
            
            st.json(modules_status)

def debug_session_state():
    """Show detailed session state information"""
    if st.session_state.get('debug_mode', False):
        with st.sidebar.expander("Session State Debug"):
            state_info = {}
            for key, value in st.session_state.items():
                if key == 'documents':
                    state_info[key] = f"List with {len(value)} items"
                elif hasattr(value, '__class__'):
                    state_info[key] = f"{value.__class__.__name__} object"
                else:
                    state_info[key] = str(value)[:100]
            st.json(state_info)

def check_file_permissions():
    """Check file system permissions"""
    if st.session_state.get('debug_mode', False):
        with st.sidebar.expander("File System Check"):
            import os
            cwd = os.getcwd()
            st.text(f"Current directory: {cwd}")
            st.text(f"Can read: {os.access(cwd, os.R_OK)}")
            st.text(f"Can write: {os.access(cwd, os.W_OK)}")
            
            # Check if key directories exist
            dirs_to_check = ['logs', '.cache', 'chroma_db']
            for dir_name in dirs_to_check:
                dir_path = os.path.join(cwd, dir_name)
                exists = os.path.exists(dir_path)
                st.text(f"{dir_name}: {'Exists' if exists else 'Missing'}")

def test_claude_connection():
    """Test Claude API connection"""
    if st.session_state.get('debug_mode', False) and st.session_state.get('analyzer'):
        with st.sidebar.expander("Claude Connection Test"):
            if st.button("Test Claude API"):
                try:
                    # Simple test query
                    import asyncio
                    result = asyncio.run(
                        st.session_state.analyzer.client.messages.create(
                            model="claude-3-sonnet-20240229",
                            max_tokens=50,
                            messages=[{"role": "user", "content": "Hello, respond with 'API working'"}]
                        )
                    )
                    st.success("✅ Claude API connection successful")
                    st.text(f"Response: {result.content[0].text}")
                except Exception as e:
                    st.error(f"❌ Claude API error: {str(e)}")
