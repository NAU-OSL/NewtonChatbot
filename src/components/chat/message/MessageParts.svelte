<script lang="ts">
  import type { IChatMessage, IMessagePart } from "../../../common/chatbotInterfaces";
  import { splitUnifiedMessage } from "../../../common/messages";
  import Code from "./message_parts/Code.svelte";
  import Form from "./message_parts/Form.svelte";
  import FullOptions from "./message_parts/FullOptions.svelte";
  import Hypertext from "./message_parts/Hypertext.svelte";
  import Options from "./message_parts/Options.svelte";
  import Panel from "./message_parts/Panel.svelte";
  import TextInput from "./message_parts/TextInput.svelte";
  import Text from "./message_parts/Text.svelte";
  import type { IChatInstance } from "../../../chatinstance";
  import Metadata from "./message_parts/Metadata.svelte";
  import Markdown from "./message_parts/Markdown.svelte";

  export let chatInstance: IChatInstance;
  export let message: IChatMessage
  export let scrollBottom: () => void
  export let preview: boolean = false

  let items: IMessagePart[] = splitUnifiedMessage(message.text);
</script>

{#each items as messagePart}
  {#if messagePart.type == 'ul' || messagePart.type == 'ol'}
    <Options {chatInstance} {messagePart} {message}/>
  {:else if messagePart.type == 'ful' || messagePart.type == 'fol'}
    <FullOptions {chatInstance} {messagePart} {message}/>
  {:else if messagePart.type == 'code'}
    <Code {messagePart} {scrollBottom}/>
  {:else if messagePart.type == 'direct-code'}
    <Code {messagePart} {scrollBottom} direct={true}/>
  {:else if messagePart.type == 'html'}
    <Hypertext {messagePart}/>
  {:else if messagePart.type == 'input'}
    <TextInput {chatInstance} {messagePart} {message}/>
  {:else if messagePart.type == 'web-panel'}
    <Panel {messagePart} {message} {preview} type='url'/>
  {:else if messagePart.type == 'text-panel'}
    <Panel {messagePart} {message} {preview} type='text'/>
  {:else if messagePart.type == 'html-panel'}
    <Panel {messagePart} {message} {preview} type='html'/>
  {:else if messagePart.type == 'form'}
    <Form {chatInstance} {messagePart} {message}/>
  {:else if messagePart.type == 'markdown'}
    <Markdown {messagePart} {scrollBottom}/>
  {:else if messagePart.type == 'metadata'}
    <Metadata {chatInstance} {messagePart}/>
  {:else}
    <Text {messagePart}/>
  {/if}
{/each}