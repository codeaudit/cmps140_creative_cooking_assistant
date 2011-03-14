"""
Chatbot application object.
"""
import code
import logging
from nlg import NaturalLanguageGenerator
from nlu import NaturalLanguageUnderstander
from nlu.messages import *
from dm import DialogueManager

# Monkey-patch the Python 2.7 logger.getChild() method into the logger class,
# to maintain backwards-compatibility with Python 2.6.
#pylint: disable=C0103
if not hasattr(logging.Logger, "getChild"):
    def _getChild(self, suffix):
        """
        Logger.getChild() method, added in Python 2.7
        """
        if self.root is not self:
            suffix = '.'.join((self.name, suffix))
        return self.manager.getLogger(suffix)
    logging.Logger.getChild = _getChild


class Chatbot(object):
    """
    Object that represents an instance of the chatbot application.
    This object coordinates the flow of information through the
    different modules of the application, as well as configuration
    settings.
    """

    def __init__(self, db, logger, enable_debug=True):
        """
        Create a new instance of the chatbot application.

        >>> from database import Database
        >>> db = Database('sqlite:///:memory:')
        >>> bot = Chatbot(db, logging.getLogger())
        >>> response = bot.handle_input("Hi!")
        """
        self.enable_debug = enable_debug
        self.db = db
        self.log = logger
        self.nlg = NaturalLanguageGenerator(logger.getChild('nlg'))
        self.nlu = NaturalLanguageUnderstander(0.5, logger.getChild('nlu'))
        self.dm = DialogueManager(db, logger.getChild('dm'))
        self.log.debug("Chatbot instantiated")
        self.last_bot_output = ""

        # Register the NLU messages we want
        self.nlu.register_message(YesNoMessage)
        self.nlu.register_message(SearchMessage)
        self.nlu.register_message(SystemMessage)

    def handle_input(self, user_input):
        """
        Given a string of user input, return the output string.
        """
        if self.enable_debug and user_input == "/debug":
            self.debug_prompt()
            # Return the chatbot's last output utterance, to remind the user
            # where they were before they entered the debugging prompt.
            return self.last_bot_output
        self.log.info('%12s = "%s"' % ('user_input', user_input))
        self.last_user_input = user_input
        parsed_input = self.nlu.parse_input(user_input)
        # If the input could not be parsed, we could include code here to
        # use a general-purpose chatbot that can guide the user back to the
        # topic.
        self.log.debug('%12s = "%s"' % ('parsed_input', parsed_input))
        content_plan = self.dm.plan_response(parsed_input)
        self.log.debug('%12s = "%s"' % ('content_plan', content_plan))
        bot_response = self.nlg.generate_response(content_plan)
        self.log.info('%12s = "%s"' % ('bot_response', bot_response))
        self.last_bot_output = bot_response
        return bot_response

    def debug_prompt(self):
        """
        Enters an interactive debugging prompt. You can access system
        components through local variables.  Type ctrl-D to exit the debug
        prompt.
        """
        variables = {
            'db': self.db,
            'dm': self.dm,
            'nlg': self.nlg,
            'nlu': self.nlu,
            'chatbot': self
        }
        banner = "Debugging Console (db, dm, nlg, nlu, chatbot)"
        code.interact(banner=banner, local=variables)

    def get_greeting(self):
        """
        Return an initial message from the chatbot.
        """
        return "Hello!"
