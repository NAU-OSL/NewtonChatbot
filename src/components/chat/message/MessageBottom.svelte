<script lang="ts">
  import type { IChatInstance } from "../../../chatinstance";
  import type { IChatMessage } from "../../../common/chatbotInterfaces";
  import { sendMessageToBuild, sendMessageToWizardInput, sendMessageToUser, selectChatGPTResponse, sendChatGPTRequest } from "../../../common/messages";
  import { wizardMode } from "../../../stores";
  import IconButton from "../../generic/IconButton.svelte";
  import FeedbackButtons from "./FeedbackButtons.svelte";
  import FeedbackForm from "./FeedbackForm.svelte";
  import Profile from "./Profile.svelte";
  import ReplyButtons from "./ReplyButtons.svelte";
  import Digging from "../../icons/fa-digging.svelte";
  import Save from "../../icons/fa-save.svelte";
  import Title from "../../icons/title.svelte";
  import ChatIcon from "../../icons/chaticon.svelte";
  import Robot from "../../icons/fa-robot.svelte";

  export let chatInstance: IChatInstance;
  export let message: IChatMessage;
  export let index: number;
  export let viewReplied: boolean;
  export let isExtraChat: boolean = false;

  let { showTime, showIndex, directSendToUser } = chatInstance.config;
  let timestamp = message.timestamp;
  if (!Number.isInteger(timestamp)) {
    timestamp = timestamp * 1000;
  }

  async function sendToBuild() {
    await sendMessageToBuild(chatInstance, message, false);
  }

  async function sentToInput() {
    await sendMessageToWizardInput(chatInstance, message, false);
  }

  async function sendToUser() {
    await sendMessageToUser(chatInstance, message, false);
  }

  async function addToGPTContext(){
    await selectChatGPTResponse(chatInstance, message, false);
  }

  async function sendUserPrompt(){
    await sendChatGPTRequest(chatInstance, message, false);
  }

  function selectMessageAlt(event: Event & { currentTarget: EventTarget & HTMLSelectElement; }) {
    message.text = message.alternatives[message.selectedAlt]
    chatInstance.submitSyncMessage({
      id: message.id,
      text: message.text,
      selectedAlt: message.selectedAlt
    })
  }

  function toggleConversationContext(e: MouseEvent): void {
    message.inConversationContext = !message.inConversationContext 
    chatInstance.submitSyncMessage({
      id: message.id,
      inConversationContext: message.inConversationContext,
    })
  }
</script>

<div class="bottom {message.type}">
  <div class="first">
    <Profile type={message.type} title={message.type == "user" ? "You" : chatInstance.mode}/>
    {#if $showIndex && $wizardMode}
      <div>{index}</div>
    {/if}
    <ReplyButtons {chatInstance} {message} viewReplied={viewReplied} on:toggleViewReplied />
    {#if $wizardMode}
      <IconButton title="To reply" on:click={sendToBuild}><Digging/></IconButton>
      <IconButton title="To input" on:click={sentToInput}><Title/></IconButton>
      {#if $directSendToUser}
        <IconButton title="To user" on:click={sendToUser}><ChatIcon/></IconButton>
      {/if}
      {#if !isExtraChat && message.type != 'user' && !message.inConversationContext}
        <IconButton title="add to GPT context" on:click={addToGPTContext}><Save/></IconButton>
      {/if}
      {#if !isExtraChat && message.type == 'user'}
        <IconButton title="send user prompt" on:click={sendUserPrompt}><Save/></IconButton>
      {/if}
    {/if}
    {#if message.loading}
      <div class="loading" title="Processing message">⌛️</div>
    {/if}
  </div>

  <div class="last">
    {#if message.type !== 'user'}
      <FeedbackButtons {chatInstance} {message}/>
    {/if}
    {#if $showTime}
      <span class="timestamp">{ new Date(timestamp).toLocaleTimeString("en-US") }</span>
    {/if}
    {#if message.alternatives.length > 0}
      <select bind:value={message.selectedAlt} on:change={selectMessageAlt}>
        {#each message.alternatives as _, i (i) }
          <option value={i}>{i + 1}</option>
        {/each}
      </select>
    {/if}
    {#if $wizardMode && isExtraChat}
      {#key message.inConversationContext }
        <IconButton 
        title={message.inConversationContext? "Remove from Conversation Context" : "Add to Conversation Context"}
        selected={message.inConversationContext} 
        on:click={toggleConversationContext}
      ><Robot/></IconButton>
      {/key}
    {/if}
  </div>
</div>
<FeedbackForm {chatInstance} {message}/>

<style>
  .bottom {
    height: 25px;
    border-top: 1px solid black;
    display: flex;
    justify-content: space-between;
    flex-direction: row;
  }

  .first {
    display: flex;
    flex-direction: row;
  }

  .first > :global(div) {
    height: 25px;
    min-width: 25px;
    text-align: center;
    display: flex;
       
    align-items: center;
    justify-content: center;
    
  }

  .last {
    font-size: 0.8em;
    padding: 0.3em;
    display: flex;
  }

  .last span {
    align-self: flex-end;
  }

  .user .timestamp {
    text-align: right;
  }

  div.user, .user .first {
    flex-direction: row-reverse;
  }
</style>