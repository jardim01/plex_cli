import subprocess

SUBTITLE_CLEANER = 'cmd /c D:\\Projects\\Electron\\SubtitleCleaner\\run.vbs'


def open_subtitle_cleaner(args):
    args = [f'"{arg}"' for arg in args]
    subprocess.call(f'{SUBTITLE_CLEANER} {" ".join(args)}')


def convert_to_utf8(file):
    p = subprocess.Popen(
        f'python "D:\\Projects\\Python\\convert_to_utf8\\main.py" -o "{file}"'
    )
    p.wait()
