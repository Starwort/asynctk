"""A ScrolledText widget feels like a text widget but also has a
vertical scroll bar on its right.  (Later, options may be added to
add a horizontal bar as well, to make the bars disappear
automatically when not needed, to move them to the other side of the
window, etc.)
Configuration options are passed to the Text widget.
A Frame widget is inserted between the master and the text, to hold
the Scrollbar widget.
Most methods calls are inherited from the Text widget; Pack, Grid and
Place methods are redirected to the Frame widget however.
"""
__all__ = ["AsyncScrolledText"]

from asynctk import AsyncFrame, AsyncText, AsyncScrollbar, Pack, Grid, Place
from tkinter.constants import RIGHT, LEFT, Y, BOTH


class AsyncScrolledText(AsyncText):
    def __init__(self, master=None, **kw):
        self.frame = AsyncFrame(master)
        self.vbar = AsyncScrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({"yscrollcommand": self.vbar.set})
        AsyncText.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar["command"] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(AsyncText).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != "_" and m != "config" and m != "configure":
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


def example():
    from tkinter.constants import END
    from asynctk import AsyncTk

    root = AsyncTk()
    stext = AsyncScrolledText(root, bg="white", height=10)
    stext.insert(END, __doc__)
    stext.pack(fill=BOTH, side=LEFT, expand=True)
    root.focus_set()
    root.mainloop()


if __name__ == "__main__":
    example()
