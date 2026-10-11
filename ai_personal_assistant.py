# AI Personal Assistant using LLM
# Hex Softwares internship - Task 3
# Tushar Pachare

import os
import getpass
from groq import Groq

# api key is read from environment variable GROQ_API_KEY (not written in the code)
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    # key not found, so ask for it here (what you type is hidden, even when you paste)
    print("GROQ_API_KEY not found in environment.")
    api_key = getpass.getpass("Paste your Groq API key and press Enter: ")


def clean_key(key):
    # remove spaces and quotes, people often paste the key with quotes
    return key.strip().strip('"').strip("'").strip()


api_key = clean_key(api_key)

if api_key == "":
    print("No API key given, closing the program")
    exit()

# show only first 4 letters and length so we can check the key without showing it
print("Key received: starts with", api_key[:4], "| length", len(api_key))
if not api_key.startswith("gsk_"):
    print("Warning: Groq keys normally start with gsk_ , maybe the wrong text was pasted")

client = Groq(api_key=api_key)

# model name (if error comes, run the model list command from the readme and use a name from it)
model = "openai/gpt-oss-20b"

# tells the model how to behave
system_prompt = "You are a helpful personal assistant. Give clear and short answers."

# chat history so the bot remembers what we talked before
history = [{"role": "system", "content": system_prompt}]

# reminders list
reminders = []


def ask_ai():
    # send full history to the model
    global client
    try:
        res = client.chat.completions.create(model=model, messages=history)
        return res.choices[0].message.content
    except Exception as e:
        # wrong api key -> ask for a new one and try again
        if "invalid_api_key" in str(e):
            print("Assistant: Your API key is not valid (Groq rejected it).")
            print("Create a new key at console.groq.com/keys if needed.")
            new_key = clean_key(getpass.getpass("Paste a correct key (or just press Enter to quit): "))
            if new_key == "":
                print("Closing the program")
                exit()
            print("Key received: starts with", new_key[:4], "| length", len(new_key))
            client = Groq(api_key=new_key)
            return ask_ai()

        print("Assistant: Sorry, some problem came while connecting to AI")
        print("Error:", e)
        if "model_not_found" in str(e):
            print("Hint: this model name is not available for your key, change the model name at the top\n")
        else:
            print()
        return None


print("=" * 50)
print("      AI PERSONAL ASSISTANT")
print("=" * 50)
print("Type a question and I will answer it.")
print("summarize: <text>  -> summary of the text")
print("remind <task> at <time>  -> save reminder")
print("reminders  -> show reminders")
print("clear  -> clear chat history")
print("exit  -> quit\n")

while True:
    user = input("You: ").strip()

    if user == "":
        continue

    low = user.lower()

    if low == "exit":
        print("Assistant: Bye!")
        break

    # clear history
    if low == "clear":
        history = [{"role": "system", "content": system_prompt}]
        print("Assistant: Chat cleared\n")
        continue

    # show reminders
    if low == "reminders":
        if len(reminders) == 0:
            print("Assistant: No reminders yet\n")
        else:
            print("Assistant: Your reminders")
            for i in range(len(reminders)):
                print(" ", str(i + 1) + ".", reminders[i])
            print()
        continue

    # add reminder, format: remind <task> at <time>
    if low.startswith("remind "):
        r = user[7:].strip()
        if r == "":
            print("Assistant: Please write what to remind, example: remind submit synopsis at 5 pm\n")
        else:
            reminders.append(r)
            print("Assistant: Reminder saved ->", r, "\n")
        continue

    # summarize
    if low.startswith("summarize:"):
        text = user[10:].strip()
        if text == "":
            print("Assistant: Please give some text after summarize:\n")
            continue
        message = "Summarize this text in 2-3 sentences: " + text
    else:
        message = user

    # send to AI
    history.append({"role": "user", "content": message})
    answer = ask_ai()

    if answer is None:
        # api failed, remove the last message from history
        history.pop()
        continue

    history.append({"role": "assistant", "content": answer})

    # keep history small (system prompt + last 20 messages)
    if len(history) > 21:
        history = [history[0]] + history[-20:]

    print("Assistant:", answer, "\n")