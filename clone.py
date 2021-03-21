import os
import subprocess

if not os.path.exists('skia'):
    subprocess.call(['git', 'clone', 'https://skia.googlesource.com/skia.git'])
