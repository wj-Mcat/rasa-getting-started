"""data merger for training data"""
from __future__ import annotations

import os
import shutil
from typing import Optional, List, Union
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader, RasaYAMLWriter
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.core.training_data.structures import StoryStep
from rasa.shared.core.training_data.story_reader.yaml_story_reader import YAMLStoryReader
from rasa.shared.core.training_data.story_writer.yaml_story_writer import YAMLStoryWriter

from src.config import get_logger, root_dir
from src.utils import find_files

logger = get_logger()


class DataMerger:
    """DataMerger: merge training data"""
    def __init__(self, bots_dir: str = 'bots', data_dir: str = 'data', action_dir: str = 'actions'):
        """
        merge the training data from bots

        Args:
            bots_dir: the path of bot training file, default path: ./bots
        """
        logger.info('init DataMerger ...')

        self.bots_dir: str = os.path.join(root_dir, bots_dir)

        self.data_dir: str = os.path.join(root_dir, data_dir)
        self.action_dir: str = os.path.join(root_dir, action_dir)

        # remove all of cached data dir
        shutil.rmtree(self.data_dir, ignore_errors=True)

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.action_dir, exist_ok=True)
        # check all of sub dir in data dir
        os.makedirs(os.path.join(self.data_dir, 'nlu'))
        os.makedirs(os.path.join(self.data_dir, 'stories'))
        os.makedirs(os.path.join(self.data_dir, 'domain'))

    @staticmethod
    def merge_nlu_files(files: Union[str, List[str]], output_file: str):
        """
        get training data from single/multiple files
        Args:
            files: str/List[str] which should contains the training data
            output_file: str, the output dur

        Returns:

        """
        logger.info(f'get training data with files: {files}')

        training_files: List[str] = []
        if isinstance(files, str):
            training_files.append(files)
        else:
            training_files.extend(files)

        reader = RasaYAMLReader()

        training_data: Optional[TrainingData] = None

        for file in files:
            file_training_data: TrainingData = reader.read(file)

            if not training_data:
                training_data = file_training_data
            else:
                training_data = training_data.merge(file_training_data)

        if not training_data:
            return

        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)

        writer = RasaYAMLWriter()
        writer.dump(output_file, training_data)

    @staticmethod
    def merge_story_files(files: Union[str, List[str]], output_file: str):
        """
        merge story files
        Args:
            files: file path that story file
            output_file: target output file
        """
        logger.info(f'get story training data with files: {files}')

        training_files: List[str] = []
        if isinstance(files, str):
            training_files.append(files)
        else:
            training_files.extend(files)

        reader = YAMLStoryReader()

        story_steps: List[StoryStep] = []

        for file in files:
            story_steps.extend(reader.read_from_file(file, skip_validation=True))

        if not story_steps:
            return

        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)

        writer = YAMLStoryWriter()
        writer.dump(output_file, story_steps)

    def merge(self):
        """merge function which handle the main loop"""
        logger.info('merge nlu/story files ...')
        function_names: List[str] = os.listdir(self.bots_dir)

        for function_name in function_names:
            # 1. find nlu/story files
            function_dir = os.path.join(self.bots_dir, function_name)
            if not os.path.isdir(function_dir):
                continue

            nlu_files: List[str] = find_files(function_dir, prefix='nlu')
            story_files: List[str] = find_files(function_dir, prefix='story')
            action_files: List[str] = find_files(function_dir, prefix='action')

            # 2. merge them
            DataMerger.merge_nlu_files(
                nlu_files,
                os.path.join(self.data_dir, 'nlu', f'{function_name}.yaml')
            )
            DataMerger.merge_story_files(
                story_files,
                os.path.join(self.data_dir, 'stories', f'{function_name}.yaml')
            )

            for action_file in action_files:
                action_file_name = os.path.basename(action_file)
                shutil.copyfile(
                    action_file,
                    os.path.join(self.action_dir, f'{function_name}_{action_file_name}')
                )

            # 3. read the nlu data

            domain_file = os.path.join(function_dir, 'domain.yaml')
            if os.path.exists(domain_file):
                shutil.copy(
                    domain_file,
                    os.path.join(self.data_dir, 'domain', f'{function_name}.yaml')
                )
