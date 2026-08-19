"""
Main entry point for A.U.R.A. Assist (Adaptive Underworld Recon Array).
Angel Cartel EVE Online Tactical AI Assistant.
"""
import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Ensure local directory is at top of import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import run_app

if __name__ == "__main__":
    run_app()
