# PARSER SETTINGS
import re

PARSER_ALLOWED_USER_PARAMS = ["mention", "name", "display_name", "id", "level", "xp"]
PARSER_ALLOWED_GUILD_PARAMS = ["name", "id"]

PARSER_ALLOWED_PARAMS = {
    "user": PARSER_ALLOWED_USER_PARAMS,
    "guild": PARSER_ALLOWED_GUILD_PARAMS,
}

PARSER_PATTERN = re.compile(
    r"{(" + "|".join(
        map(
            re.escape, PARSER_ALLOWED_PARAMS.keys()
        )
    ) + r")\.(" + "|".join(
        attr for attrs in PARSER_ALLOWED_PARAMS.values() for attr in attrs
    ) + r")}"
)