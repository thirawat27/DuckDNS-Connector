# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['duckdns_connector.py'],
    pathex=['.'],
    binaries=[],
    
    # Kept logo.ico, removed customtkinter which is not used
    datas=[
        ('logo.ico', '.')
    ],
    
    hiddenimports=['pystray._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# --- MODIFIED FOR ONE-FILE ---
# We combine everything into the EXE block and remove the COLLECT block
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='DuckDNS-Connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    
    # Console window is hidden, which is correct
    console=False,
    windowed=True,
    
    # Set the .exe icon
    icon='logo.ico'
)

# --- REMOVED FOR ONE-FILE ---
# The COLLECT block is what creates a folder. We don't need it for a single file executable.
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='DuckDNS-Connector'
# )