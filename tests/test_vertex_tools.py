"""Test Vertex proxy function calling with a full round-trip"""
import json
from openai import OpenAI

c = OpenAI(base_url='http://127.0.0.1:8046/v1', api_key='any')

# Step 1: Initial call with tools → should get function_call back
print("=== Step 1: Initial call with tools ===")
messages = [
    {"role": "system", "content": "You are a compliance expert. Use the search tool."},
    {"role": "user", "content": "Search for USB charger CE requirements in EU"},
]
tools = [{
    "type": "function",
    "function": {
        "name": "search_regulations",
        "description": "Search the web for regulatory information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "search query"}
            },
            "required": ["query"]
        }
    }
}]

try:
    r1 = c.chat.completions.create(
        model='gemini-3-flash',
        messages=messages,
        tools=tools,
        tool_choice='required',
        max_tokens=200,
    )
    msg1 = r1.choices[0].message
    print(f"Tool calls: {msg1.tool_calls is not None}")
    if msg1.tool_calls:
        for tc in msg1.tool_calls:
            print(f"  {tc.id}: {tc.function.name}({tc.function.arguments})")
    print(f"Finish: {r1.choices[0].finish_reason}")
except Exception as e:
    print(f"Step 1 FAILED: {e}")
    exit(1)

# Step 2: Send tool response back → should get text response
print("\n=== Step 2: Send tool response back ===")
messages.append({
    "role": "assistant",
    "content": None,
    "tool_calls": [
        {
            "id": msg1.tool_calls[0].id,
            "type": "function",
            "function": {
                "name": msg1.tool_calls[0].function.name,
                "arguments": msg1.tool_calls[0].function.arguments,
            }
        }
    ]
})
messages.append({
    "role": "tool",
    "tool_call_id": msg1.tool_calls[0].id,
    "name": msg1.tool_calls[0].function.name,
    "content": json.dumps({
        "results": [
            {"title": "CE Marking for USB Chargers", "url": "https://example.com", "snippet": "USB chargers need CE marking with LVD and EMC directives"}
        ]
    })
})

try:
    r2 = c.chat.completions.create(
        model='gemini-3-flash',
        messages=messages,
        tools=tools,
        tool_choice='auto',
        max_tokens=500,
    )
    msg2 = r2.choices[0].message
    print(f"Tool calls: {msg2.tool_calls is not None}")
    print(f"Content: {(msg2.content or 'None')[:200]}")
    print(f"Finish: {r2.choices[0].finish_reason}")
    print("SUCCESS!")
except Exception as e:
    print(f"Step 2 FAILED: {e}")
