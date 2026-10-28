import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const runtime=await readFile(new URL('../forge_hardware/viewer/runtime.js',import.meta.url),'utf8');
const {kinematics,point}=await import('data:text/javascript;base64,'+Buffer.from(runtime).toString('base64'));
const robot={links:{base:{},arm:{},tip:{}},joints:[
 {name:'shoulder',type:'revolute',parent:'base',child:'arm',xyz:[0,0,.03],rpy:[0,0,0],axis:[0,0,1]},
 {name:'slide',type:'prismatic',parent:'arm',child:'tip',xyz:[.16,0,0],rpy:[0,0,0],axis:[1,0,0]}
]};
function close(actual,expected){actual.forEach((v,i)=>assert.ok(Math.abs(v-expected[i])<1e-8,`${actual} != ${expected}`));}
let fk=kinematics(robot,{shoulder:Math.PI/2,slide:.02});
close(point(fk.tip,[0,0,0]),[0,180,30]);
close(point(fk.arm,[160,0,0]),[0,160,30]);
close(point(kinematics(robot,{}).tip,[0,0,0]),[160,0,30]);
const tilted={links:{base:{},arm:{}},joints:[{name:'tilt',type:'fixed',parent:'base',child:'arm',xyz:[.1,.2,.3],rpy:[Math.PI/2,0,0]}]};
close(point(kinematics(tilted).arm,[0,10,0]),[100,200,310]);
assert.deepEqual(kinematics(null),{});
for(const name of ['runtime.js','client.js']){
 const source=await readFile(new URL('../forge_hardware/viewer/'+name,import.meta.url),'utf8');
 assert.ok(!source.includes('https://'),'Offline runtime must not use CDN assets');
}
console.log('Viewer kinematics: 5 checks passed; local asset check passed.');
const {rasterize}=await import('data:text/javascript;base64,'+Buffer.from(runtime).toString('base64'));
const near={id:'near',color:'#ff0000',pts:[[0,0,5],[8,0,5],[0,8,5]]},far={id:'far',color:'#0000ff',pts:[[0,0,0],[8,0,0],[0,8,0]]};
for(const order of [[near,far],[far,near]]){let r=rasterize(order,10,10);assert.equal(r.ids[r.parts[11]],'near');assert.deepEqual([...r.pixels.slice(44,48)],[255,0,0,255]);}
const i18n=await readFile(new URL('../forge_hardware/viewer/i18n.js',import.meta.url),'utf8');
const {translations,language}=await import('data:text/javascript;base64,'+Buffer.from(i18n).toString('base64'));
assert.equal(language('xx'),'en');assert.deepEqual(Object.keys(translations.en).sort(),Object.keys(translations.pt).sort());assert.deepEqual(Object.keys(translations.en).sort(),Object.keys(translations.es).sort());
console.log('Depth occlusion and English/Portuguese/Spanish parity checks passed.');
