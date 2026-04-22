import os
from pathlib import Path

class PathExistsError(Exception):
    pass

def get_path_from_user():
    home = Path.home()
    path = Path(input(f'Fill in directory path you want to organize (e.g {home}/a/directory): '))
    if not path.exists():
        raise PathExistenceError(f'The path \'{path}\' does not exist in your file system')
    elif not path.is_dir():
        raise NotADirectoryError(f'Not a directory: \'{path}\'')
    
    return path

def get_file_category(extension, file_mapping):
    return file_mapping.get(extension, 'unknown_file_type')

def get_unique_path(base_path):
    if not base_path.exists():
        return base_path
    else:
        copy_num = 1
        while True: 
            new_path = base_path.with_name(f'{base_path.stem}_{copy_num}{base_path.suffix}')
            if not new_path.exists():
                return new_path
            copy_num += 1

def organize_folder(target_path, file_mapping):
    for file in target_path.iterdir():
        if file.is_file():
            try:
                file_cat = get_file_category(file.suffix, file_mapping)
                Path(target_path / file_cat).mkdir(exist_ok=True)
                dest_path = target_path / file_cat / file.name
                new_dest_path = get_unique_path(dest_path)
                file.rename(new_dest_path)
            except PermissionError:
                print(f'No permission for: \'{dest_path}\' will be ignored.')

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
    except PathExistsError as e:
        print(f'!! {e} !!')
    except NotADirectoryError as e:
        print(f'!! {e} !!')
    

if __name__ == '__main__':
    main()