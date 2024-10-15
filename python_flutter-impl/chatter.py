import flet as ft
import ollama
import requests
import json
import pprint
from operator import setitem

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
            response = client.chat(model=model, messages=bot["messages"], stream=False)
            bot["messages"].append({"role": response["message"]["role"], "content": response["message"]["content"]})
            return bot
    raise RuntimeError(f"Bot invalid:\n{bot}")

def main(page: ft.Page):
    page.title = "Chatter"
    page.vertical_alignment = ft.MainAxisAlignment.START

    def keypress(e):
        if (e.ctrl and e.key == "Q"):
            page.window.close()
    page.on_keyboard_event = keypress

    chatbot = None
    previous_button = None

    def on_ollama_host_submit(e):
        if not ollama_host_input.value:
            return
        try:
            nonlocal chatbot
            chatbot = bot_connect(bot_new(ollama_host_input.value))
            status_text.value = f"Connected to {chatbot["ollama_host"]} |"
            
            # Fetch and populate the model list
            bot_load_models(chatbot)

            for model in chatbot["models"]:
                but = ft.FilledButton(model)
                but.style = ft.ButtonStyle(
                    color=ft.colors.BLACK,
                    bgcolor=ft.colors.WHITE
                )
                but.on_click = (lambda model, but: (lambda _: on_model_change(model, but)))(model, but)
                model_list.controls.append(but)

        except Exception as ex:
            status_text.value = f"Failed to connect or fetch models: {str(ex)}"

        page.update()

    def on_model_change(model, da_button):
        nonlocal previous_button

        chatbot["model"] = model
        user_input.disabled = False

        if previous_button:
            previous_button.style.color = ft.colors.BLACK
            previous_button.style.bgcolor = ft.colors.WHITE
        da_button.style.color = ft.colors.WHITE
        da_button.style.bgcolor = ft.colors.BLACK
        previous_button = da_button

        status_text.value = status_text.value[:status_text.value.index("|")+1] + f" Model {model} selected"
        page.update()

    def on_clear(e):
        chatbot["messages"].clear()
        chat_messages.controls.clear()
        clear_button.disabled = True
        page.update()

    def on_copy(e):
        page.set_clipboard(
            "\n\n====================\n\n".join(
                [f"[{message["role"]}]\n\n{message["content"]}" for message in chatbot["messages"]]
            )
        )

    def on_chat_submit(e):
        user_message = user_input.value
        user_input.value = ""

        bot_chat(chatbot, user_message)

        chat_messages.controls.insert(0, ft.Divider(height=10, thickness=7, color=ft.colors.DEEP_ORANGE_200))
        chat_messages.controls.insert(0, ft.Markdown(f"### LLM {chatbot["model"]}\n\n{chatbot["messages"][-1]["content"]}"))
        chat_messages.controls.insert(0, ft.Markdown(f"## You\n> {chatbot["messages"][-2]["content"]}"))

        copy_button.disabled = False
        clear_button.disabled = False

        page.update()

    ollama_host_input = ft.TextField(
        label="Ollama Host",
        width=250,
        hint_text="localhost OR 192.168.50.247",
        on_submit=on_ollama_host_submit
    )

    status_text = ft.Text("")

    model_list = ft.ListView(expand=True)

    user_input = ft.TextField(
        label="Your input to the LLM",
        hint_text="What is Critical Realism?",
        multiline=True,
        min_lines=3,
        max_lines=5,
        on_submit=on_chat_submit,
        shift_enter=True,
        expand=True,
        disabled=True
    )

    clear_button = ft.ElevatedButton("Clear", on_click=on_clear, disabled=True)
    copy_button = ft.ElevatedButton("Copy", on_click=on_copy, disabled=True)

    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    page.add(
        ft.Row([ollama_host_input, status_text]),
        ft.Row([
            ft.Container(
                content=model_list,
                height=100,
                width=250,
                border=ft.border.all(1, ft.colors.OUTLINE)
            ),
            user_input]),
        ft.Row([copy_button, clear_button]),
        ft.Container(
            content=chat_messages,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
    )

ft.app(target=main)
