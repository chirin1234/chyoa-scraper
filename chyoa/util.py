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

def get_choice_names(ref_list):
    names = []

    for ref in ref_list:
        names.append(" -> \"%s\"" % ref.name)

    return "\n".join(names)

