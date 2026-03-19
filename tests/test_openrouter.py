from openai import OpenAI
c = OpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key='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',
)
r = c.chat.completions.create(
    model='google/gemini-2.0-flash-001',
    messages=[{'role':'user','content':'Search for EU CE requirements for USB charger'}],
    tools=[{
        'type': 'function',
        'function': {
            'name': 'search',
            'description': 'Search the web for regulatory info',
            'parameters': {'type':'object','properties':{'query':{'type':'string'}},'required':['query']}
        }
    }],
    tool_choice='auto',
    max_tokens=200,
)
msg = r.choices[0].message
has_tools = msg.tool_calls is not None
if has_tools:
    for tc in msg.tool_calls:
        print(f"Tool call: {tc.function.name}({tc.function.arguments})")
content = msg.content or "None"
print(f"Content: {content[:100]}")
print(f"Finish: {r.choices[0].finish_reason}")
print("Tools supported: YES" if has_tools else "Tools supported: NO (model answered directly)")
