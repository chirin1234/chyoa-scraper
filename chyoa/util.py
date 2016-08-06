__all__ = ["abridge", "get_elapsed_time"]

import time

def abridge(string):
    if len(string) < 20:
        return string
    else:
        return string[:20] + "..."

def get_elapsed_time(seconds):
    result = []
    if seconds > 3600:
        hours = seconds / 3600
        seconds %= 3600

        if hours == 1:
            result.append("1 hour")
        else:
            result.append("%d hours" % hours)
    if seconds > 60:
        minutes = seconds / 60
        seconds %= 60

        if minutes == 1:
            result.append("1 minute")
        else:
            result.append("%d minutes" % minutes)

    if result:
        return ", ".join(result) + (" and %.3f seconds" % seconds)
    else:
        return "%.3f seconds" % seconds

def get_choice_names(choices):
    lines = []

    for choice in choices:
        lines.append(" -> \"%s\"" % choice[1])

    if lines:
        lines.append("")
        return "\n".join(lines)
    else:
        return "(none)\n"

