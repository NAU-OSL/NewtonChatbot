
<script lang="ts">
  import { beforeUpdate, afterUpdate } from 'svelte';
  import type { IChatInstance } from '../../chatinstance';
  import Message from './message/Message.svelte';

  export let chatInstance: IChatInstance;
  export let isExtraChat: boolean;

  let { showExtraMessages } = chatInstance.config;
  
  let div: HTMLElement;
  let autoscroll = true;

  beforeUpdate(() => {
    autoscroll = div && (div.offsetHeight + div.scrollTop) > (div.scrollHeight - 20);
  });

  export function scrollBottom() {
    if (autoscroll) div.scrollTo(0, div.scrollHeight);
  }

  afterUpdate(() => {
    scrollBottom();
  });

</script>

<style>
  div {
    overflow: auto;
    height: 100%;
    padding-top: 0.8em;
    scrollbar-gutter: stable;
  }
</style>


<div bind:this={div}>
  {#each $chatInstance as message, index (message.id)}
    {#if $showExtraMessages || !isExtraChat || (message.type == "error") || message.isGPTMessage || message.isUserPrompt }
      <Message {chatInstance} {message} chat={div} {scrollBottom} {index} {isExtraChat}/>
    {/if}
  {/each}
</div>