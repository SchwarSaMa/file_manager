from pathlib import Path
import logging
import json


def prompt_user_for_path(home_dir):
    path = Path(
        input(
            f"Fill in directory path you want to organize (e.g {home_dir}/a/directory): "
        )
    )

    return path


class PathExistsError(Exception):
    pass


class FileOrganizer:
    DEFAULT_CATEGORY = "Unknown"

    def __init__(
        self,
        path,
        log_file=Path(__file__).parent / "file_organizer.log",
        mapping_file=Path(__file__).parent / "file_types.json",
    ):
        self.path = self.validate_path(Path(path))
        self.mapping_file = mapping_file
        self.known_file_types = self._load_mapping(mapping_file)
        self.unknown_file_types = set()

    @staticmethod
    def validate_path(path: Path) -> Path:
        if not path.exists():
            raise PathExistsError(
                f"The path '{path}' does not exist in your file system"
            )
        elif not path.is_dir():
            raise NotADirectoryError(f"Not a directory: '{path}'")

        return path

    @staticmethod
    def load_mapping(mapping_file: Path) -> dict:
        try:
            with open(mapping_file, "r") as f:
                return json.load(f)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            logging.warning(f"Could not be loaded: {mapping_file}")
            return {}

    @staticmethod
    def get_unique_path(file_path):
        if not file_path.exists():
            return file_path
        else:
            copy_num = 1
            while True:
                new_file_path = file_path.with_name(
                    f"{file_path.stem}_{copy_num}{file_path.suffix}"
                )
                if not new_file_path.exists():
                    return new_file_path
                copy_num += 1

    def _get_file_category(self, file_suffix):
        return self.known_file_types.get(file_suffix, FileOrganizer.DEFAULT_CATEGORY)

    def save_mapping(self):
        updated_file_types = self.known_file_types | {
            file_type: None for file_type in self.unknown_file_types
        }
        with open(self.mapping_file, "w") as f:
            json.dump(updated_file_types, f, indent=4)
        logging.info(f"Unknown file extensions saved: {self.unknown_file_types}")

    def run(self):
        file_categories = set()

        for file in self.path.iterdir():
            file_suffix = file.suffix.lower()
            if file.is_file() and not file_suffix == "":
                try:
                    file_category = self._get_file_category(file_suffix)

                    if file_category == FileOrganizer.DEFAULT_CATEGORY:
                        self.unknown_file_types.add(file_suffix)
                        continue

                    # for cases {'.example': null} in file_types.json
                    if file_category is None:
                        continue

                    file_category_path = self.path / file_category
                    if file_category not in file_categories:
                        file_category_path.mkdir(exist_ok=True)
                        file_categories.add(file_category)

                    file_path = file_category_path / file.name
                    unique_file_path = self.get_unique_path(file_path)
                    file.rename(unique_file_path)
                    logging.info(
                        f"File successfully moved: {file.name} -> {unique_file_path}"
                    )

                except PermissionError:
                    logging.warning(
                        f"No permission for: '{unique_file_path}' will be ignored."
                    )


def validate_path_from_user(path):
    if not path.exists():
        raise PathExistsError(f"The path '{path}' does not exist in your file system")
    elif not path.is_dir():
        raise NotADirectoryError(f"Not a directory: '{path}'")

    return path


def get_file_category(extension, file_mapping, default_category):
    return file_mapping.get(extension, default_category)


def get_unique_path(base_path):
    if not base_path.exists():
        return base_path
    else:
        copy_num = 1
        while True:
            new_path = base_path.with_name(
                f"{base_path.stem}_{copy_num}{base_path.suffix}"
            )
            if not new_path.exists():
                return new_path
            copy_num += 1


def organize_folder(target_path, file_mapping, default_category):
    directories = set()
    unknown_file_types = set()

    for file in target_path.iterdir():
        file_suffix = file.suffix.lower()
        if file.is_file() and not file_suffix == "":
            try:
                file_cat = get_file_category(
                    file_suffix, file_mapping, default_category
                )

                if file_cat == default_category:
                    unknown_file_types.add(file_suffix)
                    continue

                # for cases {'.example': null} in file_extensions.json
                if file_cat is None:
                    continue

                category_dir = target_path / file_cat
                if file_cat not in directories:
                    category_dir.mkdir(exist_ok=True)
                    directories.add(file_cat)

                dest_path = category_dir / file.name
                new_dest_path = get_unique_path(dest_path)
                file.rename(new_dest_path)
                logging.info(f"File successfully moved: {file.name} -> {new_dest_path}")

            except PermissionError:
                logging.warning(f"No permission for: '{dest_path}' will be ignored.")

    return unknown_file_types


def logging_config(path_to_log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.WARNING)
    f_handler = logging.FileHandler(path_to_log_file, encoding="utf-8")
    f_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    for handler in [c_handler, f_handler]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def import_json(file_path):
    try:
        with open(file_path, "r") as f:
            known_file_types = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return {}
    return known_file_types


def export_json(new_extensions, old_extensions, file_path):
    old_ext_dict = old_extensions | {extension: None for extension in new_extensions}
    with open(file_path, "w") as f:
        json.dump(old_ext_dict, f, indent=4)
    logging.info(f"Unknown file extensions saved: {new_extensions}")


def main():
    LOG_FILE = Path(__file__).parent / "file_organizer.log"
    JSON_FILE = Path(__file__).parent / "file_extensions.json"
    UNKNOWN_CATEGORY = "unknown_category"
    HOME_DIR = Path.home()

    logging_config(LOG_FILE)
    try:
        target_path = validate_path_from_user(prompt_user_for_path(HOME_DIR))
        known_file_types = import_json(JSON_FILE)
        unknown_file_types = organize_folder(
            target_path, known_file_types, UNKNOWN_CATEGORY
        )
        export_json(unknown_file_types, known_file_types, JSON_FILE)
    except PathExistsError as e:
        logging.critical(f"!! {e} !!")
    except NotADirectoryError as e:
        logging.critical(f"!! {e} !!")


if __name__ == "__main__":
    main()
