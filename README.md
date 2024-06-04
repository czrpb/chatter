# Chatter

Chatter is a "quick" attempt to build a chatbot against Ollama.

### Credit

Might be nice to tell me if you like this or if you use it in some way!

:stuck_out_tongue_winking_eye:

## Docs

[Requirements](requirements.md)

[Design](design.md)

[User Stories](user-stories.md)

[UX / UI](ux-ui.md)

## Features

1. Select model from installation's known models.
   1. Can change models, which will receive the whole chat history.
1. Ctrl-Enter to submit current prompt as latest message in the chat.
1. Chat is displayed reverse, most recent prompt and reply is at top.
1. Ctrl-Click in the chat area copies its markdown.

## Get Up and Running!

1. Get ollama
   1. Get a model
      * `ollama run codellama:7b`
      * `ollama run codegemma:latest`
   1. Start it: `ollama serve`
1. Get node
1. Get this code
   1. Start it: `npm run dev`
1. Browse and chat!

## Movie

https://github.com/czrpb/chatter/assets/33663800/92736cd8-52d6-487f-9331-8dfc54beff83
