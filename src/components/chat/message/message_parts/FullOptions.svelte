<script lang="ts">
  import type { IChatInstance } from "../../../../chatinstance";
  import type { IChatMessage, IMessagePart } from "../../../../common/chatbotInterfaces";
  import Options from "./Options.svelte";
  import Text from "./Text.svelte";
  import TextInput from "./TextInput.svelte";

  export let chatInstance: IChatInstance;
  export let messagePart: IMessagePart;
  export let message: IChatMessage;
</script>

<Text messagePart={{type: 'text', text: 'Suggestions (clickable):', source: message.text}}/>
<Options {chatInstance} {messagePart} {message}/>
<TextInput {chatInstance} messagePart={{type: 'input', text:'Ask a different question', source: message.text}} {message}/>
