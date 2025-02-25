import { DockLayout, Widget } from '@lumino/widgets';
import type { ComponentType, SvelteComponent } from 'svelte';
import { get } from 'svelte/store';
import { mainChatIcon } from '../iconimports';
import { jupyterapp, panelWidget } from '../stores';

export class SveltePanelView extends Widget {
  private _panel: SvelteComponent;
  private _detached: boolean;
  
  constructor(
    svelteComponent: ComponentType,
    props: Record<string, any>,
  ) {
    super();
    this._detached = false;
    this._panel = new svelteComponent({
      target: this.node,
      props
    });
    
    this._panel.$on('detach', event => {
      panelWidget.set(null);
      this._detached = true;
    })
  }

  set_props(props: Record<string, any>) {
    this._panel.$set(props);
  }


  dispose(): void {
    if (!this._detached) {
      panelWidget.set(null);
    }
    super.dispose();
  }
}

export function openPanel(
  svelteComponent: ComponentType,
  title: string,
  props: Record<string, any>,
  mode: DockLayout.InsertMode
) {
  let panel = new SveltePanelView(svelteComponent, props);
  panel.id = "NewtonChatPanel-" + crypto.randomUUID();

  panel.title.closable = true;
  panel.title.label = title;
  panel.title.icon = mainChatIcon.bindprops({ stylesheet: 'mainAreaTab' });
  const app = get(jupyterapp);
  if (app) {
    app.shell.add(panel, 'main', { mode })
  }
  return panel;
}
