#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys

def main(paths):
    base = os.getcwd()
    for rel in paths:
        p = os.path.join(base, *rel.split('/'))
        print('=== FILE:', p)
        if os.path.isfile(p):
            try:
                with open(p, 'r', encoding='utf-8', errors='replace') as f:
                    print(f.read())
            except Exception as e:
                print('ERROR:', e)
        else:
            print('MISSING')

if __name__ == '__main__':
    args = sys.argv[1:] or [
        'docs/proposals/Request_for_Codex_100xFenok_Analysis.md',
        'communication/gemini/100xFenok_IMPROVEMENT_REPORT.md',
    ]
    main(args)

