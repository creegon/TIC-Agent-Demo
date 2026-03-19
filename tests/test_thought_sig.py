"""Test if thinking_budget=0 avoids thought_signature requirement"""
import json, os
from google import genai
from google.genai import types

for k in ['GOOGLE_API_KEY','GEMINI_API_KEY','GOOGLE_GENAI_API_KEY']:
    os.environ.pop(k, None)

c = genai.Client(vertexai=True, project='project-50ed99e3-757c-456d-800', location='global')

tools = [types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name='search',
        description='Search web for info',
        parameters={'type': 'object', 'properties': {'q': {'type': 'string'}}, 'required': ['q']}
    )
])]

# Step 1: Initial call with thinking_budget=0
config = types.GenerateContentConfig(
    max_output_tokens=200,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    tools=tools,
    tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode='ANY')),
)

r1 = c.models.generate_content(
    model='gemini-3-flash-preview',
    contents=[types.Content(role='user', parts=[types.Part(text='Search for USB charger CE requirements')])],
    config=config,
)

print("=== Step 1 Response ===")
fc_part = None
for part in r1.candidates[0].content.parts:
    if hasattr(part, 'function_call') and part.function_call:
        fc = part.function_call
        print(f"  Function call: {fc.name}({dict(fc.args)})")
        fc_part = part
    sig = getattr(part, 'thought_signature', None)
    print(f"  thought_signature present: {sig is not None}")
    if sig:
        print(f"  sig type: {type(sig).__name__}, len: {len(str(sig))}")

if not fc_part:
    print("No function call in response!")
    exit(1)

# Step 2: Send function response back
print("\n=== Step 2: Send tool response ===")
contents = [
    types.Content(role='user', parts=[types.Part(text='Search for USB charger CE requirements')]),
    r1.candidates[0].content,  # Use the raw response content (preserves thought_signature)
    types.Content(role='user', parts=[
        types.Part(function_response=types.FunctionResponse(
            name=fc_part.function_call.name,
            response={"results": [{"title": "CE for USB", "snippet": "LVD and EMC required"}]}
        ))
    ])
]

config2 = types.GenerateContentConfig(
    max_output_tokens=500,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    tools=tools,
)

try:
    r2 = c.models.generate_content(
        model='gemini-3-flash-preview',
        contents=contents,
        config=config2,
    )
    print(f"  Response text: {(r2.text or 'None')[:200]}")
    print("Step 2 SUCCESS with native content passthrough!")
except Exception as e:
    print(f"Step 2 FAILED: {e}")
    
    # Try without thought_signature
    print("\n=== Step 2b: Try manually constructing content (no signature) ===")
    contents2 = [
        types.Content(role='user', parts=[types.Part(text='Search for USB charger CE requirements')]),
        types.Content(role='model', parts=[types.Part(function_call=types.FunctionCall(
            name=fc_part.function_call.name, args=dict(fc_part.function_call.args)
        ))]),
        types.Content(role='user', parts=[
            types.Part(function_response=types.FunctionResponse(
                name=fc_part.function_call.name,
                response={"results": [{"title": "CE for USB", "snippet": "LVD and EMC required"}]}
            ))
        ])
    ]
    try:
        r2b = c.models.generate_content(
            model='gemini-3-flash-preview',
            contents=contents2,
            config=config2,
        )
        print(f"  Response text: {(r2b.text or 'None')[:200]}")
        print("Step 2b SUCCESS without signature!")
    except Exception as e2:
        print(f"Step 2b ALSO FAILED: {e2}")
