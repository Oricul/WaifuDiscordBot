from __future__ import print_function
import datetime

oldPrintFunc = print

def print(text, flush=True, **kwargs):
    if '\n' in text:
        oldPrintFunc("{0}>>\n{1}".format(datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y %I:%M:%S"), text), flush=flush, **kwargs)
    else:
        oldPrintFunc("{0}>> {1}".format(datetime.datetime.strftime(datetime.datetime.now(),"%m/%d/%Y %I:%M:%S"),text), flush=flush, **kwargs)
    return
