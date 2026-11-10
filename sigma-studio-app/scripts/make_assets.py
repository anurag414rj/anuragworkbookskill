"""Generate the studio asset kit (original art, safe to ship) from brand colors.

    python3 make_assets.py --ink '#252423' --accent '#efff92' --second '#b9b3e0' --out site/assets [--seed 7]

Writes glass.svg, dark-glass.svg, hero-dark.svg. Copy logo.svg / logo-light.svg in yourself.
"""
import argparse, math, os, random


def mix(a, b, t):
    a, b = a.lstrip('#'), b.lstrip('#')
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#' + ''.join('%02x' % round(x + (y - x) * t) for x, y in zip(ca, cb))


def glass(second):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" preserveAspectRatio="none">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="{mix('#ffffff', second, .03)}"/><stop offset="1" stop-color="{mix('#ffffff', second, .12)}"/></linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="1"/><stop offset=".1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
    <radialGradient id="glow" cx="1" cy="0" r=".8"><stop offset="0" stop-color="{second}" stop-opacity=".16"/><stop offset="1" stop-color="{second}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#g)"/><rect width="400" height="300" fill="url(#glow)"/><rect width="400" height="300" fill="url(#sheen)"/>
</svg>
'''


def dark_glass(ink, accent, second):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" preserveAspectRatio="none">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(ink, '#000000', .25)}"/><stop offset=".6" stop-color="{ink}"/><stop offset="1" stop-color="{mix(ink, second, .22)}"/></linearGradient>
    <radialGradient id="glow" cx="1" cy="1" r=".9"><stop offset="0" stop-color="{accent}" stop-opacity=".10"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".08"/><stop offset=".15" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#g)"/><rect width="400" height="300" fill="url(#glow)"/><rect width="400" height="300" fill="url(#sheen)"/>
</svg>
'''


def hero(ink, accent, second, seed):
    rnd = random.Random(seed)
    rings = []
    cx, cy = 1180, 150
    for k in range(9):  # wobbly concentric contours, bottom-right
        r = 40 + k * 26
        pts = []
        ph = rnd.uniform(0, 6.28)
        for i in range(61):
            a = 6.2832 * i / 60
            rr = r * (1 + .08 * math.sin(3 * a + ph) + .04 * math.sin(5 * a - ph))
            pts.append('%.1f,%.1f' % (cx + 1.9 * rr * math.cos(a), cy + .9 * rr * math.sin(a)))
        rings.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#ffffff" stroke-opacity="{.05 + .012 * k:.3f}" stroke-width="1"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 340" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(ink, '#000000', .3)}"/><stop offset=".6" stop-color="{ink}"/><stop offset="1" stop-color="{mix(ink, second, .25)}"/></linearGradient>
    <radialGradient id="ga" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{accent}" stop-opacity=".30"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <radialGradient id="gs" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{second}" stop-opacity=".35"/><stop offset="1" stop-color="{second}" stop-opacity="0"/></radialGradient>
    <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
  </defs>
  <rect width="1600" height="340" fill="url(#bg)"/>
  <ellipse cx="1250" cy="300" rx="520" ry="150" fill="url(#ga)"/>
  <ellipse cx="200" cy="-20" rx="460" ry="200" fill="url(#gs)"/>
  <g>{"".join(rings)}</g>
  <rect x="980" y="318" width="520" height="2" fill="url(#bar)" opacity=".7"/>
</svg>
'''


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ink', required=True)
    ap.add_argument('--accent', required=True)
    ap.add_argument('--second', required=True)
    ap.add_argument('--out', default='site/assets')
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = {'glass.svg': glass(a.second), 'dark-glass.svg': dark_glass(a.ink, a.accent, a.second),
             'hero-dark.svg': hero(a.ink, a.accent, a.second, a.seed)}
    for n, s in files.items():
        open(os.path.join(a.out, n), 'w').write(s)
        print('wrote', os.path.join(a.out, n), len(s), 'bytes')
