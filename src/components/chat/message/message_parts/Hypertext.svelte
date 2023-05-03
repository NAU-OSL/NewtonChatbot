<script lang="ts">
  import type { IMessagePart } from "../../../../common/chatbotInterfaces";

  export let messagePart: IMessagePart;
</script>

<div>{@html messagePart.text}</div>