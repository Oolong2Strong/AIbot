import os
import argparse
from dotenv import load_dotenv
import json
from prompts import system_prompt
from call_function import available_functions, call_function
import sys



load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key == None:
    raise RuntimeError("Key Not Found")

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)
parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("user_prompt", type=str, help="User prompt")
args = parser.parse_args()
# Now we can access `args.user_prompt`


messages = [
    {"role": "system","content": system_prompt},
    {"role": "user","content": args.user_prompt}
    ]


for _ in range(20):
    response = client.chat.completions.create(
    model="openrouter/free",
    messages=messages,
    tools=available_functions,
    )
    
    if response.usage == None:
        raise RuntimeError("No Response")
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print (f"Prompt tokens: {response.usage.prompt_tokens}")
        print (f"Response tokens: {response.usage.completion_tokens}")

    message = response.choices[0].message
    messages.append(message)
    if message.tool_calls:
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, verbose=args.verbose)
            messages.append(result_message)
            if not result_message["content"]:
                raise Exception("No content in result message")
            if args.verbose:
                print(f"-> {result_message['content']}")
    else:
        print(message.content)
        break
else:
    sys.exit("Maximum number of attempts reached")