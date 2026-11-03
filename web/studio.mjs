import {EXPRESSIONS, sourceRect} from './atlas.mjs';
import {sampleMotion, DURATION} from './motion.mjs';
const $ = id => document.getElementById(id);
const poses = ['open arms', 'peace sign', 'cheeky hands', 'celebration', 'hands on hips', 'gasp'];
const image = new Image();
let expression = 'happy', time = 0, playing = false, last = null, ready = false;
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
function draw(canvas, seconds) {
  const ctx = canvas.getContext('2d'), size = canvas.width;
  ctx.clearRect(0,0,size,size);
  if ($('background').value !== 'transparent') {ctx.fillStyle=$('background').value;ctx.fillRect(0,0,size,size);}
  const rect=sourceRect(image.naturalWidth,image.naturalHeight,expression);
  const p=sampleMotion($('motion').value,seconds), scale=size/768;
  ctx.save();ctx.translate(size/2+p.x*scale,size*.87+p.y*scale);
  ctx.rotate(p.angle);ctx.scale(p.sx*($('flip').checked?-1:1),p.sy);
  const width=size*.67;
  ctx.drawImage(image,rect.x,rect.y,rect.width,rect.height,-width/2,-width,width,width);
  ctx.restore();
}
function render() {if(ready)draw($('stage'),time);$('time').value=time;$('time-label').value=`${time.toFixed(2)}s`;}
function setPlaying(value) {playing=value;last=null;$('play').textContent=value?'Pause':'Play';}
for (const [i,e] of EXPRESSIONS.entries()) {
  const b=document.createElement('button');b.textContent=e[0].toUpperCase()+e.slice(1);b.setAttribute('aria-pressed',e===expression);
  b.addEventListener('click',()=>{expression=e;for(const button of $('expressions').children)button.setAttribute('aria-pressed',button===b);$('pose-label').textContent=`${e} / ${poses[i]}`;render();});$('expressions').append(b);
}
$('play').onclick=()=>setPlaying(!playing);
$('time').oninput=()=>{setPlaying(false);time=Number($('time').value);render();};
for (const id of ['motion','flip','background']) $(id).onchange=render;
reduced.addEventListener('change',event=>{if(event.matches)setPlaying(false);});
function tick(now) {if(playing){if(last!==null)time=(time+(now-last)/1000*Number($('speed').value))%DURATION;last=now;render();}requestAnimationFrame(tick);}
async function save(canvas,name) {
  const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
  if(!blob)throw Error('PNG encoding failed');download(blob,name);
}
function download(blob,name) {const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('png').onclick=()=>save($('stage'),`suki-${expression}-${$('motion').value}.png`).catch(report);
function report(error){$('status').textContent=error.message;}
$('sheet').onclick=async()=>{
  $('sheet').disabled=true;
  try {
    const sheet=document.createElement('canvas');sheet.width=512*8;sheet.height=512*6;
    const cell=document.createElement('canvas');cell.width=cell.height=512;
    const ctx=sheet.getContext('2d');
    for(let i=0;i<48;i++){draw(cell,i/24);ctx.drawImage(cell,(i%8)*512,Math.floor(i/8)*512);}
    const name=`suki-${expression}-${$('motion').value}`;
    await save(sheet,`${name}.png`);
    download(new Blob([JSON.stringify({image:`${name}.png`,expression,pose:poses[EXPRESSIONS.indexOf(expression)],clip:$('motion').value,frameWidth:512,frameHeight:512,columns:8,rows:6,frames:48,fps:24,duration:DURATION,loop:true,flipped:$('flip').checked,background:$('background').value},null,2)],{type:'application/json'}),`${name}.json`);
    $('status').textContent='Exported PNG sheet and JSON manifest. Playback speed changes preview only.';
  }catch(error){report(error);}finally{$('sheet').disabled=false;}
};
try {image.src='assets/artwork/suki-expressions-atlas.png';await image.decode();sourceRect(image.naturalWidth,image.naturalHeight,expression);ready=true;for(const id of ['play','png','sheet'])$(id).disabled=false;$('status').textContent='Ready. Exports use the same motion as the preview.';render();setPlaying(!reduced.matches);requestAnimationFrame(tick);}catch(error){report(error);}
