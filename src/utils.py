import os
from typing import Optional, List, Union
from datetime import datetime
from recognizers_suite import Culture, recognize_datetime, ModelResult

from src.config import get_logger

logger = get_logger()


def find_files(data_dir: str, prefix: str = '', suffix: str = '') -> List[str]:
    """
    find files with different prefix
    Args:
        data_dir: data directory
        prefix: the file prefix name
        suffix: the file suffix name
    Returns:

    """
    logger.info('find files ...')

    files: List[str] = [file for file in os.listdir(data_dir) if file.startswith(prefix) and file.endswith(suffix)]
    if not files:
        logger.warning(f'there is no target files exist in: {data_dir}')
        return []

    files = [os.path.join(data_dir, file) for file in files]
    return files


def parse_date(sentence: str, single_date: bool = True) -> Union[None, datetime, List[datetime]]:
    """parse datetime from sentence"""
    results: List[ModelResult] = recognize_datetime(sentence, culture=Culture.Chinese)

    datetime_list: List[datetime] = []
    for result in results:
        if result.resolution and result.resolution['values']:
            values = result.resolution['values']
            datetime_list.append(
                values[0]
            )
    if not datetime_list:
        return None
    if single_date:
        return datetime_list[0]

    return datetime_list

def find_yaml_files(base_dir: str) -> List[str]:
    """find all of yaml files with recursion mode

    Args:
        base_dir (str): the base directory of files

    Returns:
        List[str]: the yaml files 
    """
    files_or_directories: List[str] = []
    # 1. find all files/directories in the current dir
    for file_or_dir in os.listdir(base_dir):

        path = os.path.join(base_dir, file_or_dir)
        if os.path.isdir(path):
            files_or_directories.extend(
                find_yaml_files(path)
            )
            continue

        # 2. if there is dir, find with recursion mode
        if file_or_dir.endswith('.yml') or file_or_dir.endswith('.yaml'):
            files_or_directories.append(path)
        
    return files_or_directories
    