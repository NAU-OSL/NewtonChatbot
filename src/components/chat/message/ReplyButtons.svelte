<script lang="ts">
  import type { IChatMessage } from "../../../common/chatbotInterfaces";
  import { wizardMode } from "../../../stores";
  import Eye from "../../icons/eye.svelte";
  import Reply from "../../icons/fa-reply.svelte";
  import { createEventDispatcher } from 'svelte';
  import IconButton from "../../generic/IconButton.svelte";
  import type { IChatInstance } from "../../../chatinstance";

  export let chatInstance: IChatInstance;
  export let message: IChatMessage;
  export let viewReplied: boolean;

  let { replying } = chatInstance;

  const dispatch = createEventDispatcher();
  
  function select(e: any) {
    if ($replying == message.id) {
      $replying = null;
    } else {
      $replying = message.id;
    }
  }

  function toggleViewReplied() {
    viewReplied = !viewReplied;
		dispatch('toggleViewReplied', {
      viewReplied
    });
	}

  $: selected = $replying == message.id;
</script>

<div class="buttons">
  {#if message.reply}
    <IconButton 
      title={viewReplied? "Hide replied message" : "View replied message"} 
      selected={viewReplied}
      on:click={toggleViewReplied}
    ><Eye/></IconButton>
  {/if}

  <IconButton 
    title={selected? "Replying to" : "Reply to"}
    selected={selected} 
    hide={!$wizardMode && message.type == 'user'}
    on:click={select}
  ><Reply/></IconButton>
</div>
