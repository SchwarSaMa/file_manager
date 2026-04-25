from pathlib import Path
import logging
import json

class PathExistsError(Exception):
    pass

def get_path_from_user():
    home = Path.home()
    path = Path(input(f'Fill in directory path you want to organize (e.g {home}/a/directory): '))
    if not path.exists():
        raise PathExistsError(f'The path \'{path}\' does not exist in your file system')
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
    directories = set()
    unknown_file_types = set()

    for file in target_path.iterdir():
        if file.is_file() and not file.suffix == '':
            try:
                file_cat = get_file_category(file.suffix.lower(), file_mapping)
                if file_cat == 'unknown_file_type':
                    unknown_file_types.add(file.suffix.lower())
                    continue
                if file_cat == None:
                    continue
                if file_cat not in directories:
                    Path(target_path / file_cat).mkdir(exist_ok=True)
                    directories.add(file_cat)
                dest_path = target_path / file_cat / file.name
                new_dest_path = get_unique_path(dest_path)
                file.rename(new_dest_path)
                logging.info(f'File successfully moved: {file.name} -> {new_dest_path}')
            except PermissionError:
                logging.warning(f'No permission for: \'{dest_path}\' will be ignored.')
            except TypeError:
                logging.warning(f'{file.suffix.lower()} is not yet defined.')
    return unknown_file_types

def logging_config(path_to_log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    while logger.handlers:
        logger.removeHandler(logger.handlers[0])
    
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.WARNING)
    f_handler = logging.FileHandler(path_to_log_file, encoding='utf-8')
    f_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    for handler in [c_handler, f_handler]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def import_json(file_path):
    try:
        with open(file_path, 'r') as f:
            known_file_types = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return {}
    return known_file_types

def export_json(new_extensions, old_extensions, file_path):
    old_ext_dict = old_extensions | {extension: None for extension in new_extensions}
    with open(file_path, 'w') as f:
        json.dump(old_ext_dict, f, indent=4)
    logging.info(f'Unknown file extensions saved: {new_extensions}')

def main():
    LOG_FILE = Path(__file__).parent / "file_organizer.log"
    JSON_FILE = Path(__file__).parent / "file_extensions.json"

    logging_config(LOG_FILE)
    try: 
        known_file_types = import_json(JSON_FILE)
        target_path = get_path_from_user()
        unknown_file_types = organize_folder(target_path, known_file_types)
        export_json(unknown_file_types, known_file_types, JSON_FILE)
    except PathExistsError as e:
        logging.critical(f'!! {e} !!')
    except NotADirectoryError as e:
        logging.critical(f'!! {e} !!')
    
if __name__ == '__main__':
    main()