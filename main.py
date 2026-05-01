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

    def __init__(
        self,
        path: Path,
        mapping_file: Path = Path(__file__).parent / "file_types.json",
    ) -> None:
        self.path = FileOrganizer.validate_path(Path(path))
        self.mapping_file = mapping_file
        self.known_file_types = self._load_mapping(mapping_file)
        self.unknown_file_types: set[str] = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def validate_path(path: Path) -> Path:
        if not path.exists():
            raise PathExistsError(
                f"The path '{path}' does not exist in your file system"
            )
        elif not path.is_dir():
            raise NotADirectoryError(f"Not a directory: '{path}'")

        return path

    def _load_mapping(self, mapping_file: Path) -> dict[str, str | None]:
        try:
            with open(mapping_file, "r") as f:
                return json.load(f)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self.logger.warning(f"Could not be loaded: {mapping_file}")
            return {}

    @staticmethod
    def get_unique_path(file_path: Path) -> Path:
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

    def _get_file_category(self, file_suffix: str) -> str | None:
        return self.known_file_types.get(file_suffix, FileOrganizer.DEFAULT_CATEGORY)

    def save_mapping(self) -> None:
        updated_file_types = self.known_file_types | dict.fromkeys(
            self.unknown_file_types
        )
        with open(self.mapping_file, "w") as f:
            json.dump(updated_file_types, f, indent=4)
        self.logger.info(
            f"Unknown file extensions saved: {self.unknown_file_types or 'None'}"
        )

    def organize(self) -> None:
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
                    unique_file_path = FileOrganizer.get_unique_path(file_path)
                    file.rename(unique_file_path)
                    self.logger.info(
                        f"File successfully moved: {file.name} -> {unique_file_path}"
                    )

                except PermissionError:
                    self.logger.warning(
                        f"No permission for: '{unique_file_path}' will be ignored."
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
