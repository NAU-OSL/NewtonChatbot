<script lang="ts">
  import { onMount, tick } from 'svelte';
  import Below from "../icons/below.svelte";
  import Bottom from "../icons/bottom.svelte";
  import InnerCell from "../icons/innercell.svelte";
  import Copy from "../icons/fa-copy.svelte";
  import { notebookCommModel } from '../../stores';
  import { ContentFactory, ModelFactory } from '../chat/message/cellutils';
  import Above from '../icons/above.svelte';
  import IconButton from './IconButton.svelte';
  import type { IObservableString } from '@jupyterlab/observables';

  export let code: string;
  export let scrollBottom: () => void;
  export let direct: boolean = false;

  let tempcode: string | null = null;
  let tempcellvalue: IObservableString | null = null;


  let div: HTMLElement;
  onMount(async () => {
    const factory = new ContentFactory();
    const modelFactory = new ModelFactory({});

    const cell = factory.createRawCell({
      model: modelFactory.createRawCell({}),
    });
    cell.readOnly = true;
    cell.model.mimeType = "text/x-python";
    cell.model.value.text = code;
    div.appendChild(cell.node)
    if (scrollBottom) {
      await tick();
      await new Promise(r => setTimeout(r, 100));
      await tick();
      scrollBottom();
    }
  });

  function onLeaveRestore() {
    if (tempcode !== null && tempcellvalue !== null) {
      tempcellvalue.text = tempcode;
      tempcode = null;
      tempcellvalue = null;
    }
  }

  function onClickInsertAbove() {
    onLeaveRestore();
    $notebookCommModel?.insertAbove(code as string);
  }

  function onEnterInsertAbove() {
    onLeaveRestore();
    const content = $notebookCommModel?._notebook.content;
    const value = content?.activeCell?.model.value;
    if (value) {
      tempcellvalue = value;
      tempcode = value.text;
      value.text = "# ↑↑↑\n" + value.text;
    }
  }

  function onClickInsertBelow() {
    onLeaveRestore();
    $notebookCommModel?.insertBelow(code as string);
  }

  function onEnterInsertBelow() {
    onLeaveRestore();
    const content = $notebookCommModel?._notebook.content;
    const value = content?.activeCell?.model.value;
    if (value) {
      tempcellvalue = value;
      tempcode = value.text;
      value.text = value.text + "\n# ↓↓↓";
    }
  }

  function onClickInsertBottom() {
    onLeaveRestore();
    $notebookCommModel?.insertBottom(code as string);
  }

  function onEnterInsertBottom() {
    onLeaveRestore();
    const content = $notebookCommModel?._notebook.content;
    const cell = content?.widgets[content.widgets.length - 1]
    
    if (cell && cell.model.value) {
      const value = cell.model.value;
      tempcellvalue = value;
      tempcode = value.text;
      value.text = value.text + "\n# ↓↓↓";
    }
  }

  function onClickInsertOnCell() {
    onLeaveRestore();
    const content = $notebookCommModel?._notebook.content;
    const activeCell = content?.activeCell;
    if (activeCell) {
      const value = activeCell?.model.value;
      if (value) {
        let old = value.text;
        if (old.trim() != "") {
          old += '\n';
        }
        value.text = old + code as string
        activeCell.editorWidget.editor.focus();
      }
    }
  }

  function onEnterInsertOnCell() {
    onLeaveRestore();
    const content = $notebookCommModel?._notebook.content;
    const value = content?.activeCell?.model.value;
    if (value) {
      tempcellvalue = value;
      tempcode = value.text;
      let old = value.text;
      if (old.trim() != "") {
        old += '\n# ';
      } else {
        old += '# ';
      }
      value.text = old + code.split('\n').join('\n# ');
    }
  }
  
  function onClickCopy() {
    navigator.clipboard.writeText(code as string);
  }

</script>
  
  
  
<div class="outer" class:direct={direct}>
  <div class="inner" bind:this={div}/>
  {#if !direct}
    <div class="buttons">
      <IconButton on:click={onClickCopy} title="Copy to Clipboard"><Copy/></IconButton>
      <IconButton 
        on:click={onClickInsertAbove}
        on:mouseenter={onEnterInsertAbove}
        on:mouseleave={onLeaveRestore}
        title="Insert Cell Above"><Above/></IconButton>
      <IconButton
        on:click={onClickInsertBelow} 
        on:mouseenter={onEnterInsertBelow}
        on:mouseleave={onLeaveRestore}
        title="Insert Cell Below"><Below/></IconButton>
      <IconButton
        on:click={onClickInsertBottom}
        on:mouseenter={onEnterInsertBottom}
        on:mouseleave={onLeaveRestore}
        title="Insert Cell at the Bottom"><Bottom/></IconButton>
      
      <IconButton
        on:click={onClickInsertOnCell}
        on:mouseenter={onEnterInsertOnCell}
        on:mouseleave={onLeaveRestore}
        title="Insert on Current Cell"><InnerCell/></IconButton>
    </div>
  {/if}
</div>


<style>
  .inner :global(.jp-InputArea-prompt) {
    display: none;
  }

  .inner :global(.jp-InputCollapser) {
    display: none;
  }

  .inner :global(.jp-Cell) {
    padding: 0;
  }

  .outer :global(.CodeMirror) {
    z-index: 0;
    font-size: 1em;
  }

  .buttons {
    display: flex;
  }

  .direct :global(.CodeMirror) {
    background: none;
  }

  .direct :global(.jp-InputArea-editor) {
    border: none;
    background: none;
    white-space: pre-line;
  }
</style>