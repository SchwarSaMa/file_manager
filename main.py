import os
from pathlib import Path

def main():
    file_extensions = {
        '.jpg': 'pictures',
        '.png': 'pictures',
        '.pdf': 'documents',
        '.docx': 'documents',
    }

    home = Path.home()
    downloads = home / 'Downloads'
    for file in downloads.iterdir():
        if file.is_file():
            file_cat = file_extensions.get(file.suffix, 'unknown_file_type')
            Path(downloads / file_cat).mkdir(exist_ok=True)
            dest_path = downloads / file_cat / file.name
            if not dest_path.exists():
                file.rename(downloads / file_cat / file.name)
            else:
                print(f'File {file.name} already exists in Directory {dest_path}')

if __name__ == '__main__':
    main()