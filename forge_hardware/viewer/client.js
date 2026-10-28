import {Viewport} from './runtime.js';
import {translations,language} from './i18n.js';
export async function loadAssets(){let names=['scene.json','manifest.json','refs.json'];return Promise.all(names.map(async n=>{let r=await fetch(n);if(!r.ok)throw Error(`${n}: ${r.status}`);return r.json();}));}
function button(text,fn,cls=''){let b=document.createElement('button');b.textContent=text;b.className=cls;b.onclick=fn;return b;}
async function main(){const [scene,manifest,refs]=await loadAssets();let selection=document.querySelector('#selection'),parts=document.querySelector('#parts');let viewport=new Viewport(document.querySelector('canvas'),scene,pick);
 let locale=language(localStorage.getItem('forge.language'));
 function translate(){const t=translations[locale];document.documentElement.lang=locale;document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t[el.dataset.i18n]);document.querySelector('#language').value=locale;viewport.labels=t;viewport.draw();if(!viewport.selected)selection.textContent=t.select;}
 document.querySelector('#language').onchange=e=>{locale=language(e.target.value);localStorage.setItem('forge.language',locale);translate();};translate();
 function emit(ref){parent.postMessage({type:'forge.selection',version:1,ref,design:scene.name},location.origin);}
 function pick(id){viewport.select(id);selection.textContent=JSON.stringify({ref:id,...refs[id]},null,2);document.querySelectorAll('.part').forEach(b=>b.classList.toggle('selected',b.dataset.id===id));emit(id);}
 document.querySelector('#name').textContent=scene.name;document.querySelector('#params').textContent=JSON.stringify(scene.parameters,null,2);
 for(let p of scene.parts){let b=button(p.id,()=>pick(p.id),'part');b.dataset.id=p.id;parts.append(b);for(let [name,info] of Object.entries(p.features||{}))parts.append(button(`${p.id}/${name}`,()=>{viewport.select(p.id);selection.textContent=JSON.stringify({ref:`${p.id}/${name}`,...info},null,2);emit(`${p.id}/${name}`);},'feature'));}
 let frames=document.querySelector('#flat'),mode=document.querySelector('#mode'),files=Object.keys(manifest.files),flats=files.filter(n=>/^flat-.*\.svg$/.test(n)),robots=files.filter(n=>/\.(urdf|srdf|sdf)$/.test(n));
 mode.onchange=()=>{let list=mode.value==='flat'?flats:robots;frames.style.display=mode.value==='model'?'none':'block';if(mode.value!=='model'){if(list.length)frames.src=list[0];else{frames.removeAttribute('src');selection.textContent=translations[locale].missing;}}};
 let links=document.querySelector('#files');for(let name of files.filter(n=>!/meshes\//.test(n))){let a=document.createElement('a');a.textContent=name;a.href=name;a.target='_blank';links.append(a);}
 document.querySelector('#reset').onclick=()=>{viewport.yaw=-.8;viewport.pitch=.55;viewport.fit();};
 for(let j of scene.robot?.joints||[]){if(j.type==='fixed')continue;let label=document.createElement('label'),input=document.createElement('input'),value=document.createElement('span');label.textContent=j.name+' ';input.type='range';input.min=j.limit.lower??-Math.PI;input.max=j.limit.upper??Math.PI;input.step=.001;input.value=Math.max(+input.min,Math.min(+input.max,0));viewport.values[j.name]=+input.value;input.oninput=()=>{viewport.values[j.name]=+input.value;value.textContent=`${(+input.value).toFixed(3)} ${j.type==='prismatic'?'m':'rad'}`;viewport.draw();};label.append(value,input);document.querySelector('#joints').append(label);input.oninput();}
 if(!scene.robot)document.querySelector('#joint-title').hidden=true;
 window.addEventListener('message',e=>{if(e.origin!==location.origin||e.source!==parent)return;let m=e.data;if(m?.version!==1)return;if(m.type==='forge.select'&&refs[m.ref])pick(m.ref);if(m.type==='forge.reset')viewport.fit();});
 parent.postMessage({type:'forge.ready',version:1,design:scene.name},location.origin);
}
main().catch(e=>{document.querySelector('#name').textContent='Build could not be loaded';document.querySelector('#selection').textContent=e.message;});
