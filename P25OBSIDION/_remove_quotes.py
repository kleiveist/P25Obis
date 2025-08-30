#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def remove_quotes_from_numbers(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Alle Vorkommen von "123" → 123
    new_text = re.sub(r'"(\d+)"', r'\1', text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)

def main():
    for fname in os.listdir('.'):
        if fname.lower().endswith('.md'):
            remove_quotes_from_numbers(fname)

if __name__ == "__main__":
    main()
