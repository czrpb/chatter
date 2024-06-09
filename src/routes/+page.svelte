<!-- App.svelte -->
<script>
    // @ts-nocheck

	// Add any necessary imports
	import { onMount } from "svelte";
	import SvelteMarkdown from "svelte-markdown";

	// Vars
	let apiRoot = 'http://localhost:11434/api';
	let apiChat = apiRoot + '/chat';
	let apiTags = apiRoot + '/tags';

	let prompt = 'What is Critical Realism?';
	let selected_models = [];
	let models = fetch(apiTags).then((r) => r.json());
	let messages = {};
	let messages_models = {};
	let waiting = false;

	function date_now() {
		const date = new Date(Date.now());
	    return date.toLocaleDateString(
			'en-US',
			{ year: 'numeric', month: '2-digit', day: '2-digit' }) + '-' + 
                date.toTimeString().substring(0, 8);
	}

	function clearChat() {
		document
		    .querySelector("div.chat-histories")
			.innerHTML = "";
		messages = {};
		messages_models = {};
	}

	function get_models(res) {
		var x = res
		.map((model) => [model['size'], model['name']]);

		return x
		.toSorted((a,b) => a[0]-b[0])
		.map((model) => model[1]);
	}

	async function generate() {
		if (!selected_models.length) {
			alert("No model selected."); return null;
		}
		
		var gtc = "100%";
		if (selected_models.length > 1) { gtc = "48% ".repeat(selected_models.length); }
		document
		    .querySelector("div.chat-histories")
			.style["grid-template-columns"] = gtc;

		waiting = true;
		selected_models.forEach(
			async (model) => {
				if (!messages.hasOwnProperty(model)) {
					messages[model] = [];
					messages_models[model] = [];
				}
				messages[model].push({"role": "user", "content": prompt});
				messages_models[model].push(null);
				const payload = {
					"model": model,
					"messages": messages[model],
					"stream": false
				};
				const request = new Request(apiChat, {
					"method": "POST",
					"body":  JSON.stringify(payload)
				});
				const response = await fetch(request);
				var res = await response.json();
				waiting = false;
				messages[model] = [...messages[model], res['message']];
				messages_models[model] = [...messages_models[model], model];
			}
		);

		return null;
	}

	async function copy_chat() {
		await navigator.clipboard.writeText(
			messages
			.map( (msg, idx) => {
				var role = msg['role'];
				var content = msg['content'];
				return ((role == "user") ?
						"## Me\n\n" :
						"## AI - " + messages_models[idx] + "\n\n"
					   ) + content;
			})
			.join("\n\n\n")
		);
	};

	let counter = 0;
	let highlight;
	onMount(() => {
		setInterval(() => {
			Array.from(document.getElementsByClassName('model')).forEach(
				(e) =>
				{
					if (selected_models.includes(e.innerText)) {
						counter = (counter == 360) ? 0 : counter + 1;
						highlight = `background: linear-gradient(${counter}deg, rgba(255,0,0,0.6) 25%, rgba(0,0,255,0.6) 75%)`;
						e.setAttribute('style', highlight);
					} else {
						e.setAttribute('style', '');
					}
				}
			);
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
					{#each get_models(res['models']) as name, idx}
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div class="model" idx="{idx}"
						     on:click={
							 	() =>
							 	(selected_models.includes(name)) ?
								 selected_models.splice(selected_models.indexOf(name), 1) :
								 selected_models.push(name)
							 }>
							{name}
						</div>
					{/each}
				{/await}
			</div>
			<button on:click={clearChat} disabled={waiting || !Object.keys(messages).length}>
				{#if waiting}
				    <span class="bounce">Chat In Progress</span>
				{:else}
				    Clear **ALL** Chats
				{/if}
			</button>
		</div>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="chat-histories">
			{#each selected_models.toSorted() as model}
   		    	<div class="chat-history" on:click={ (e) => { e.ctrlKey && copy_chat(); } }>
					{#each messages[model].toReversed().map(
				   		       (msg, idx) =>
							     [msg, messages_models[model].toReversed()[idx]]
				   	       ) as message_model}
			        	<h3>{#if message_model[0]['role'] == 'user'}Me{:else}AI - {message_model[1]}({date_now()}){/if}</h3>
			        	<SvelteMarkdown source={message_model[0]['content']} />
			    	{/each}
				</div>
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
		height: 90%;
		border-bottom: 1px solid #ccc;
		padding-top: 15px;
	}

	.controls {
		display: grid;
		grid-template-columns: auto auto;
		max-height: 30%;
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

	.chat-histories {
		display: grid;
    	/* grid-template-columns: repeat(auto-fill, 1fr); */
    	grid-gap: 10px;
		margin-top: 3px;
		max-height: 70%;
		overflow: scroll;
	}

	.chat-history {
		/* Add styles for chat history component */
		overflow-x: hidden;
		overflow-y: scroll;
	}

	.bounce {
		/* Add styles for bouncing text */
		animation: 10s linear infinite bounce;
		display: inline-block;
	}

	@keyframes bounce {
		0%, 100% { transform: translateX(0); }
		25% { transform: translateX(200%); }
		50% { transform: translateX(0); }
		75% { transform: translateX(-200%); }
	}

	textarea {
		margin-top: 0;
		margin-bottom: 5px;
	}
</style>
