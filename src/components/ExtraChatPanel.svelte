<script lang="ts">
  import { createChatInstance, type IChatInstance } from "../chatinstance";
  import type { ILoaderForm } from "../common/chatbotInterfaces";
  import type { NotebookCommModel } from "../dataAPI/NotebookCommModel";
  import AutoCompleteInput from "./chat/AutoCompleteInput.svelte";
  import Chat from "./chat/Chat.svelte";
  import Header from './header/Header.svelte';
  import IconButton from "./generic/IconButton.svelte";
  import { wizardOpenChatInstance } from "../stores";
  import {onDestroy} from "svelte";
  import InstanceForm from "./header/InstanceForm.svelte";

  export let model: NotebookCommModel;

  const chatInstances = model.chatInstances;
  const chatLoaders = model.chatLoaders;
  let chatInstance: IChatInstance | null = null;
  let instanceName: string | null;
  let mode: string = "";
  let newForm: ILoaderForm | null = null;

  function deselectEverything() {
    instanceName = null;
    deselectChatInstance();
    newForm = null;
  }

  function refreshLoaders() {
    model.refresh();
  }

  function deselectChatInstance(){
    if(chatInstance != null)
      $wizardOpenChatInstance[chatInstance.chatName] -= 1; 
    chatInstance = null;
  }

  onDestroy(()=>{
    deselectChatInstance();
  });

  function selectExisting(key: string) {
    mode = "existing:" + key;
    instanceName = key;
    deselectChatInstance();
    chatInstance = $chatInstances[key]
    if (chatInstance) {
      if($wizardOpenChatInstance[chatInstance.chatName] == undefined)
      {
        $wizardOpenChatInstance[chatInstance.chatName] = 0;
      }
      $wizardOpenChatInstance[chatInstance.chatName] += 1;
      chatInstance.refresh();
      $chatInstance = $chatInstance;
    }
    newForm = null;
  }

  function selectMode() {
    if (mode.startsWith("existing:")) {
      selectExisting(mode.substring("existing:".length));
      newForm = null;
    } else if (mode.startsWith("new:")) {
      instanceName = null;
      deselectChatInstance();
      newForm = $chatLoaders[mode.substring("new:".length)] || {};

    } else {
      deselectEverything();
    }
  }

  function createInstance(event: CustomEvent<{data: { [id: string]: string | null }}>) {
    let newKey = crypto.randomUUID();
    let newMode = mode.substring("new:".length);
    $chatInstances[newKey] = createChatInstance(model, newKey, newMode, newForm || {}, event.detail.data);
    model.sendCreateInstance(newKey, newMode, event.detail.data);
    selectExisting(newKey);
  }

  function removeInstance() {
    if ((instanceName !== null) && confirm(`Do you want to remove ${instanceName}?`)) {
      model.sendRemoveInstance(instanceName)
    }
  }

  chatInstances.subscribe((newValue) => {
    if ((instanceName !== null) && !(instanceName in newValue)) {
      deselectEverything();
      mode = "";
    }
  })

  chatLoaders.subscribe((newValue) => {
    if (mode.startsWith("new:")) {
      const loader = mode.substring("new:".length);
      if (!(loader in newValue)) {
        deselectEverything();
        mode = "";
      }
    }
  })


</script>

<div class="panel wizardPanel">
  <div class="selector">
    <label>
      Chat mode:
      <select bind:value={mode} on:change={selectMode}>
        {#each Object.entries($chatInstances) as [key, instance] }
          <option value="existing:{key}">Existing: {instance.mode} ({key})</option>
        {/each}
        {#each Object.keys($chatLoaders) as loader }
          <option value="new:{loader}">Create: {loader}</option>
        {/each}
      </select>
    </label>
    <IconButton
      title="Refresh"
      on:click={refreshLoaders}>↻</IconButton>

    {#if chatInstance && (mode !== 'existing:base')}
      <IconButton
        title="Remove"
        on:click={removeInstance}>❌</IconButton>
    {/if}
  </div>

  {#if newForm }
    <InstanceForm form={newForm} on:save={createInstance}/>
  {/if}

  {#if chatInstance}
    {#key chatInstance}
    <Header {chatInstance} title="{chatInstance.mode} - {model.name }" showConfigs={false}/>
    {/key}
    <Chat {chatInstance} isExtraChat={true}/>
    <AutoCompleteInput {chatInstance} isExtraChat={true}/>
  {/if}
</div>

<style>
  .panel {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .selector {
    padding: 1em;
    display: flex;
    flex-wrap: wrap;
  }

  label {
    display: flex;
    box-sizing: border-box;
  }


</style>