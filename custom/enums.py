from __future__ import annotations

from typing import Type, TypeVar, TYPE_CHECKING

from discord.enums import Enum

__all__ = (
    "Environment",
    "DateTimeFormat",
    "LogType",
    "Effect",
    "EmbedSize",
    "TrackEndReason",
)

from voice import utilities

if TYPE_CHECKING:
    from .context import Context
    from .exceptions import EmbedError


NL = "\n"
EnumType = TypeVar("EnumType", bound=Enum)


class Environment(Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1


class DateTimeFormat(Enum):

    # Dates
    FULL_LONG_DATE = "dddd [the] Do [of] MMMM YYYY"
    PARTIAL_LONG_DATE = "dddd Do [of] MMMM YYYY"
    LONG_DATE = "dddd Do MMMM YYYY"
    FULL_SHORT_DATE = "DD/MM/YYYY"
    PARTIAL_SHORT_DATE = "D/M/YY"
    FULL_COMPUTER_DATE = "YYYY/MM/DD"
    PARTIAL_COMPUTER_DATE = "YY/M/D"

    # Times
    FULL_TIME = "hh:mm:ss A"
    PARTIAL_TIME = "hh:mm A"

    # Dates and times
    FULL_LONG_DATETIME = "dddd [the] Do [of] MMMM YYYY [at] hh:mm A"
    FULL_LONG_DATETIME_WITH_SECONDS = "dddd [the] Do [of] MMMM YYYY [at] hh:mm:ss A"
    PARTIAL_LONG_DATETIME = "dddd Do [of] MMMM YYYY [at] hh:mm A"
    PARTIAL_LONG_DATETIME_WITH_SECONDS = "dddd Do [of] MMMM YYYY [at] hh:mm:ss A"
    SHORT_DATETIME = "dddd Do MMMM YYYY [at] hh:mm A"
    SHORT_DATETIME_WITH_SECONDS = "dddd Do MMMM YYYY [at] hh:mm:ss A"


class LogType(Enum):
    DM = 0
    GUILD = 1
    ERROR = 2
    COMMAND = 3


class Effect(Enum):

    ROTATION = "8d"
    NIGHTCORE = "nightcore"
    MONO = "mono"
    LEFT_EAR = "left-ear"
    RIGHT_EAR = "right-ear"


class TrackEndReason(Enum):
    NORMAL = 0
    STUCK = 1
    EXCEPTION = 2
    REPLACED = 3


def convert_enum(
    cls: Type[EnumType],
    name: str,
    argument: str
) -> EnumType:

    try:
        return cls[argument.replace(" ", "_").upper()]
    except KeyError:
        options = NL.join(
            [f'- **{option.title()}**' for option in [enum.name.replace('_', ' ').lower() for enum in cls]]
        )
        raise EmbedError(
            description=f"**{utilities.truncate(argument, 10)}** is not a valid {name}.\n\n"
                        f"Valid options are:\n"
                        f"{options}"
        )


class EmbedSize(Enum):

    LARGE = 0
    MEDIUM = 1
    SMALL = 2
    IMAGE = 3

    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> EmbedSize:
        return convert_enum(cls, "embed size", argument)
