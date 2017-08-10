import re
import time
import datetime
import calendar

def date_to_rfc822(value, format="%a, %d %b %Y %H:%M:%S +0000"):
    if type(value) == int or type(value) == float:
        return time.strftime(format, time.gmtime(value))
    elif type(value) == str:
        return time.strftime(format, time.strptime(value))
    elif type(value) in [datetime.date, datetime.datetime]:
        return value.strftime(format)
    elif type(value) == time.struct_time:
        return time.strftime(format, value)
    else:
        raise Exception("Unknwon value type!")

def date_to_iso8601(value, format="%Y-%m-%dT%H:%M:%S%z"):
    if type(value) == int or type(value) == float:
        return time.strftime(format, time.gmtime(value))
    elif type(value) == str:
        return time.strftime(format, time.strptime(value))
    elif type(value) in [datetime.date, datetime.datetime]:
        return value.strftime(format)
    elif type(value) == time.struct_time:
        return time.strftime(format, value)
    else:
        raise Exception("Unknwon value type!")

def xml_escape(value):
    if not value:
        return ''
    else:
        XML_CHARS = {
            "<": '&lt;',
            ">": '&gt;',
            "'": '&apos;',
            '"': '&quot;',
            '&': '&amp;',
        }
        def sub(match):
            return XML_CHARS.get(match)
        return re.sub(r"[<>'\"&]", sub, str(value))

def escape_quote(value):
    def sub(match):
        return r'\"'
    if not value:
        return ''
    else:
        return re.sub(r'"', sub, value)
