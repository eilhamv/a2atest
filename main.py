#!/usr/bin/env python3
"""
Railway entry point - runs the email agent
"""
import sys
import os
import subprocess

# Change to email-agent directory and run
email_agent_dir = os.path.join(os.path.dirname(__file__), 'email-agent')
os.chdir(email_agent_dir)

# Run the email agent
subprocess.run([sys.executable, '__main__.py'])

# Made with Bob
