import { get, writable, type Writable } from "svelte/store";
import { MessageDisplay, type IAutoCompleteItem, type IChatMessage, type IConfigVar, type Subset, type ILoaderForm } from "./common/chatbotInterfaces";
import { checkTarget, cloneMessage, messageTarget } from "./common/messages";
import type { NotebookCommModel } from "./dataAPI/NotebookCommModel";
import { wizardMode, wizardPreviewMessage } from "./stores";

export function createChatInstance(model: NotebookCommModel, chatName: string, mode: string, loader: ILoaderForm, botlConfig: { [id: string]: string | null }) {
    let current: IChatMessage[] = [];
    let autoCompleteResponseId = writable(-1);
    let replying: Writable<string | null> = writable(null);
    let autoCompleteItems: Writable<IAutoCompleteItem[]> = writable<IAutoCompleteItem[]>([]);
    let configMap: { [id: string]: IConfigVar<any>} = {};
    let botLoader: Writable<ILoaderForm> = writable<ILoaderForm>(loader);
    let botConfig: Writable<{ [id: string]: string | null }> = writable(botlConfig);
  
    function createConfigVar<T>(name: string, value: T) {
      let { subscribe, set, update } = writable(value);
      let configVar = { subscribe, set, update, load: (_v: T) => {}, initialized: false };
      configVar.set = (new_value: T) => {
        model.sendConfig(chatName, { 
          key: name, 
          value: new_value, 
          _mode: configVar.initialized? 'update': 'init'
        })
        return set(value);
      }
      configVar.load = (new_value: any) => {
        set(new_value);
      }
      configMap[name] = configVar;
      return configVar;
    }
  
    let config = {
      processInKernel: createConfigVar("process_in_kernel", true),
      enableAutoComplete: createConfigVar("enable_autocomplete", true),
      enableAutoLoading: createConfigVar("enable_auto_loading", false),
      loading: createConfigVar("loading", false),
      processBaseChatMessage: createConfigVar("process_base_chat_message", true),
  
      showReplied: createConfigVar("show_replied", false),
      showIndex: createConfigVar("show_index", false),
      showTime: createConfigVar("show_time", true),
      showBuildMessages: createConfigVar("show_build_messages", true),
      showKernelMessages: createConfigVar("show_kernel_messages", true),
      showMetadata: createConfigVar("show_metadata", false),
      directSendToUser: createConfigVar("direct_send_to_user", false),
    }
  
    let messageMap: { [key: string]: { position: number, message: IChatMessage} } = {};
    const { subscribe, set, update } = writable(current);
  
    function push(newMessage: IChatMessage) {
      newMessage.new = true;
      messageMap[newMessage['id']] = { position: current.length, message: newMessage };
      current.push(newMessage);
      
      set(current);
      if ((get(wizardMode) != (newMessage.type != 'user')) && !['kernel', 'build'].includes(checkTarget(newMessage))) {
        replying.set(newMessage['id']);
      }
      if (newMessage.display == MessageDisplay.WizardModeInput) {
        let buildMessage = cloneMessage(newMessage, messageTarget('user'))
        wizardPreviewMessage.set([...get(wizardPreviewMessage), buildMessage]);
      }
    }
  
    function addNew(newMessage: IChatMessage) {
      if (get(wizardMode) && get(config.enableAutoLoading) && get(replying) === newMessage.reply && (newMessage.reply != null)) {
        removeLoading(newMessage.reply);
      }
      model.sendMessageKernel(chatName, newMessage);
    }
  
    function load(data: IChatMessage[]) {
      current = data;
      messageMap = {};
      current.forEach((message, index) => {
        messageMap[message['id']] = { position: index, message: message };
      });
      const lastMessage = data[data.length - 1];
      if ((get(wizardMode) != (lastMessage.type != 'user')) && !['kernel', 'build'].includes(checkTarget(lastMessage))) {
        replying.set(lastMessage['id']);
      }
      set(current);
    }
  
    function updateMessage(message: IChatMessage) {
      let { position } = messageMap[message['id']];
      current[position] = message;
      messageMap[message['id']] = { position, message };
      set(current);
    }
  
    function submitSyncMessage(message: Pick<IChatMessage, 'id'> & Subset<IChatMessage>) {
      model.sendSyncMessage(chatName, message);
    }
  
    function removeLoading(messageId: string) {
      submitSyncMessage({
        id: messageId,
        loading: false
      })
    }
  
    function reset() {
      current = [];
      messageMap = {};
      autoCompleteResponseId.set(-1);
      autoCompleteItems.set([]);
      set(current);
    }
  
    function findById(messageId: string | null) {
      if (messageId === null) {
        return null;
      }
      let message = messageMap[messageId];
      if (message === undefined) {
        return null;
      }
      return message.message;
    }
  
    function sendAutoComplete(requestId: number, query: string) {
      model.sendAutoCompleteQuery(chatName, requestId, query);
    }

    function sendUpdateInstanceBot(data: { [id: string]: string | null }) {
      model.sendUpdateInstanceBot(chatName, data);
    }
  
    function refresh() {
      console.log("refresh", chatName)
      model.sendRefreshInstance(chatName);
    }
  
    return {
      chatName,
      mode,
      subscribe,
      set,
      update,
      push,
      addNew,
      load,
      submitSyncMessage,
      updateMessage,
      removeLoading,
      reset,
      findById,
      sendAutoComplete,
      sendUpdateInstanceBot,
      refresh,

      model,
  
      configMap,
      config,
      autoCompleteResponseId,
      autoCompleteItems,
      replying,

      botLoader,
      botConfig
    };
  }

  export type IChatInstance = ReturnType<typeof createChatInstance>;