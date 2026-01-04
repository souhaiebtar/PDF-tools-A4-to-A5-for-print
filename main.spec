# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['customtkinter', 'darkdetect']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Bundle local external tool dependencies into the onefile EXE.
# Note: they will still be extracted to a temp folder at runtime (sys._MEIPASS).
# __file__ is not guaranteed to be defined in the spec execution context.
# We rely on running pyinstaller from the project root (build.bat enforces this).
BASE_DIR = os.path.abspath(os.getcwd())


def _add_tree(src_dir: str, dest_dir: str, out_list: list[tuple[str, str]]) -> None:
    for root, _dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        target_dir = dest_dir if rel_root == "." else os.path.join(dest_dir, rel_root)
        for filename in files:
            out_list.append((os.path.join(root, filename), target_dir))


deps_dir = os.path.join(BASE_DIR, "dependencies")

pdfcpu_exe = os.path.join(deps_dir, "pdfcpu.exe")
if os.path.exists(pdfcpu_exe):
    binaries.append((pdfcpu_exe, "dependencies"))

qpdf_dir = os.path.join(deps_dir, "qpdf")
if os.path.isdir(qpdf_dir):
    _add_tree(qpdf_dir, os.path.join("dependencies", "qpdf"), binaries)


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
