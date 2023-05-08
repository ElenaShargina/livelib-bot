import os


def get_correct_filename(filename: str, folder: str, ) -> str:
    """
    служебная функция для получения корректного пути до тестовых файлов конфига, дб и тд,
    нужна для правильной отработки тестов в Github Actions
    """
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    prefix_folder = os.path.join(parent_dir, *folder.split('/'))
    return os.path.join(prefix_folder, filename)
