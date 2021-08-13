"""action for default fallback"""
from typing import List, Dict, Text, Any

from rasa_sdk import Action, Tracker

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class DateTimeAction(Action):
    """DateTime Action Extractor with """
    def name(self) -> Text:
        """name of DateTime Extractor """
        return "action_default_fallback"

    async def run(
            self, dispatcher: "CollectingDispatcher",
            tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:

        dispatcher.utter_message('对不起，我暂时没有理解您的意思')

        return []

