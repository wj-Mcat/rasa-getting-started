"""action for datetime extractor"""
from typing import List, Dict, Text, Any

from rasa_sdk import Action, Tracker

import recognizers_suite as Recognizer
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class DateTimeAction(Action):
    """DateTime Action Extractor with """
    def name(self) -> Text:
        """name of DateTime Extractor """
        return "action_extract_datetime"

    async def run(
            self, dispatcher: "CollectingDispatcher",
            tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:

        sentence = tracker.latest_message[0]
        return []
