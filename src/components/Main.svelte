<script lang="ts">
  import { connectionReady, notebookCommModel, kernelStatus, restrictNotebooks, wizardMode } from '../stores';
  import Chat from './chat/Chat.svelte';
  import AutoCompleteInput from './chat/AutoCompleteInput.svelte';
  import Header from './header/Header.svelte';
  import WizardChat from './chat/WizardChat.svelte';
  import { get } from 'svelte/store';
  import type { IChatInstance } from '../chatinstance';

  let chatInstance: IChatInstance;
  let name: string;
  $: if ($notebookCommModel) {
    chatInstance = get($notebookCommModel.chatInstances)["base"]
  }
  $: if ($connectionReady && $notebookCommModel) {
    chatInstance = get($notebookCommModel.chatInstances)["base"]
    name = $notebookCommModel.name;
  }
  $: ({ hasKernel } = $kernelStatus);
</script>

{#if chatInstance}

  {#if $notebookCommModel && ($restrictNotebooks.length === 0 || $restrictNotebooks.includes(name)) }
    {#key chatInstance}
      <Header {chatInstance} title="Newton - {name}"/>
    {/key}
    <Chat {chatInstance} isExtraChat={false}/>
    {#if $hasKernel}
      {#if $wizardMode}
        <WizardChat {chatInstance}/>
      {:else}
        <AutoCompleteInput {chatInstance}/>
      {/if}
    {/if}
  {:else}
    {#key chatInstance}
      <Header {chatInstance} title="Newton"/>
    {/key}
    {#if $restrictNotebooks.length !== 0}
      Currently, the chatbot only works on files named {$restrictNotebooks.join(" or ")}.
    {/if}
  {/if}

{/if}
