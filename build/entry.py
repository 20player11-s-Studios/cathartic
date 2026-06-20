#!/usr/bin/env python3
"""Cathartic entry point for PyInstaller bundle."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cathartic.menu import main
main()
