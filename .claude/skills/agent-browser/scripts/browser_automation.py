#!/usr/bin/env python3
"""
Common browser automation utilities for agent-browser workflows.
This module provides helper functions for common web automation tasks.
"""

import subprocess
import json
import time
import re
from typing import List, Dict, Optional, Any

class AgentBrowserHelper:
    """Helper class for agent-browser command execution."""
    
    def __init__(self, session: Optional[str] = None):
        """Initialize with optional session name."""
        self.session_prefix = f"--session {session}" if session else ""
    
    def run_command(self, command: str, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Execute agent-browser command and return result."""
        full_command = f"agent-browser {self.session_prefix} {command}".strip()
        print(f"Running: {full_command}")
        
        if capture_output:
            result = subprocess.run(
                full_command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result
        else:
            return subprocess.run(full_command, shell=True)
    
    def get_interactive_elements(self) -> Dict[str, Any]:
        """Get interactive elements with their references."""
        result = self.run_command("snapshot -i --json")
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise Exception(f"Failed to get elements: {result.stderr}")
    
    def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear."""
        result = self.run_command(f"wait {selector} --timeout {timeout}")
        return result.returncode == 0
    
    def fill_form_by_labels(self, form_data: Dict[str, str]) -> None:
        """Fill form using label-based semantic locators."""
        for label, value in form_data.items():
            command = f'find label "{label}" fill "{value}"'
            result = self.run_command(command)
            if result.returncode != 0:
                print(f"Warning: Failed to fill {label}: {result.stderr}")
    
    def take_screenshot(self, filename: str, full_page: bool = False) -> None:
        """Take screenshot of current page."""
        full_flag = "--full" if full_page else ""
        result = self.run_command(f"screenshot {filename} {full_flag}")
        if result.returncode != 0:
            raise Exception(f"Failed to take screenshot: {result.stderr}")
    
    def extract_table_data(self, table_selector: str = "table") -> List[List[str]]:
        """Extract data from HTML table."""
        # Get table HTML
        result = self.run_command(f"get html {table_selector}")
        if result.returncode != 0:
            raise Exception(f"Failed to get table HTML: {result.stderr}")
        
        # Parse table HTML (basic parsing)
        html = result.stdout
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
        
        table_data = []
        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            # Clean HTML tags and whitespace
            clean_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
            table_data.append(clean_cells)
        
        return table_data
    
    def login_and_save_state(self, login_url: str, credentials: Dict[str, str], 
                           success_url_pattern: str, state_file: str) -> None:
        """Complete login flow and save browser state."""
        # Navigate to login page
        self.run_command(f"open {login_url}")
        
        # Fill login form
        self.fill_form_by_labels(credentials)
        
        # Submit form (look for submit button)
        submit_result = self.run_command('find role button click --name "Submit"')
        if submit_result.returncode != 0:
            # Try alternative submit button patterns
            for pattern in ["Sign In", "Login", "Log In"]:
                result = self.run_command(f'find role button click --name "{pattern}"')
                if result.returncode == 0:
                    break
        
        # Wait for successful navigation
        self.run_command(f'wait --url "{success_url_pattern}"')
        
        # Save browser state
        self.run_command(f"state save {state_file}")
    
    def load_state_and_navigate(self, state_file: str, url: str) -> None:
        """Load saved browser state and navigate to URL."""
        self.run_command(f"state load {state_file}")
        self.run_command(f"open {url}")

def create_form_filling_script(form_mapping: Dict[str, str]) -> str:
    """Generate agent-browser commands for form filling."""
    commands = []
    
    for field_label, value in form_mapping.items():
        commands.append(f'agent-browser find label "{field_label}" fill "{value}"')
    
    return "\n".join(commands)

def create_table_extraction_script(table_selector: str = "table", output_file: str = "table_data.csv") -> str:
    """Generate script for extracting table data to CSV."""
    script = f"""# Extract table data
agent-browser get html {table_selector} --json > table_html.json

# Process with Python (run separately)
python3 -c "
import json
import re
import csv

with open('table_html.json', 'r') as f:
    html = json.load(f)['stdout']

# Parse table
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
table_data = []

for row in rows:
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
    clean_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
    table_data.append(clean_cells)

# Save to CSV
with open('{output_file}', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(table_data)

print(f'Table data saved to {output_file}')
"
"""
    return script

# Example usage patterns
if __name__ == "__main__":
    # Initialize helper
    browser = AgentBrowserHelper()
    
    # Example: Login to a service
    # browser.login_and_save_state(
    #     login_url="https://example.com/login",
    #     credentials={"Email": "user@example.com", "Password": "password123"},
    #     success_url_pattern="**/dashboard",
    #     state_file="auth_state.json"
    # )
    
    # Example: Extract table data
    # data = browser.extract_table_data("table.data-table")
    # print(f"Extracted {len(data)} rows")
    
    print("Agent Browser Helper utilities loaded.")
