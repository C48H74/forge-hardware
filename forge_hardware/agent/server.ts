/** Versioned, same-origin view protocol used by the embedded App.tsx. */
export type ViewEvent = {type:'forge.ready';version:1;design:string} |
  {type:'forge.selection';version:1;design:string;ref:string};
export type ViewCommand = {type:'forge.select';version:1;ref:string} | {type:'forge.reset';version:1};
export function isViewEvent(data:unknown):data is ViewEvent {
  if(typeof data!=='object'||data===null)return false;
  const d=data as Record<string,unknown>;
  return d.version===1 && typeof d.design==='string' &&
    (d.type==='forge.ready'||(d.type==='forge.selection'&&typeof d.ref==='string'));
}
export function sendViewCommand(frame:HTMLIFrameElement, command:ViewCommand):void {
  const target=new URL(frame.src,location.href);
  if(target.origin!==location.origin)throw Error('Viewer must be same-origin');
  frame.contentWindow?.postMessage(command,target.origin);
}
