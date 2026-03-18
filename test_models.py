import json
from openai import OpenAI

with open(r'C:\Users\creegon\.openclaw\openclaw.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)
key = cfg.get('agents',{}).get('defaults',{}).get('memorySearch',{}).get('remote',{}).get('apiKey','')

c = OpenAI(
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/',
    api_key=key,
)

models = ['gemini-2.5-flash-preview-04-17', 'gemini-2.0-flash-001', 'gemini-1.5-flash']

for model in models:
    try:
        r = c.chat.completions.create(
            model=model,
            messages=[{'role':'user','content':'say hi'}],
            tools=[{
                'type': 'function',
                'function': {
                    'name': 'search',
                    'description': 'Search',
                    'parameters': {'type':'object','properties':{'q':{'type':'string'}},'required':['q']}
                }
            }],
            tool_choice='auto',
            max_tokens=50,
        )
        msg = r.choices[0].message
        has_tools = msg.tool_calls is not None
        content = (msg.content or "None")[:30]
        print(f"{model}: OK, tools={has_tools}, content={content}")
    except Exception as e:
        err = str(e)[:120]
        print(f"{model}: FAIL - {err}")
