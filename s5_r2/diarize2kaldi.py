#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

if len(sys.argv) < 3:
    raise Exception(f'usage: {sys.argv[0]} outdir diar1.json ...')

outdir = sys.argv[1]
wavscp = list()
segments = list()
utt2spk = list()

for fn in sorted(sys.argv[2:]):
    rec = f'{fn[:-5]}'

    with open(fn) as f:
        seg = json.load(f)

    prev = 0
    for (i, s) in enumerate(seg['segments']):
        if prev > s[1]:
            s[1] = prev + 0.01
        start = int(s[1] * 100)
        end = int(s[2] * 100)
        seg = f'{rec}_{start:06d}-{end:06d}'
        segments.append(f'{s[0]:02d}-{seg} {s[0]:02d}-{rec} {s[1]:.2f} {s[2]:.2f}')
        utt2spk.append(f'{s[0]:02d}-{seg} {s[0]:02d}-{rec}')
        wavscp.append(f'{s[0]:02d}-{rec} {rec}')
        prev = s[2]

wavscp = list(set(wavscp))
with open(f'{outdir}/wav.scp', 'w') as f:
    f.writelines(s + '\n' for s in wavscp)

with open(f'{outdir}/segments', 'w') as f:
    f.writelines(s + '\n' for s in segments)

with open(f'{outdir}/utt2spk', 'w') as f:
    f.writelines(s + '\n' for s in utt2spk)
    
