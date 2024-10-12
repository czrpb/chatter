import flet as ft
import ollama
import requests
import json
import pprint

def bot_new(ollama_host):
    return {
        "ollama_host": ollama_host,
        "model": None
    }

def bot_connect(bot):
    bot["client"] = ollama.Client(host=bot["ollama_host"])
    return bot

def bot_load_models(bot):
    models = bot["client"].list()
    bot["models"] = [model['name'] for model in models['models']]
    bot["messages"] = []
    return bot

def bot_chat(bot, prompt):
    match bot:
        case {"client": client, "model": model}:
            bot["messages"].append({"role": "user", "content": prompt})
            print("======  BEFORE ===============")
            pprint.pprint(bot["messages"])
            print("======  BEFORE ===============")
            response = client.chat(model=model, messages=bot["messages"], stream=False)
            pprint.pprint(response)
            bot["messages"].append({"role": response["message"]["role"], "content": response["message"]["content"]})
            print("======  AFTER ===============")
            pprint.pprint(bot["messages"])
            print("======  AFTER ===============")
            return bot
    raise RuntimeError(f"Bot invalid:\n{bot}")

def main(page: ft.Page):
    page.title = "Chatter"
    page.vertical_alignment = ft.MainAxisAlignment.START
    chatbot = None

    def on_ollama_host_submit(e):
        if not ollama_host_input.value:
            return
        try:
            nonlocal chatbot
            chatbot = bot_connect(bot_new(ollama_host_input.value))
            status_text.value = f"Connected to {chatbot["ollama_host"]}"
            
            # Fetch and populate the model list
            bot_load_models(chatbot)
            model_dropdown.options = [ft.dropdown.Option(model) for model in chatbot["models"]]
            model_dropdown.disabled = False            
        except Exception as ex:
            status_text.value = f"Failed to connect or fetch models: {str(ex)}"

        page.update()

    def on_model_change(e):
        chatbot["model"] = model_dropdown.value
        user_input.disabled = False

        page.update()

    def on_chat_submit(e):
        user_message = user_input.value
        user_input.value = ""

        bot_chat(chatbot, user_message)

        chat_messages.controls.insert(0, ft.Divider(height=10, thickness=7, color=ft.colors.DEEP_ORANGE_200))
        chat_messages.controls.insert(0, ft.Markdown(f"### LLM {chatbot["model"]}\n\n{chatbot["messages"][-1]["content"]}"))
        chat_messages.controls.insert(0, ft.Markdown(f"## You\n> {chatbot["messages"][-2]["content"]}"))
        page.update()

    ollama_host_input = ft.TextField(
        label="Ollama Host",
        hint_text="localhost OR 192.168.50.247",
        on_submit=on_ollama_host_submit
    )

    status_text = ft.Text("")

    model_dropdown = ft.Dropdown(
        label="Choose a model",
        options=[],  # Will be populated dynamically
        disabled=True,
        on_change=on_model_change
    )

    user_input = ft.TextField(
        label="Your input to the LLM",
        hint_text="What is Critical Realism?",
        multiline=True,
        min_lines=3,
        max_lines=5,
        on_submit=on_chat_submit,
        shift_enter=True,
        disabled=True
    )

    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    page.add(
        ft.Row([ollama_host_input, ft.ElevatedButton("Connect", on_click=on_ollama_host_submit)]),
        status_text,
        model_dropdown,
        user_input,
        ft.Container(
            content=chat_messages,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
    )

ft.app(target=main)
