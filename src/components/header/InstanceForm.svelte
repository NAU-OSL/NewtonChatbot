<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { ILoaderForm } from "../../common/chatbotInterfaces";
  import DynamicInput from "../jsonform/DynamicInput.svelte";
  import { writable, type Writable } from "svelte/store";

  const dispatch = createEventDispatcher<{save: {data: { [id: string]: string | null }}}>();
  
  export let form: ILoaderForm;
  export let buttonLabel: string = "Create";
  export let custom: Writable<{ [id: string]: string | null }> = writable({});

  let formValues: { [id: string]: {
    type: string,
    value: any
  } } = {};

  for (const [key, [type_, config]] of Object.entries(form)) {
    formValues[key] = {type: type_, value: $custom[key] ?? config.value ?? null};
  }

  custom.subscribe((data) => {
    for (const [key, value] of Object.entries(data)) {
      formValues[key].value = value ?? formValues[key].value; 
    }
  })

  function save(event: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement; }) {
    let data: { [id: string]: string | null } = {};
    for (const [key, { value }] of Object.entries(formValues)) {
      data[key] = value;
    }
    dispatch('save', { data });
  }
</script>

<form>
  {#each Object.entries(form) as [key, [type, config]] (key)}
    <DynamicInput {key} {type} {config} bind:value={formValues[key].value}/>
  {/each}
  <button on:click|preventDefault={save}>{buttonLabel}</button>
</form>

<style>
  form {
    padding: 0 1em;
    display: flex;
    flex-direction: column;
    gap: 15px;
    justify-content: center;
    margin: auto;
    overflow: auto;
  }

  button {
    cursor: pointer;
  }
</style>