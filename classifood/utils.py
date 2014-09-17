from datetime import timedelta
import re


"""
Capitalizes the first letter of every word
"""
def cap_first_letter(s):
    if isinstance(s, str) or isinstance(s, unicode):
        letters = []
        letters.append(s[0].upper())

        for i in range(1, len(s)):
            if s[i-1] == ' ':
                letters.append(s[i].upper())
            else:
                letters.append(s[i])

        return ''.join(letters)

    else:
        return ''


"""
Escapes single quote
"""
def escape(s):
    if isinstance(s, str) or isinstance(s, unicode):
        if len(s) == 0:
            return s

        # re.sub(<pattern>, <replacement>, <input string>)
        s = re.sub('\\\'', '\\\'', s)
        s = re.sub('\\\\', '\\\\', s)

        return s

    else:
        return ''


"""
Unescapes single quote
"""
def unescape(s):
    if isinstance(s, str) or isinstance(s, unicode):
        if len(s) == 0:
            return s

        # re.sub(<pattern>, <replacement>, <input string>)
        s = re.sub('\\\\\\\'', '\'', s)
        s = re.sub('\\\\\\\\', r'\\', s) # re does not allow '\\' endings, therefore raw

        return s

    else:
        return ''


"""
Converts Python DateTime T_Delta to string
"""
def get_time_delta_str(t_delta):
    if not isinstance(t_delta, timedelta):
        return ''

    years = t_delta.days / 365
    months = t_delta.days % 365 / 30
    days = t_delta.days % 365 % 30
    hours = t_delta.seconds / 3600
    minutes = t_delta.seconds % 3600 / 60
    seconds = t_delta.seconds % 3600 % 60

    if years:
        return '{0} year(s) {1} month{s}'.format(years, months)

    if months:
        return '{0} month(s) {1} day(s)'.format(months, days)
            
    if days:
        return '{0} day(s) {1} hour(s)'.format(days, hours)

    if hours:
        return '{0} hour(s) {1} minute(s)'.format(hours, minutes)

    if minutes:
        return '{0} minute(s) {1} second(s)'.format(minutes, seconds)

    return '{0} second(s)'.format(seconds)

