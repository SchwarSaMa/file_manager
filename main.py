import os
from pathlib import Path

class PathExistenceError(Exception):
    pass

def get_path_from_user(): 
    path = Path(input('Fill in directory path you want to organize: '))
    if not path.exists():
        raise PathExistenceError(f'The path \'{path}\' does not exist in your file system')
    elif not path.is_dir():
        raise NotADirectoryError(f'Not a directory: \'{path}\'')
    
    return path

def get_file_category(extension, file_mapping):
    return file_mapping.get(extension, 'unknown_file_type')

def organize_folder(target_path, file_mapping):
    for file in target_path.iterdir():
        if file.is_file():
            file_cat = get_file_category(file.suffix, file_mapping)
            Path(target_path / file_cat).mkdir(exist_ok=True)
            dest_path = target_path / file_cat / file.name
            if not dest_path.exists():
                file.rename(dest_path)
            else:
                print(f'File {file.name} already exists in Directory {dest_path}')

def main():
    file_mapping = {
        '.jpg': 'pictures',
        '.png': 'pictures',
        '.pdf': 'documents',
        '.docx': 'documents',
    }
    downloads = Path.home() / 'Downloads'
    print(downloads)

    try: 
        target_path = get_path_from_user()
        organize_folder(target_path, file_mapping)
    except PathExistenceError as e:
        print(f'!! {e} !!')
    except NotADirectoryError as e:
        print(f'!! {e} !!')
    

if __name__ == '__main__':
    main()