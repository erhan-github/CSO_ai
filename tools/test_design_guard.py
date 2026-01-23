
import asyncio
import sys
from pathlib import Path

# Mock sys.path to find backend
sys.path.append(str(Path.cwd() / "backend" / "src"))

from side.server import resource_manager, prompt_manager

async def test_guard():
    print("🎨 Testing Design Guard...")
    
    # 1. Create a Fake Design System (if not exists)
    web_ui = Path("web/components/ui")
    web_ui.mkdir(parents=True, exist_ok=True)
    (web_ui / "Button.tsx").touch()
    (web_ui / "Card.tsx").touch()
    
    # 2. Mock User Input (Bad Code)
    bad_code = """
    export default function MyComponent() {
        return (
            <div className="p-4 bg-white shadow-md rounded">
                <button className="bg-blue-500 text-white p-2">Click Me</button>
            </div>
        )
    }
    """
    
    # 3. Call the Prompt Handler
    try:
        # We need to manually trigger the logic inside get_prompt_result
        # Since prompt_manager is what we use in server.py
        result = prompt_manager.get_prompt_result("check_design", {"code": bad_code})
        
        print("\n✅ Prompt Generated Successfully:")
        print(f"--- Description: {result.description} ---")
        msg = result.messages[0].content.text
        print(msg)
        
        if "Button" in msg and "Card" in msg:
            print("\n✅ SUCCESS: Approved Components detected in context.")
        else:
            print("\n❌ FAILURE: Components not found in context.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_guard())
