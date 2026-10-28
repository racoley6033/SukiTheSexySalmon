"""Deterministic layered SVG mascot, PNG stickers and animated social exports."""
import argparse, io, json, math, subprocess
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
EXPRESSIONS = tuple(json.loads((ROOT/'character.json').read_text())['expressions'])

def svg(expression='happy', phase=0, motion='idle'):
    """Layered vector interpretation of the supplied Sally character sheet."""
    if expression not in EXPRESSIONS: raise ValueError(expression)
    bob=5*math.sin(phase*math.tau)
    tilt=5*math.sin(phase*math.tau) if motion=='dance' else 0
    arm=-22*math.sin(phase*math.tau) if motion=='wave' else 0
    def eye(x, side):
        closed=expression in ('flirty','excited','sleepy') or (expression=='wink' and side==1)
        if closed:
            return f'<g transform="translate({x} 248)"><path d="M-30 4 Q0 -23 28 1 M-23 -1 l-12 -12 M-13 -7 l-8 -15 M-2 -9 l-3 -16" stroke="#191a18" stroke-width="6" stroke-linecap="round" fill="none"/></g>'
        if expression=='love':
            return f'<path d="M{x} 275 C{x-60} 242 {x-25} 207 {x} 236 C{x+25} 207 {x+60} 242 {x} 275" fill="#d94355"/>'
        lid='M-32 -3 Q-4 -16 31 -5' if expression=='sassy' else 'M-32 3 Q-29 -43 1 -43 Q25 -39 31 -4'
        return f'''<g transform="translate({x} 247) rotate({side*7})"><path d="M-32 3 Q-30 -42 1 -42 Q31 -38 32 20 Q-3 36 -32 3" fill="#fff9e7"/>
<ellipse cx="3" cy="-1" rx="23" ry="30" fill="url(#iris)"/><ellipse cx="5" cy="0" rx="12" ry="22" fill="#101d0e"/><path d="M-10 10 l-4 8 M-1 16 v9 M12 13 l6 7" stroke="#bbd86c" stroke-width="2" opacity=".8"/><circle cx="-5" cy="-15" r="9" fill="white"/><circle cx="13" cy="10" r="4" fill="#edfcca"/>
<path d="{lid}" fill="none" stroke="#171916" stroke-width="7" stroke-linecap="round"/><path d="M-27 -19 q-16 -3 -18 -16 M-19 -32 q-13 -8 -12 -19 M-6 -40 q-8 -10 -6 -19" stroke="#171916" stroke-width="6" fill="none" stroke-linecap="round"/>
{'<path d="M-32 -3 Q-7 -24 31 -5 L28 -33 L-19 -38Z" fill="#ffb775"/>' if expression=='sassy' else ''}</g>'''
    if expression=='surprised': mouth='<ellipse cx="260" cy="299" rx="15" ry="22" fill="#7e1e19"/><ellipse cx="262" cy="312" rx="9" ry="7" fill="#f87779"/>'
    elif expression in ('sad','angry','sleepy','sassy','flirty'):
        d={'sad':'M239 309 Q258 292 280 308','angry':'M238 307 Q258 299 278 307','sleepy':'M247 305 L268 305','sassy':'M236 300 Q260 316 282 291','flirty':'M246 296 Q265 310 276 292'}[expression]
        mouth=f'<path d="{d}" stroke="#993620" stroke-width="4" fill="none" stroke-linecap="round"/>'
    else:
        mouth='<path d="M229 285 Q255 298 289 283 Q282 331 258 329 Q236 322 229 285" fill="#8e201e" stroke="#b53c27" stroke-width="2"/><path d="M232 287 Q258 299 286 286 L281 297 Q256 308 236 296Z" fill="#fff9e8"/><path d="M248 317 Q264 304 277 315 Q267 335 252 324Z" fill="#ff737d"/>'
    rice=[]
    for row in range(4):
        for j in range(11):
            x=157+j*19+(row%2)*8; y=326+row*12
            if ((x-256)/110)**2+((y-333)/36)**2<1.1:
                rice.append(f'<ellipse cx="{x}" cy="{y}" rx="12" ry="9" transform="rotate({(j*31+row*19)%70-35} {x} {y})" fill="url(#rice)" stroke="#e6ceab" stroke-width=".7"/>')
    marbling=''.join(f'<path d="M{150+i*34} 172 Q{187+i*26} 149 {220+i*22} 141"/>' for i in range(5))
    brows='<path d="M188 202 l34 9 M291 210 l32 -12" stroke="#a54420" stroke-width="5" fill="none"/>' if expression=='angry' else '<path d="M187 204 Q200 190 216 199 M294 199 Q310 189 322 204" stroke="#b64e25" stroke-width="5" stroke-linecap="round" fill="none"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Sally {expression}">
<defs>
<radialGradient id="salmon" cx="35%" cy="20%" r="85%"><stop stop-color="#ffb365"/><stop offset=".55" stop-color="#ff7838"/><stop offset="1" stop-color="#d74724"/></radialGradient>
<radialGradient id="skin" cx="45%" cy="35%" r="70%"><stop stop-color="#ffe4b2"/><stop offset=".7" stop-color="#ffc184"/><stop offset="1" stop-color="#f78e61"/></radialGradient>
<radialGradient id="iris" cx="45%" cy="75%"><stop stop-color="#c7eb58"/><stop offset=".6" stop-color="#6a9b27"/><stop offset="1" stop-color="#263814"/></radialGradient>
<radialGradient id="rice" cx="35%" cy="25%"><stop stop-color="#fffef7"/><stop offset=".65" stop-color="#f8ecd7"/><stop offset="1" stop-color="#d9bc9e"/></radialGradient>
<linearGradient id="nori" x1="0" x2="1" y2="1"><stop stop-color="#101610"/><stop offset=".35" stop-color="#3d4739"/><stop offset=".55" stop-color="#121a13"/><stop offset="1" stop-color="#030905"/></linearGradient>
<linearGradient id="avo" x2="1" y2=".5"><stop stop-color="#81a02b"/><stop offset=".2" stop-color="#dbea7c"/><stop offset=".7" stop-color="#dfec8b"/><stop offset="1" stop-color="#9ec24c"/></linearGradient>
<radialGradient id="cheek"><stop stop-color="#fa6c62" stop-opacity=".85"/><stop offset="1" stop-color="#fa6c62" stop-opacity="0"/></radialGradient>
</defs>
<g id="character" transform="translate(0 {bob:.3f}) rotate({tilt:.3f} 256 280)">
<g id="nori-legs" stroke="#0c160d" stroke-linecap="round" fill="url(#nori)"><path d="M225 348 Q224 379 210 407 L192 412 L199 397 L202 354Z" stroke-width="3"/><path d="M282 350 L301 399 L299 416 L279 417 L265 353Z" stroke-width="3"/></g>
<g id="boots" fill="url(#nori)" stroke="#10170e" stroke-width="3"><path d="M190 397 Q201 403 218 399 L220 423 Q231 434 224 447 Q205 460 170 451 Q156 437 174 425Z"/><path d="M277 398 Q289 402 303 397 L309 422 Q337 424 342 443 Q333 457 280 453 Q268 442 277 424Z"/><path d="M170 447 Q196 456 225 444 M279 448 Q313 455 339 443" stroke="#62644b" stroke-width="3"/><path d="M182 423 q7 -13 17 -11 M300 428 q15 -1 22 7" stroke="#afb49d" stroke-width="4" fill="none" stroke-linecap="round"/></g>
<g id="salmon-back"><path d="M135 286 Q107 259 126 209 Q116 153 178 128 Q225 97 287 114 Q357 112 379 179 Q402 221 381 261 Q398 300 362 321 Q332 342 300 330 L182 331 Q145 334 135 286Z" fill="url(#salmon)" stroke="#db6336" stroke-width="2"/>
<path d="M145 215 Q130 260 161 296 M154 185 Q138 231 175 276 M354 177 Q379 225 355 269 M370 219 Q389 267 363 303" fill="none" stroke="#ffc58b" stroke-width="6" stroke-linecap="round"/></g>
<g id="rice-collar"><ellipse cx="256" cy="334" rx="106" ry="33" fill="#e8d0ad"/>{''.join(rice)}</g>
<g id="peach-face"><path d="M163 209 Q180 158 246 167 Q323 159 350 221 L345 272 Q329 329 259 331 Q191 333 167 287Z" fill="url(#skin)"/>
{brows}{eye(207,-1)}{eye(306,1)}<ellipse cx="181" cy="281" rx="36" ry="23" fill="url(#cheek)"/><ellipse cx="331" cy="282" rx="34" ry="22" fill="url(#cheek)"/>
<path d="M254 275 q8 7 15 0" stroke="#df8651" stroke-width="3" fill="none"/>{mouth}<ellipse cx="177" cy="274" rx="6" ry="3" fill="#ffdebf"/><ellipse cx="332" cy="275" rx="6" ry="3" fill="#ffdebf"/></g>
<g id="salmon-bob-locks" fill="url(#salmon)" stroke="#e36a37" stroke-width="2"><path d="M144 225 Q124 174 181 140 Q231 111 276 132 Q229 132 211 168 Q162 181 144 225Z"/><path d="M149 239 Q130 283 152 300 Q166 314 183 293 Q161 279 179 231 Q159 211 149 239Z"/><path d="M174 183 Q186 148 234 139 Q254 135 281 144 Q230 147 211 179 Q190 190 174 183Z"/><path d="M302 137 Q348 141 368 186 Q382 226 354 249 Q365 206 328 186Z"/>
<g fill="none" stroke="#ffcf9e" stroke-width="4" stroke-linecap="round"><path d="M148 192 Q174 153 215 143 M144 213 Q167 174 200 167 M150 273 Q147 285 160 290 M322 153 Q357 174 360 204 M183 174 Q206 151 241 146"/>{marbling}</g>
<path d="M162 162 Q193 135 221 137" stroke="#fff0cf" stroke-width="3" fill="none" opacity=".8"/></g>
<g id="avocado-forehead"><path d="M235 115 Q274 103 300 126 Q304 160 289 196 L275 222 Q268 199 253 184 Q247 145 226 131Z" fill="url(#avo)" stroke="#9eb544" stroke-width="2"/><path d="M237 122 Q262 139 268 183" stroke="#f5f4b7" stroke-width="3" opacity=".8" fill="none"/><path d="M278 145 l4 4 m-6 14 l4 4 m-7 13 l3 3" stroke="#a4bc4d" stroke-width="2" stroke-linecap="round"/></g>
<g id="jalapeno-hat"><path d="M235 100 L235 114 Q265 141 306 118 L306 103Z" fill="#274a14" stroke="#243e13" stroke-width="2"/><ellipse cx="271" cy="101" rx="37" ry="21" fill="#5c8326" stroke="#263f12" stroke-width="3"/><ellipse cx="271" cy="100" rx="29" ry="14" fill="#bfd36b"/>
{''.join(f'<ellipse cx="{271+18*math.cos(i*math.tau/7):.2f}" cy="{100+8*math.sin(i*math.tau/7):.2f}" rx="7" ry="3.5" transform="rotate({i*360/7:.2f} {271+18*math.cos(i*math.tau/7):.2f} {100+8*math.sin(i*math.tau/7):.2f})" fill="#ffe4a1"/>' for i in range(7))}
<ellipse cx="272" cy="94" rx="15" ry="11" fill="#d82c0d"/><circle cx="274" cy="89" r="12" fill="#ee3b13"/><ellipse cx="270" cy="83" rx="5" ry="3" fill="#fff3cc"/></g>
<g id="left-arm-glove" fill="url(#nori)" stroke="#111b10" stroke-width="2"><path d="M171 326 Q144 336 132 306 L137 287 L146 290 Q145 311 166 304Z"/><ellipse cx="133" cy="294" rx="17" ry="22" transform="rotate(-20 133 294)"/><ellipse cx="125" cy="272" rx="7" ry="20" transform="rotate(-30 125 272)"/><ellipse cx="141" cy="272" rx="7" ry="20" transform="rotate(16 141 272)"/><ellipse cx="146" cy="291" rx="8" ry="11" transform="rotate(30 146 291)"/><ellipse cx="124" cy="291" rx="8" ry="9"/><path d="M126 270 l-5 -9 M128 293 l-3 -5 M144 312 l6 4" fill="none" stroke="#85907b" stroke-width="3" stroke-linecap="round"/></g>
<g id="right-arm-glove" transform="rotate({arm:.3f} 340 320)" fill="url(#nori)" stroke="#111b10" stroke-width="2"><path d="M340 313 Q366 326 372 299 L385 302 Q382 346 349 333Z"/><ellipse cx="379" cy="291" rx="18" ry="20" transform="rotate(20 379 291)"/><ellipse cx="372" cy="272" rx="7" ry="14"/><ellipse cx="384" cy="271" rx="7" ry="15" transform="rotate(12 384 271)"/><ellipse cx="393" cy="280" rx="6" ry="12" transform="rotate(28 393 280)"/><ellipse cx="366" cy="292" rx="8" ry="12" transform="rotate(-25 366 292)"/><path d="M375 285 q7 -7 14 -1 M361 327 l9 -5" stroke="#818c77" stroke-width="3" fill="none" stroke-linecap="round"/></g></g></svg>'''

def png(source, size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=source.encode(), output_width=size, output_height=size))).convert('RGBA')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--size', type=int, default=1080); p.add_argument('--video', action='store_true'); a=p.parse_args()
    if a.size < 64 or a.size > 4096: p.error('size must be 64–4096')
    dest=ROOT/'assets/2d'; dest.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1280,600),'#faf3e7'); draw=ImageDraw.Draw(sheet)
    for i,e in enumerate(EXPRESSIONS):
        source=svg(e); (dest/f'{e}.svg').write_text(source,encoding='utf-8'); png(source,a.size).save(dest/f'{e}.png')
        tile=png(source,256); sheet.paste(tile,((i%5)*256,(i//5)*300),tile); draw.text(((i%5)*256+100,(i//5)*300+270),e,fill='#18392f')
    sheet.save(dest/'expression-sheet.png')
    social=ROOT/'assets/social'; social.mkdir(parents=True,exist_ok=True)
    for motion in ('idle','wave','dance'):
        frames=[png(svg('wink' if motion=='wave' else 'happy',i/48,motion),512) for i in range(48)]
        frames[0].save(social/f'{motion}.webp',save_all=True,append_images=frames[1:],duration=42,loop=0,lossless=True)
        # Sprite sheet is RGBA and usable in video editors or game engines.
        sprites=Image.new('RGBA',(512*8,512*6))
        for i,f in enumerate(frames): sprites.paste(f,((i%8)*512,(i//8)*512))
        sprites.save(social/f'{motion}-sprites.png')
        if a.video:
            for label,w,h in [('square',1080,1080),('portrait',1080,1920)]:
                cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s','512x512','-r','24','-i','-','-vf',f'scale={w}:{w},pad={w}:{h}:0:({h}-ih)/2:color=0xfaf3e7,format=yuv420p','-c:v','libx264','-movflags','+faststart',str(social/f'{motion}-{label}.mp4')]
                # Composite before encoding: MP4 does not support transparency.
                with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
                    for f in frames:
                        bg=Image.new('RGBA',f.size,'#faf3e7'); bg.alpha_composite(f); proc.stdin.write(bg.tobytes())
                    proc.stdin.close()
                    if proc.wait(): raise RuntimeError('FFmpeg export failed')
    (social/'sprites.json').write_text(json.dumps({'frameWidth':512,'frameHeight':512,'columns':8,'frames':48,'fps':24,'clips':['idle','wave','dance']},indent=2)+'\n')
    print('Exported 10 SVG/PNG expressions, contact sheet, 3 WebP loops and sprite sheets.')
if __name__=='__main__': main()
