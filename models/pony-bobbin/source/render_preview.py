#!/usr/bin/env python3
"""Screenshot two WebGL views of the exported STL (no generated artwork)."""

import json
from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright
import trimesh

MODEL_DIR = Path(__file__).resolve().parents[1]
mesh = trimesh.load_mesh(MODEL_DIR / "exports/pony-bobbin-65x25x1mm.stl")
payload = json.dumps({
    "positions": mesh.triangles.reshape(-1).tolist(),
    "normals": mesh.face_normals.repeat(3, axis=0).reshape(-1).tolist(),
})

html = r'''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;background:#eeefeb;color:#25303a;font-family:Arial,sans-serif}
main{padding:40px 48px;width:1600px;height:1000px}
header{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:24px}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:2px;color:#6c7478;margin-bottom:10px}
h1{font-size:35px;font-weight:600;letter-spacing:-1px;margin:0}
.subtitle{font-size:15px;color:#647075;line-height:1.6;text-align:right}
.views{display:grid;grid-template-columns:1fr 1fr;gap:22px;height:704px}
.view{position:relative;background:#fafaf7;border:1px solid #d8ded7;border-radius:12px;overflow:hidden}
.label{position:absolute;top:22px;left:24px;font-size:14px;font-weight:600;z-index:1}
.label span{display:block;font-size:12px;color:#7a827c;margin-top:6px;font-weight:400}
canvas{display:block;width:740px;height:704px}
.viewnote{position:absolute;bottom:20px;left:24px;font-size:12px;color:#657069}
footer{display:flex;align-items:center;justify-content:space-between;margin-top:24px}
.metrics{display:flex;gap:35px}.metric{font-size:12px;color:#657069}.metric b{display:block;color:#263630;font-size:23px;margin-bottom:5px;font-weight:600}
.note{font-size:13px;color:#53635a;text-align:right;line-height:1.65}
</style></head><body><main>
<header><div><div class="eyebrow">3D MODEL PREVIEW</div><h1>Pony-style yarn bobbin</h1></div>
<div class="subtitle">Simplified from the P60624 reference<br>Rendered from the exported STL · millimetres</div></header>
<section class="views">
<div class="view"><div class="label">TOP VIEW<span>Long edges parallel to Y</span></div><canvas id="top"></canvas><div class="viewnote">The slit connects the rounded opening to the outside.</div></div>
<div class="view"><div class="label">3D VIEW<span>Flat on the print bed · Z = 0</span></div><canvas id="angled"></canvas><div class="viewnote">One continuous solid · no supports</div></div>
</section><footer><div class="metrics">
<div class="metric"><b>65 mm</b>LENGTH</div><div class="metric"><b>25 mm</b>WIDTH</div>
<div class="metric"><b>1 mm</b>THICKNESS</div><div class="metric"><b>0.6 mm</b>OPEN SLIT</div>
</div><div class="note">Sized for a first test print<br>Editable source included</div></footer>
</main><script>
const data=__MESH__;
const normalize=a=>{const n=Math.hypot(...a);return a.map(x=>x/n)},
cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],
dot=(a,b)=>a.reduce((n,x,i)=>n+x*b[i],0);
function render(id,eye){
  const canvas=document.getElementById(id);canvas.width=1480;canvas.height=1408;
  const gl=canvas.getContext('webgl',{antialias:true,preserveDrawingBuffer:true});
  if(!gl)throw new Error('WebGL unavailable');
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
  const vs=shader(gl.VERTEX_SHADER,`
    attribute vec3 position;attribute vec3 normal;
    uniform vec3 center,right,up,forward;uniform float scale,aspect;
    varying vec3 n;
    void main(){vec3 p=position-center;gl_Position=vec4(dot(p,right)/scale/aspect,dot(p,up)/scale,-dot(p,forward)/250.0,1.0);n=normal;}
  `);
  const fs=shader(gl.FRAGMENT_SHADER,`
    precision highp float;varying vec3 n;uniform vec3 color;uniform float unlit;
    void main(){float light=0.46+0.54*max(dot(normalize(n),normalize(vec3(-0.5,0.65,1.4))),0.0);gl_FragColor=vec4(color*mix(light,1.0,unlit),1.0);}
  `);
  const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);gl.useProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));
  const center=[12.5,32.5,0.5],forward=normalize(eye.map((x,i)=>x-center[i])),right=normalize(cross([0,1,0],forward)),up=cross(forward,right);
  for(const [name,value] of Object.entries({center,right,up,forward}))gl.uniform3fv(gl.getUniformLocation(program,name),value);
  gl.uniform1f(gl.getUniformLocation(program,'scale'),41);
  gl.uniform1f(gl.getUniformLocation(program,'aspect'),canvas.width/canvas.height);
  const locations={};
  for(const name of ['position','normal']){locations[name]=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(locations[name]);}
  function buffer(name,values){const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values),gl.STATIC_DRAW);gl.vertexAttribPointer(locations[name],3,gl.FLOAT,false,0,0);}
  gl.clearColor(0.9804,0.9804,0.9686,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);
  const grid=[];
  for(let x=-60;x<=85;x+=5)grid.push(x,-45,-0.06,x,110,-0.06);
  for(let y=-45;y<=110;y+=5)grid.push(-60,y,-0.06,85,y,-0.06);
  buffer('position',grid);buffer('normal',grid.map((_,i)=>i%3===2?1:0));
  gl.uniform3fv(gl.getUniformLocation(program,'color'),[0.891,0.910,0.885]);gl.uniform1f(gl.getUniformLocation(program,'unlit'),1);
  gl.drawArrays(gl.LINES,0,grid.length/3);
  buffer('position',data.positions);buffer('normal',data.normals);
  gl.uniform3fv(gl.getUniformLocation(program,'color'),[0.215,0.360,0.755]);gl.uniform1f(gl.getUniformLocation(program,'unlit'),0);
  gl.drawArrays(gl.TRIANGLES,0,data.positions.length/3);gl.finish();
}
render('top',[12.5,32.5,150]);render('angled',[95,-8,130]);window.previewReady=true;
</script></body></html>'''.replace("__MESH__", payload)

browser_path = shutil.which("chromium") or shutil.which("google-chrome")
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=browser_path, headless=True, args=[
        "--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle",
        "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
    ])
    page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
    page.set_content(html)
    page.wait_for_function("window.previewReady === true")
    page.screenshot(path=str(MODEL_DIR / "preview.png"))
    browser.close()
print(MODEL_DIR / "preview.png")
