from asynctk import *
from tkinter import _cnfmerge
import asyncio

DIALOGUE_ICON = "questhead"


class AsyncDialogue(AsyncWidget):
    """This may not actually be asynchronous, but I do not understand how it works."""

    def __init__(self, master=None, cnf={}, **kw):
        cnf = _cnfmerge((cnf, kw))
        self.widgetName = "__dialogue__"
        AsyncWidget._setup(self, master, cnf)
        self.num = self.tk.getint(
            self.tk.call(
                "tk_dialog",
                self._w,
                cnf["title"],
                cnf["text"],
                cnf["bitmap"],
                cnf["default"],
                *cnf["strings"]
            )
        )
        try:
            asyncio.ensure_future(AsyncWidget.destroy(self))
        except TclError:
            pass

    async def destroy(self):
        pass
