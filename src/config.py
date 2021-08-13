import os
from logging import Logger
from loguru import logger


root_dir = os.path.dirname(os.path.dirname(__file__))
test_dir = os.path.join(root_dir, 'tests')

docker_bot_name: str = 'rasa-bot-server'
docker_bot_port: int = os.environ.get('RASA_BOT_PORT', 51103)

docker_action_server_name: str = 'rasa-bot-action-server'
docker_action_server_port: int = os.environ.get('ACTION_SERVER_PORT', 51155)


def get_logger() -> Logger:
    """
    get system logger
    Returns:

    """
    return logger
