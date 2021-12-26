"""test yaml merger"""
from __future__ import annotations

import os
from typing import Optional, List

from rasa.shared.core.training_data.structures import StoryStep
from rasa.shared.nlu.training_data.formats.rasa_yaml import (   # type: ignore
    RasaYAMLReader, RasaYAMLWriter
)
from rasa.shared.nlu.training_data.training_data import TrainingData    # type: ignore
from rasa.shared.core.training_data.story_reader.yaml_story_reader import YAMLStoryReader
from rasa.shared.core.domain import Domain

from src.config import test_dir
from src.utils import find_yaml_files


def test_simple_merger():
    """test simple merger"""
    reader = RasaYAMLReader()

    files = [
        os.path.join(test_dir, 'data/nlu/simple-nlu.yaml'),
        os.path.join(test_dir, 'data/nlu/weather.yaml')
    ]
    output_file = os.path.join(test_dir, 'data/nlu/result.yaml')
    training_data: Optional[TrainingData] = None

    for file in files:
        file_training_data: TrainingData = reader.read(file)

        if not training_data:
            training_data = file_training_data
        else:
            training_data = training_data.merge(file_training_data)

    writer = RasaYAMLWriter()
    writer.dump(output_file, training_data)

def test_mixin():
    reader = RasaYAMLReader()
    file = os.path.join(test_dir, 'data/nlu/mix.yaml')
    
    training_data: TrainingData = reader.read(file)
    assert len(training_data.responses) == 1
    assert len(training_data.intents) == 1
    


def test_story_merger():
    """test story merger code"""
    reader = YAMLStoryReader()

    training_data: List[StoryStep] = reader.read_from_file(
        os.path.join(test_dir, 'data/stories/story.yml'), skip_validation=True
    )
    assert len(training_data) == 2


def test_file_finder():
    files = find_yaml_files(test_dir)
    assert len(files) == 3


def test_domain_reader():
    domain_file = os.path.join(test_dir, 'data/domains/domain.yaml')
    reader: Domain = Domain.load(domain_file)
    assert len(reader.intents) == 7

    training_data: TrainingData = RasaYAMLReader().read(domain_file)
    assert len(training_data.intents) == 2

    
