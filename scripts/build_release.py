"""Native builds, packaged smoke check and release archives."""
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
version=(ROOT/'VERSION').read_text().strip()
system=platform.system()
args=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--onedir','--name','Prompchu','--add-data',str(ROOT/'assets')+os.pathsep+'assets']
if system=='Windows': args+=['--icon',str(ROOT/'assets/prompchu-corujinha.ico')]
if system=='Darwin':
    iconset=ROOT/'Prompchu.iconset';iconset.mkdir(exist_ok=True)
    for size in (16,32,128,256,512):
        for scale in (1,2):
            output=iconset/f"icon_{size}x{size}{'@2x' if scale==2 else ''}.png"
            subprocess.run(['sips','-z',str(size*scale),str(size*scale),str(ROOT/'assets/prompchu-corujinha.png'),'--out',str(output)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['iconutil','-c','icns',str(iconset),'-o',str(ROOT/'build-icon.icns')],check=True)
    args+=['--icon',str(ROOT/'build-icon.icns'),'--osx-bundle-identifier','com.bugzinho.prompchu']
subprocess.run(args+[str(ROOT/'main.py')],check=True)
exe=ROOT/('dist/Prompchu/Prompchu.exe' if system=='Windows' else 'dist/Prompchu.app/Contents/MacOS/Prompchu' if system=='Darwin' else 'dist/Prompchu/Prompchu')
with tempfile.TemporaryDirectory() as config:
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen',XDG_CONFIG_HOME=config)
    subprocess.run([str(exe),'--smoke-test'],env=env,check=True,timeout=60)
out=ROOT/'release';out.mkdir(exist_ok=True)
name=f'Prompchu-{version}-{system}-{platform.machine()}'
if system=='Darwin':
    archive=out/(name+'.zip')
    subprocess.run(['ditto','-c','-k','--sequesterRsrc','--keepParent','dist/Prompchu.app',str(archive)],check=True)
else:
    bundle=ROOT/'dist/Prompchu'
    shutil.copy2(ROOT/'README.md',bundle/'README.md')
    archive=Path(shutil.make_archive(str(out/name),'zip' if system=='Windows' else 'gztar',root_dir='dist',base_dir='Prompchu'))
print('Archive:',archive.name)
print('SHA256:',hashlib.file_digest(archive.open('rb'),'sha256').hexdigest())
