<!-- App.svelte -->
<script>
	// Add any necessary imports
	import SvelteMarkdown from "svelte-markdown";
	
	// Vars
	let apiRoot = 'http://localhost:11434/api/chat';
	let prompt = 'What is Critical Realism?';

	let reply = '';
	function generate() {
		const payload = {
            "model": "phi3",
			"messages": [
				{
					"role": "user",
					"content": "What is Critical Realism?"
				}
			],
            "stream": false
        };
		const request = new Request(apiRoot, {
            "method": "POST",
			"body":  JSON.stringify(payload)
		});
		const response = fetch(request)
		.then((response) => { return response.json(); })
		.then((response) => {
			reply = response['message']['content']
			//reply = JSON.stringify(JSON.parse(response['response']))
			;
		});
		return null;
	}
</script>

<div class="app">
	<h1 class="app-title">Chatter</h1>
	<div class="main">
		<textarea placeholder="Enter prompt" bind:value={prompt} cols="100" rows="10"
		on:keyup={ (k) => { k.ctrlKey && k.code == "Enter" && generate(); } }
		/>
		<div class="chat-history">
			{reply}
		</div>
	</div>
</div>

<style>
	.app {
		display: block;
		height: 100vh;
		border: 2px solid #333;
		padding: 20px;
	}

	.app-title {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		text-align: center;
		background-color: #333;
		color: #fff;
		padding: 10px;
		margin: 0;
	}

	.main {
		display: block;
		border-bottom: 1px solid #ccc;
		padding-top: 35px;
	}

	.chat-history {
		/* Add styles for chat history component */
	}

	textarea {
		margin-bottom: 5px;
	}
</style>
