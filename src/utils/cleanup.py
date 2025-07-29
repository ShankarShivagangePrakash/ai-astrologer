"""
Streamlit Session Cleanup Utility
Automatically cleans up temporary files when users navigate between pages
"""

import streamlit as st
import os
import glob
import atexit
import tempfile
from pathlib import Path

class StreamlitFileCleanup:
    def __init__(self):
        """Initialize cleanup utility"""
        self.temp_files = []
        self.session_id = self.get_session_id()
        
    def get_session_id(self):
        """Get or create a unique session ID"""
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())[:8]
        return st.session_state.session_id
    
    def register_temp_file(self, filepath):
        """Register a temporary file for cleanup"""
        if 'temp_files' not in st.session_state:
            st.session_state.temp_files = []
        st.session_state.temp_files.append(filepath)
        
    def cleanup_temp_files(self):
        """Clean up all registered temporary files"""
        if 'temp_files' in st.session_state:
            for filepath in st.session_state.temp_files:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    pass
            st.session_state.temp_files = []
    
    def cleanup_old_charts(self, pattern="*vedicHoroscope*.png"):
        """Clean up old chart files"""
        try:
            chart_files = glob.glob(pattern)
            for file in chart_files:
                try:
                    os.remove(file)
                except:
                    pass
        except Exception as e:
            pass

# Global cleanup instance
cleanup_manager = StreamlitFileCleanup()

# Register cleanup on exit
@atexit.register
def cleanup_on_exit():
    cleanup_manager.cleanup_temp_files()
    cleanup_manager.cleanup_old_charts()

def auto_cleanup():
    """Call this at the start of each Streamlit page"""
    cleanup_manager.cleanup_temp_files()
    cleanup_manager.cleanup_old_charts()

def register_for_cleanup(filepath):
    """Register a file for automatic cleanup"""
    cleanup_manager.register_temp_file(filepath)
