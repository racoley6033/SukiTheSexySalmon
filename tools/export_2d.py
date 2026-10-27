"""Deterministic layered SVG mascot, PNG stickers and animated social exports."""
import argparse, io, json, math, subprocess
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
EXPRESSIONS = ('happy', 'wink', 'excited', 'love', 'surprised', 'sad', 'angry', 'sleepy')

def svg(expression='happy', phase=0, motion='idle'):
    if expression not in EXPRESSIONS:
        raise ValueError(expression)
    bob = 8 * math.sin(phase * 2 * math.pi)
    arm = -30 * math.sin(phase * 2 * math.pi) if motion == 'wave' else 0
    tilt = 6 * math.sin(phase * 2 * math.pi) if motion == 'dance' else 0
    def eye(x, closed=False):
        if closed: return f'<path d="M{x-22} 268 Q{x} 244 {x+22} 268" fill="none" stroke="#18392f" stroke-width="9" stroke-linecap="round"/>'
        if expression == 'love': return f'<path d="M{x} 283 C{x-65} 249 {x-20} 219 {x} 245 C{x+20} 219 {x+65} 249 {x} 283" fill="#df4262"/>'
        return f'<ellipse cx="{x}" cy="261" rx="29" ry="36" fill="#fffdf3"/><ellipse cx="{x+3}" cy="265" rx="17" ry="23" fill="#4eaa65"/><ellipse cx="{x+5}" cy="267" rx="9" ry="16" fill="#173a30"/><circle cx="{x-1}" cy="253" r="6" fill="white"/>'
    mouth = {'happy':'M226 299 Q256 333 286 299','wink':'M226 299 Q256 333 286 299','excited':'M226 297 Q256 353 286 297 Z','love':'M230 300 Q256 329 282 300','sad':'M231 320 Q256 292 281 320','angry':'M232 318 Q256 301 280 318','sleepy':'M244 311 L268 311'}.get(expression)
    mouth = f'<path d="{mouth}" fill="{"#542c35" if expression == "excited" else "none"}" stroke="#173a30" stroke-width="7" stroke-linecap="round"/>' if mouth else '<ellipse cx="256" cy="314" rx="15" ry="21" fill="#542c35"/>'
    brows = '<path d="M183 220 L221 234 M291 234 L329 220" stroke="#173a30" stroke-width="8" stroke-linecap="round"/>' if expression == 'angry' else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Suki {expression}">
<g id="character" transform="translate(0 {bob:.3f}) rotate({tilt:.3f} 256 280)">
<g id="nori-limbs" fill="#18392f" stroke="#18392f" stroke-width="19" stroke-linecap="round"><path d="M210 365 L202 413 M301 365 L312 413 M141 285 Q106 303 96 330" fill="none"/><ellipse cx="194" cy="421" rx="25" ry="12" stroke="none"/><ellipse cx="320" cy="421" rx="25" ry="12" stroke="none"/><g transform="rotate({arm:.3f} 370 285)"><path d="M370 285 Q402 268 413 233" fill="none"/><path d="M413 240 L401 222 M413 240 L425 219" fill="none" stroke-width="10"/></g></g>
<g id="rice"><rect x="142" y="260" width="228" height="122" rx="54" fill="#f6edce" stroke="#18392f" stroke-width="7"/><path d="M165 336 l12 5 m20 11 l13 -2 m24 8 l12 -3 m25 1 l11 -5 m25 -2 l12 -5 m20 -8 l10 -5" stroke="#dfd1ad" stroke-width="7" stroke-linecap="round"/></g>
<g id="salmon"><path d="M135 225 Q133 180 186 177 L325 177 Q376 178 382 222 L378 293 Q375 327 341 326 L170 326 Q135 323 134 292 Z" fill="#fa886f" stroke="#18392f" stroke-width="7"/><path d="M157 217 Q206 201 230 184 M206 223 Q256 207 281 182 M264 224 Q312 207 331 187 M319 226 Q347 216 364 204" fill="none" stroke="#ffd3a7" stroke-width="10" stroke-linecap="round"/></g>
<g id="garnish"><path d="M245 178 L244 215 Q253 229 268 218 L270 177" fill="#a8cb68" stroke="#18392f" stroke-width="5"/><ellipse cx="285" cy="172" rx="40" ry="17" fill="#479052" stroke="#18392f" stroke-width="5"/><ellipse cx="285" cy="171" rx="23" ry="8" fill="#b9d67b"/><circle cx="287" cy="160" r="10" fill="#e14332"/></g>
<g id="face">{eye(202, expression == 'sleepy')}{eye(310, expression in ('wink','sleepy'))}{brows}<ellipse cx="169" cy="291" rx="16" ry="8" fill="#e86668"/><ellipse cx="343" cy="291" rx="16" ry="8" fill="#e86668"/>{mouth}</g></g></svg>'''

def png(source, size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=source.encode(), output_width=size, output_height=size))).convert('RGBA')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--size', type=int, default=1080); p.add_argument('--video', action='store_true'); a=p.parse_args()
    if a.size < 64 or a.size > 4096: p.error('size must be 64–4096')
    dest=ROOT/'assets/2d'; dest.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1024,600),'#faf3e7'); draw=ImageDraw.Draw(sheet)
    for i,e in enumerate(EXPRESSIONS):
        source=svg(e); (dest/f'{e}.svg').write_text(source,encoding='utf-8'); png(source,a.size).save(dest/f'{e}.png')
        tile=png(source,256); sheet.paste(tile,((i%4)*256,(i//4)*300),tile); draw.text(((i%4)*256+100,(i//4)*300+270),e,fill='#18392f')
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
    print('Exported 8 SVG/PNG expressions, contact sheet, 3 WebP loops and sprite sheets.')
if __name__=='__main__': main()
