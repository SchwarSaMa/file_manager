import json
import logging
from pathlib import Path


def prompt_user_for_path(home_dir: Path) -> Path:
    prompt = (
        f"Fill in directory path you want to organize (e.g {home_dir}/a/directory): "
    )
    path = Path(input(prompt))

    return path


class PathExistsError(Exception):
    pass


class FileOrganizer:
    DEFAULT_CATEGORY = "Unknown"
    MAPPING_FILE = Path(__file__).parent / "file_types.json"

    def __init__(self, path: Path) -> None:
        self.path = path
        self._known_file_types = self._load_mapping(FileOrganizer.MAPPING_FILE)
        self._unknown_file_types: set[str] = set()
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: Path):
        self._path = self._validate_path(path)

    @staticmethod
    def _validate_path(path: Path) -> Path:
        if not path.exists():
            raise PathExistsError(
                f"The path '{path}' does not exist in your file system"
            )
        elif not path.is_dir():
            raise NotADirectoryError(f"Not a directory: '{path}'")

        return path

    @staticmethod
    def _get_unique_path(file_path: Path) -> Path:
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

    def _load_mapping(self, mapping_file: Path) -> dict[str, str | None]:
        try:
            with open(mapping_file, "r") as f:
                return json.load(f)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self._logger.warning(f"Could not be loaded: {mapping_file}")
            return {}

    def save_mapping(self) -> None:
        updated_file_types = self._known_file_types | dict.fromkeys(
            self._unknown_file_types
        )
        with open(FileOrganizer.MAPPING_FILE, "w") as f:
            json.dump(updated_file_types, f, indent=4)
        self._logger.info(
            f"Unknown file extensions saved: {self._unknown_file_types or 'None'}"
        )

    def _get_category(self, file: Path) -> str | None:
        suffix = file.suffix.lower()
        if file.is_file() and not suffix == "":
            return self._known_file_types.get(suffix, FileOrganizer.DEFAULT_CATEGORY)
        else:
            return None

    def _make_directory(self, category: str) -> Path:
        directory = self.path / category
        directory.mkdir(exist_ok=True)
        return directory

    def organize(self) -> None:
        for file in self.path.iterdir():
            category = self._get_category(file)

            if category is None:
                continue

            if category == FileOrganizer.DEFAULT_CATEGORY:
                self._unknown_file_types.add(file.suffix.lower())
                continue

            directory = self._make_directory(category)
            unique_path = self._get_unique_path(directory / file.name)

            try:
                file.rename(unique_path)
            except PermissionError:
                self._logger.warning(
                    f"No permission for: '{unique_path}' will be ignored."
                )
            else:
                self._logger.info(
                    f"File successfully moved: {file.name} -> {unique_path}"
                )


def logging_config(path_to_log_file: Path) -> None:
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    c_handler: logging.Handler = logging.StreamHandler()
    f_handler: logging.Handler = logging.FileHandler(path_to_log_file, encoding="utf-8")

    c_handler.setLevel(logging.WARNING)
    f_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    for handler in [c_handler, f_handler]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)


if __name__ == "__main__":
    HOME = Path.home()
    PATH_TO_LOG_FILE = Path(__file__).parent / "file_organizer.log"

    logging_config(PATH_TO_LOG_FILE)
    user_response = prompt_user_for_path(HOME)

    try:
        downloads = FileOrganizer(user_response)
        downloads.organize()
        downloads.save_mapping()
    except PathExistsError as e:
        logging.critical(f"!! {e} !!")
    except NotADirectoryError as e:
        logging.critical(f"!! {e} !!")
