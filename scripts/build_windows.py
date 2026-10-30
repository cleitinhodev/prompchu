"""Execute com Python no Windows; gera dist/Prompchu com todos os assets."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    if sys.platform != 'win32':
        raise SystemExit('Execute esta build no Windows. PyInstaller gera para o sistema em que é executado.')
    subprocess.run([
        sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--windowed', '--onedir', '--name', 'Prompchu',
        '--icon', str(ROOT / 'assets/prompchu-corujinha.ico'),
        '--add-data', str(ROOT / 'assets') + os.pathsep + 'assets',
        str(ROOT / 'main.py'),
    ], cwd=ROOT, check=True)
    print('Pronto: dist/Prompchu/Prompchu.exe. Distribua a pasta inteira.')

if __name__ == '__main__':
    main()
