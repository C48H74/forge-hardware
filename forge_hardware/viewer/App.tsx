/** Optional React host for embedding the same offline viewer in an agent UI.
 * Serve host and viewer on the same origin. No hosted backend is required.
 */
import React, {useEffect, useRef} from 'react';
import {isViewEvent, type ViewEvent} from '../agent/server';
export function App({src, onSelection}:{src:string;onSelection?:(ref:string)=>void}) {
  const frame=useRef<HTMLIFrameElement>(null);
  useEffect(()=>{
    const receive=(event:MessageEvent)=>{
      if(event.origin!==location.origin || event.source!==frame.current?.contentWindow || !isViewEvent(event.data))return;
      const message:ViewEvent=event.data;
      if(message.type==='forge.selection')onSelection?.(message.ref);
    };
    window.addEventListener('message',receive);
    return ()=>window.removeEventListener('message',receive);
  },[onSelection]);
  const target=new URL(src,location.href);
  if(target.origin!==location.origin)throw new Error('Use a same-origin local viewer');
  return <iframe ref={frame} src={target.href} title="Forge Hardware geometry review" style={{border:0,width:'100%',height:'100%'}}/>;
}
