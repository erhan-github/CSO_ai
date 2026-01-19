
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd() + '/src')

from side.tools.audit import handle_run_audit


import asyncio
import json

# Run audit on web/app
async def main():
    try:
        # Change to the web app directory so ForensicEngine scans the right files
        target_path = '/Users/erhanerdogan/Desktop/side/web/app'
        os.chdir(target_path)
        
        # handle_run_audit expects a dict of arguments
        result = await handle_run_audit({})
        print(result) 
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
