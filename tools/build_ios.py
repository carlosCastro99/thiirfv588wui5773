#!/usr/bin/env python3
"""Assemble ios/www for the Capacitor shell: the app, every pack (all languages), icons and legal pages,
with native-bridge.js loaded before the app script."""
import os, shutil, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW = os.path.join(ROOT, "ios", "www")
if os.path.exists(WWW): shutil.rmtree(WWW)
os.makedirs(WWW)
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
tag = '<script src="native-bridge.js"></script>\n'
i = html.index("<script>")
open(os.path.join(WWW, "index.html"), "w", encoding="utf-8").write(html[:i] + tag + html[i:])
shutil.copy(os.path.join(ROOT, "ios", "native-bridge.js"), WWW)
for f in ("manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"):
    shutil.copy(os.path.join(ROOT, f), WWW)
shutil.copytree(os.path.join(ROOT, "packs"), os.path.join(WWW, "packs"))
if os.path.isdir(os.path.join(ROOT, "legal")): shutil.copytree(os.path.join(ROOT, "legal"), os.path.join(WWW, "legal"))
n = len(glob.glob(os.path.join(WWW, "packs", "**", "*.json"), recursive=True))
size = sum(os.path.getsize(f) for f in glob.glob(os.path.join(WWW, "**", "*"), recursive=True) if os.path.isfile(f))
print(f"ios/www: {n} pack files, {size/1e6:.1f} MB")
