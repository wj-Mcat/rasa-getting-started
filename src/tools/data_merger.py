"""data merger for training data"""
from __future__ import annotations

import os
import shutil
from typing import Optional, List, Union
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader, RasaYAMLWriter
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.core.training_data.structures import StoryStep
from rasa.shared.core.training_data.story_reader.yaml_story_reader import StoryReader, YAMLStoryReader
from rasa.shared.core.training_data.story_writer.yaml_story_writer import StoryWriter, YAMLStoryWriter
from rasa.shared.core.domain import Domain
from tqdm import tqdm


from src.config import get_logger, root_dir
from src.utils import find_files, find_yaml_files

logger = get_logger()


class DataMerger:
    """DataMerger: merge training data"""
    def __init__(self, bots_dir: str = './bots', output_dir: str = 'data'):
        """
        merge the training data from bots

        Args:
            bots_dir: the path of bot training file, default path: ./bots
        """
        logger.info('init DataMerger ...')
        shutil.rmtree(output_dir, ignore_errors=True)

        os.makedirs(output_dir, exist_ok=True)
        
        self.yaml_files = find_yaml_files(bots_dir)
        for file in self.yaml_files:
            logger.info(f'finding file<{file}>')

        self.output_dir = output_dir

    def _merge_domain_files(self):
        logger.info('merge domain files ...')

        domain = Domain.load(self.yaml_files[0])
        bar = tqdm(total=len(self.yaml_files))
        bar.update()
        bar.set_description_str(f'loading file: {self.yaml_files[0]}')
        
        for yaml_file in self.yaml_files[1:]:
            bar.update()
            bar.set_description_str(f'loading file: {yaml_file}')

            domain = domain.merge(
                Domain.load(yaml_file),
                override=True
            )
        
        domain.persist('domain.yml')

    def _merge_nlu_files(self):
        logger.info('merge nlu files ...')
        reader = RasaYAMLReader()
        bar = tqdm(total=len(self.yaml_files))
        bar.update()
        bar.set_description_str(f'loading file: {self.yaml_files[0]}')
        
        training_data: TrainingData = reader.read(self.yaml_files[0])
        for yaml_file in self.yaml_files[1:]:
            bar.update()
            bar.set_description_str(f'loading file: {yaml_file}')

            training_data = training_data.merge(
                reader.read(yaml_file)
            )
        
        writer = RasaYAMLWriter()
        writer.dump(
            os.path.join(self.output_dir, 'nlu.yml'),
            training_data
        )

    def _merge_story_files(self):
        logger.info('merge story files ...')
        bar = tqdm(total=len(self.yaml_files))
        bar.update()
        bar.set_description_str(f'loading file: {self.yaml_files[0]}')
        
        # TODO: to fix it
        # 为了避免引用reader的问题，在此每次重新初始化reader
        steps: List[StoryStep] = YAMLStoryReader().read_from_file(self.yaml_files[0])
        for yaml_file in self.yaml_files[1:]:
            bar.update()
            bar.set_description_str(f'loading file: {yaml_file}')

            file_steps = YAMLStoryReader().read_from_file(yaml_file)
            if file_steps:
                steps.extend(
                    file_steps
                )
        
        logger.info(f'final steps: <{len(steps)}>')
        
        writer = YAMLStoryWriter()
        writer.dump(
            os.path.join(self.output_dir, 'stories.yml'), 
            steps
        )

    def merge(self):
        self._merge_domain_files()
        self._merge_nlu_files()
        self._merge_story_files()