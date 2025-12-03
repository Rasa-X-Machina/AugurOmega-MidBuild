# Assuming both files are in the same directory
from .message_utils import sanitize_message_history
from typing import List, Dict, Any
def sanitize_message_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters message history to ensure referential integrity for Minimax/OpenAI APIs.
    Removes 'tool' responses (orphans) if their parent 'assistant' call is missing.
    """
    sanitized_history = []
    valid_tool_ids = set()

    for msg in messages:
        role = msg.get("role")
        
        # 1. Register valid parents
        if role == "assistant":
            if "tool_calls" in msg and msg["tool_calls"]:
                for tool_call in msg["tool_calls"]:
                    valid_tool_ids.add(tool_call.get("id"))
            sanitized_history.append(msg)

        # 2. Check children against parents
        elif role == "tool":
            tool_id = msg.get("tool_call_id")
            if tool_id in valid_tool_ids:
                sanitized_history.append(msg)
            else:
                # Log this drop if you have a logger configured
                pass 

        # 3. Allow User/System messages
        else:
            sanitized_history.append(msg)

    return sanitized_history