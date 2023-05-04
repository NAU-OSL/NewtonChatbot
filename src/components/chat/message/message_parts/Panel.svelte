<script lang="ts">
  import { DockLayout } from "@lumino/widgets";
  import type { IChatMessage, IMessagePart } from "../../../../common/chatbotInterfaces";
  import { panelWidget } from "../../../../stores";

  export let message: IChatMessage
  export let messagePart: IMessagePart
  export let preview: boolean
  export let type: 'url' | 'html' | 'text'
  let title: string = 'Info'
  let content: string = messagePart.text
  let desc: string = messagePart.text
  let mode: DockLayout.InsertMode = 'split-right';

  let split = messagePart.text.split(/#:(.*)/s, 2)
  console.log(split)
  if (split.length == 2) {
    desc = title = split[0]
    if (split[1]) {
      split = split[1].split(/#:(.*)/s, 2)
      if (split.length == 2) {
        if (['split-top', 'split-left', 'split-right', 'split-bottom', 'tab-before', 'tab-after'].includes(split[0].trim())) {
          mode = split[0].trim() as DockLayout.InsertMode;
        }
        content = split[1]
      } else {
        content = split[0]
      }
    }
  }

  if (message.new && !preview) {
    message.new = false
    panelWidget.load_panel(content, title, type, mode)
  }

  function onClick(e: any) {
    panelWidget.load_panel(content, title, type, mode)
  }
</script>

<style>
  div {
    word-break: break-all;
  }

  button {
    cursor: pointer;
    border: none;
  }
</style>

<div><button on:click={onClick}>📖</button>{desc}</div>