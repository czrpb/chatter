<!-- App.svelte -->
<script>
	// Add any necessary imports
	import { onMount } from "svelte";
	import SvelteMarkdown from "svelte-markdown";

	// Vars
	let apiRoot = 'http://localhost:11434/api';
	let apiChat = apiRoot + '/chat';
	let apiTags = apiRoot + '/tags';

	let prompt = 'What is Critical Realism?';
	let model;
	let models = fetch(apiTags).then((r) => r.json());
	let messages = [];

	async function generate() {
		messages.unshift({
            "role": "user",
			"content": prompt
		});
		const payload = {
            "model": model,
			"messages": messages,
            "stream": false
        };
		const request = new Request(apiChat, {
            "method": "POST",
			"body":  JSON.stringify(payload)
		});
		const response = await fetch(request);
		var res = await response.json();
		messages = [res['message'], ...messages];
		//messages.push(res['message']);
		console.log(messages);
		return null;
	}

	let selected;
	let counter = 0;
	let highlight;
	onMount(() => {
		setInterval(() => {
			Array.from(document.getElementsByClassName('model')).forEach((e) => {
				if (e.innerText == model) {
					counter = (counter == 360) ? 0 : counter + 1;
					highlight = `background: linear-gradient(${counter}deg, rgba(255,0,0,0.6) 25%, rgba(0,0,255,0.6) 75%)`;
					e.setAttribute('style', highlight);
				} else {
					e.setAttribute('style', '');
				}
			});
		}, 750);
	});
</script>

<div class="app">
	<h1 class="app-title">Chatter</h1>
	<div class="main">
		<div class="controls">
    		<textarea bind:value={prompt} cols="50" rows="10"
	         on:keyup={ (k) => { k.ctrlKey && k.code == "Enter" && generate(); } }
		    />
			<div class="models">
				{#await models}
					<b>Loading models....</b>
				{:then res}
					{#each res['models'].map((model) => model['model'].split(":")[0]).toSorted() as name}
						<div class="model" on:click={ () => model=name }>
							{name}
						</div>
					{/each}
				{/await}
			</div>
		</div>
		<div class="chat-history">
			{#each messages as message}
			    <h3>{#if message['role'] == 'user'}Me{:else}AI{/if}</h3>
			    <SvelteMarkdown source={message['content']} />
			{/each}
		</div>
	</div>
</div>

<style>
	.app {
		display: block;
		height: 90vh;
		border: 2px solid #333;
		padding: 20px;
	}

	.app-title {
		text-align: center;
		background-color: #333;
		color: #fff;
		padding: 10px;
		margin: 0;
	}

	.main {
		display: block;
		margin: auto;
		width: 80%;
		border-bottom: 1px solid #ccc;
		padding-top: 35px;
	}

	.controls {
		display: grid;
		grid-template-columns: auto auto;
	}

	.models {
		grid-column: 2 /2;
		display: block;
		overflow-y: scroll;
		margin-top: 1px;
		margin-left: 5px;
	}

	.model {
		margin-bottom: 1px;
		border: 1px solid white;
	}
	.model:hover {
		margin-bottom: 1px;
		border: 1px solid red;
	}

	.chat-history {
		/* Add styles for chat history component */
		height: 68vh;
		overflow-y: scroll;
	}

	textarea {
		margin-top: 0;
		margin-bottom: 5px;
	}
</style>
