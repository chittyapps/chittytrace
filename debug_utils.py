
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
