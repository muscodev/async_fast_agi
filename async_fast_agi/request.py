from typing import List
import time
from urllib.parse import urlparse,parse_qs
from panoramisk.fast_agi import Request as panoramiskRequest
import logging

logger = logging.getLogger(__name__)


class VerboseLevel:
    LOG_DEBUG = 0
    LOG_INFO = 1
    LOG_WARN = 2
    LOG_ERROR = 3
    LOG_CRITICAL = 4


class AGIValueError(ValueError):
    pass


def _convert_to_char(value, items):
    """
    Converts the given value into an ASCII character or raises `AGIValueError` with `items` as the
    payload.
    """
    try:
        value = value or "0"
        if value == "0":
            return None
        return chr(int(value))
    except ValueError:
        raise AGIValueError(
            f"Unable to convert Asterisk result to DTMF character: {value}"
        )


def _process_digit_list(digits):
    """
    Ensures that digit-lists are processed uniformly.
    """
    if type(digits) in (list, tuple, set, frozenset):
        digits = "".join([str(d) for d in digits])
    return f'"{digits}"'


class Request(panoramiskRequest):

    def __init__(self, app, headers, reader, writer, encoding="utf-8"):
        super().__init__(app, headers, reader, writer, encoding)
        self.channel = self.headers.get("agi_channel")
        self.args: List = [v for k,v in self.headers.items() if k.startswith('agi_arg_')]
        self.parsed_url = urlparse(self.headers.get('agi_request'))
        self.query_params = parse_qs(self.parsed_url.query)

    async def answer(self):
        return await self.send_command("ANSWER")

    async def hangup(self):
        return await self.send_command("HANGUP")

    async def EXEC(self, application, options=None):
        return await self.send_command(f"EXEC {application}")

    async def verbose(self, message, level=VerboseLevel.LOG_INFO):
        return await self.send_command(f'VERBOSE "{message}" "{level}" ')

    async def StartMusicOnHold(self, music_class=None):
        return await self.EXEC("StartMusicOnHold")

    async def StopMusicOnHold(self, music_class=None):
        return await self.EXEC("StopMusicOnHold")

    async def WaitForDigit(self, timeout=-1):
        """
        Waits for up to `timeout` milliseconds for a DTMF keypress to be received, returning that
        value. By default, this function blocks indefinitely.
        """

        response = await self.send_command(f'WAIT FOR DIGIT "{timeout}" ')

        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayDigits(self, digits, escape_digits=""):
        """
        Sends the 'SAY DIGITS' AGI command with the specified parameters.

        Args:
        - digits: The digits to be spelled out.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        digits = _process_digit_list(digits)
        escape_digits = _process_digit_list(escape_digits)
        response = await self.send_command(f'SAY DIGITS "{digits}" "{escape_digits}" ')
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayAlpha(self, text, escape_digits=""):
        """
        Sends the 'SAY ALPHA' AGI command with the specified parameters.

        Args:
        - text: The text to be spelled out.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        response = await self.send_command(f'SAY ALPHA "{text}" "{escape_digits}"')
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayDate(self, seconds, escape_digits=""):
        """
        Sends the 'SAY DATE' AGI command with the specified parameters.

        Args:
        - date: The date to be spelled out.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        if seconds is None:
            seconds = int(time.time())
        response = await self.send_command(f'SAY DATE "{seconds}" "{escape_digits}"')
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayDateTime(
        self, seconds, escape_digits="", datetime_format=None, timezone=None
    ):
        """
        Sends the 'SAY DATETIME' AGI command with the specified parameters.

        Args:
        - datetime: The date and time to be spelled out.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        if seconds is None:
            seconds = int(time.time())
        datetime_format = datetime_format or None
        timezone = timezone or None
        response = await self.send_command(
            f'SAY DATETIME "{seconds}" "{escape_digits}" "{datetime_format}" "{timezone}"'
        )
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayNumber(self, number, escape_digits=""):
        """
        Sends the 'SAY NUMBER' AGI command with the specified parameters.

        Args:
        - number: The number to be spelled out.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        number = _process_digit_list(number)
        escape_digits = _process_digit_list(escape_digits)
        response = await self.send_command(f'SAY NUMBER "{number}" "{escape_digits}"')
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayPhonetic(self, text, escape_digits=""):
        """
        Sends the 'SAY PHONETIC' AGI command with the specified parameters.

        Args:
        - text: The text to be spelled out phonetically.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        escape_digits = _process_digit_list(escape_digits)
        response = await self.send_command(f'SAY PHONETIC "{text}" "{escape_digits}"')
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def SayTime(self, seconds, escape_digits=""):
        """
        Sends the 'SAY TIME' AGI command with the specified parameters.

        Args:
        - time: The time to be spelled out.
        - escape_digits: Digits that allow the user to interrupt the playback (default: '').

        Returns:
        - None
        """
        escape_digits = _process_digit_list(escape_digits)
        if seconds is None:
            seconds = int(time.time())
        response = await self.send_command(f'SAY TIME "{time}" "{escape_digits}"')
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def StreamFile(self, filename, escape_digits="", sample_offset=0):
        """
        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)

        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received.

        `sample_offset` may be used to jump an arbitrary number of milliseconds into the audio data.

        The value returned is a tuple consisting of (dtmf_key:str, offset:int), where the offset is
        the number of milliseconds that elapsed since the start of playback, or None if playback
        completed successfully or the sample could not be opened.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        escape_digits = _process_digit_list(escape_digits)
        response = await self.send_command(
            f'STREAM FILE "{filename}" "{escape_digits}" "{sample_offset}" '
        )
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def GetOption(self, filename, escape_digits="", timeout=2000):
        """
        Stream file, prompt for DTMF, with timeout.

        Description¶
        Behaves similar to STREAM FILE but used with a timeout option.
        """
        escape_digits = _process_digit_list(escape_digits)
        response = await self.send_command(
            f'GET OPTION "{filename}" "{escape_digits}" "{timeout}" '
        )
        value, items = response.get("result")
        return _convert_to_char(value, items)

    async def GetData(self, filename, timeout=2000, max_digits=10):
        """
        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)

        `timeout` is the number of milliseconds to wait between DTMF presses or following the end
        of playback if no keys were pressed to interrupt playback prior to that point. It defaults
        to 2000.

        `max_digits` is the number of DTMF keypresses that will be accepted. It defaults to 255.

        The value returned is a tuple consisting of (dtmf_keys:str, timeout:bool). '#' is always
        interpreted as an end-of-event character and will never be present in the output.

        Response :

            (value, status=='timeout')

        """
        response = await self.send_command(
            f'GET DATA "{filename}"  "{timeout}"  "{max_digits}"'
        )
        value, status = response.get("result")
        return (value, status == "timeout")

    async def GetVariable(self, variable: str):
        response = await self.send_command(f'GET VARIABLE "{variable}"')
        code, value = response.get("result")
        if code == "1":
            return value
        return None

    async def SetVariable(self, variable: str, value: str):
        return await self.send_command(f'SET VARIABLE "{variable}" "{value}"')

