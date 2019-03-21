from .commondialogue import AsyncDialogue

#
# constants

# icons
ERROR = "error"
INFO = "info"
QUESTION = "question"
WARNING = "warning"

# types
ABORTRETRYIGNORE = "abortretryignore"
OK = "ok"
OKCANCEL = "okcancel"
RETRYCANCEL = "retrycancel"
YESNO = "yesno"
YESNOCANCEL = "yesnocancel"

# replies
ABORT = "abort"
RETRY = "retry"
IGNORE = "ignore"
OK = "ok"
CANCEL = "cancel"
YES = "yes"
NO = "no"


#
# message dialogue class


class AsyncMessage(AsyncDialogue):
    "A message box"

    command = "tk_messageBox"


#
# convenience stuff

# Rename _icon and _type options to allow overriding them in options
async def _show(title=None, message=None, _icon=None, _type=None, **options):
    if _icon and "icon" not in options:
        options["icon"] = _icon
    if _type and "type" not in options:
        options["type"] = _type
    if title:
        options["title"] = title
    if message:
        options["message"] = message
    res = await AsyncMessage(**options).show()
    # In some Tcl installations, yes/no is converted into a boolean.
    if isinstance(res, bool):
        if res:
            return YES
        return NO
    # In others we get a Tcl_Obj.
    return str(res)


async def showinfo(title=None, message=None, **options):
    "Show an info message"
    return await _show(title, message, INFO, OK, **options)


async def showwarning(title=None, message=None, **options):
    "Show a warning message"
    return await _show(title, message, WARNING, OK, **options)


async def showerror(title=None, message=None, **options):
    "Show an error message"
    return await _show(title, message, ERROR, OK, **options)


async def askquestion(title=None, message=None, **options):
    "Ask a question"
    return await _show(title, message, QUESTION, YESNO, **options)


async def askokcancel(title=None, message=None, **options):
    "Ask if operation should proceed; return true if the answer is ok"
    s = await _show(title, message, QUESTION, OKCANCEL, **options)
    return s == OK


async def askyesno(title=None, message=None, **options):
    "Ask a question; return true if the answer is yes"
    s = await _show(title, message, QUESTION, YESNO, **options)
    return s == YES


async def askyesnocancel(title=None, message=None, **options):
    "Ask a question; return true if the answer is yes, None if cancelled."
    s = await _show(title, message, QUESTION, YESNOCANCEL, **options)
    # s might be a Tcl index object, so convert it to a string
    s = str(s)
    if s == CANCEL:
        return None
    return s == YES


async def askretrycancel(title=None, message=None, **options):
    "Ask if operation should be retried; return true if the answer is yes"
    s = await _show(title, message, WARNING, RETRYCANCEL, **options)
    return s == RETRY
