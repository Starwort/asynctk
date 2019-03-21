# BROKEN

from asynctk import *
from .dialogue import AsyncDialogue
from . import commondialogue

import os
import fnmatch


dialoguestates = {}


class AsyncFileDialogue:

    """Standard file selection dialogue -- no checks on selected file.
    Usage:
        d = FileDialogue(master)
        fname = d.go(dir_or_file, pattern, default, key)
        if fname is None: ...cancelled...
        else: ...open file...
    All arguments to go() are optional.
    The 'key' argument specifies a key in the global dictionary
    'dialoguestates', which keeps track of the values for the directory
    and pattern arguments, overriding the values passed in (it does
    not keep track of the default argument!).  If no key is specified,
    the dialogue keeps no memory of previous state.  Note that memory is
    kept even when the dialogue is cancelled.  (All this emulates the
    behaviour of the Macintosh file selection dialogues.)
    """

    title = "File Selection Dialogue"

    def __init__(self, master, title=None):
        if title is None:
            title = self.title
        self.master = master
        self.directory = None

        self.top = AsyncToplevel(master)
        self.top.title(title)
        self.top.iconname(title)

        self.botframe = AsyncFrame(self.top)
        self.botframe.pack(side=BOTTOM, fill=X)

        self.selection = AsyncEntry(self.top)
        self.selection.pack(side=BOTTOM, fill=X)
        self.selection.bind("<Return>", self.ok_event)

        self.filter = AsyncEntry(self.top)
        self.filter.pack(side=TOP, fill=X)
        self.filter.bind("<Return>", self.filter_command)

        self.midframe = AsyncFrame(self.top)
        self.midframe.pack(expand=YES, fill=BOTH)

        self.filesbar = AsyncScrollbar(self.midframe)
        self.filesbar.pack(side=RIGHT, fill=Y)
        self.files = AsyncListbox(
            self.midframe, exportselection=0, yscrollcommand=(self.filesbar, "set")
        )
        self.files.pack(side=RIGHT, expand=YES, fill=BOTH)
        btags = self.files.bindtags()
        self.files.bindtags(btags[1:] + btags[:1])
        self.files.bind("<ButtonRelease-1>", self.files_select_event)
        self.files.bind("<Double-ButtonRelease-1>", self.files_double_event)
        self.filesbar.config(command=(self.files, "yview"))

        self.dirsbar = AsyncScrollbar(self.midframe)
        self.dirsbar.pack(side=LEFT, fill=Y)
        self.dirs = AsyncListbox(
            self.midframe, exportselection=0, yscrollcommand=(self.dirsbar, "set")
        )
        self.dirs.pack(side=LEFT, expand=YES, fill=BOTH)
        self.dirsbar.config(command=(self.dirs, "yview"))
        btags = self.dirs.bindtags()
        self.dirs.bindtags(btags[1:] + btags[:1])
        self.dirs.bind("<ButtonRelease-1>", self.dirs_select_event)
        self.dirs.bind("<Double-ButtonRelease-1>", self.dirs_double_event)

        self.ok_button = AsyncButton(self.botframe, text="OK", command=self.ok_command)
        self.ok_button.pack(side=LEFT)
        self.filter_button = AsyncButton(
            self.botframe, text="Filter", command=self.filter_command
        )
        self.filter_button.pack(side=LEFT, expand=YES)
        self.cancel_button = AsyncButton(
            self.botframe, text="Cancel", command=self.cancel_command
        )
        self.cancel_button.pack(side=RIGHT)

        self.top.protocol("WM_DELETE_WINDOW", self.cancel_command)
        # XXX Are the following okay for a general audience?
        self.top.bind("<Alt-w>", self.cancel_command)
        self.top.bind("<Alt-W>", self.cancel_command)

    async def go(self, dir_or_file=os.curdir, pattern="*", default="", key=None):
        if key and key in dialoguestates:
            self.directory, pattern = dialoguestates[key]
        else:
            dir_or_file = os.path.expanduser(dir_or_file)
            if os.path.isdir(dir_or_file):
                self.directory = dir_or_file
            else:
                self.directory, default = os.path.split(dir_or_file)
        await self.set_filter(self.directory, pattern)
        await self.set_selection(default)
        await self.filter_command()
        self.selection.focus_set()
        self.top.wait_visibility()  # window needs to be visible for the grab
        self.top.grab_set()
        self.how = None
        await self.master.wait_window()  # Exited by self.quit(how)
        if key:
            directory, pattern = self.get_filter()
            if self.how:
                directory = os.path.dirname(self.how)
            dialoguestates[key] = directory, pattern
        await self.top.destroy()
        return self.how

    async def quit(self, how=None):
        self.how = how
        await self.master.quit()  # Exit mainloop()

    async def dirs_double_event(self, event):
        await self.filter_command()

    async def dirs_select_event(self, event):
        dir, pat = self.get_filter()
        subdir = self.dirs.get("active")
        dir = os.path.normpath(os.path.join(self.directory, subdir))
        self.set_filter(dir, pat)

    async def files_double_event(self, event):
        await self.ok_command()

    async def files_select_event(self, event):
        file = self.files.get("active")
        self.set_selection(file)

    async def ok_event(self, event):
        await self.ok_command()

    async def ok_command(self):
        await self.quit(self.get_selection())

    async def filter_command(self, event=None):
        dir, pat = await self.get_filter()
        try:
            names = os.listdir(dir)
        except OSError:
            self.master.bell()
            return
        self.directory = dir
        await self.set_filter(dir, pat)
        names.sort()
        subdirs = [os.pardir]
        matchingfiles = []
        for name in names:
            fullname = os.path.join(dir, name)
            if os.path.isdir(fullname):
                subdirs.append(name)
            elif fnmatch.fnmatch(name, pat):
                matchingfiles.append(name)
        self.dirs.delete(0, END)
        for name in subdirs:
            self.dirs.insert(END, name)
        self.files.delete(0, END)
        for name in matchingfiles:
            self.files.insert(END, name)
        head, tail = os.path.split(await self.get_selection())
        if tail == os.curdir:
            tail = ""
        await self.set_selection(tail)

    async def get_filter(self):
        filter = self.filter.get()
        filter = os.path.expanduser(filter)
        if filter[-1:] == os.sep or os.path.isdir(filter):
            filter = os.path.join(filter, "*")
        return os.path.split(filter)

    async def get_selection(self):
        file = self.selection.get()
        file = os.path.expanduser(file)
        return file

    async def cancel_command(self, event=None):
        await self.quit()

    async def set_filter(self, dir, pat):
        if not os.path.isabs(dir):
            try:
                pwd = os.getcwd()
            except OSError:
                pwd = None
            if pwd:
                dir = os.path.join(pwd, dir)
                dir = os.path.normpath(dir)
        self.filter.delete(0, END)
        self.filter.insert(END, os.path.join(dir or os.curdir, pat or "*"))

    async def set_selection(self, file):
        self.selection.delete(0, END)
        self.selection.insert(END, os.path.join(self.directory, file))


class AsyncLoadFileDialogue(AsyncFileDialogue):

    """File selection dialogue which checks that the file exists."""

    title = "Load File Selection Dialogue"

    async def ok_command(self):
        file = self.get_selection()
        if not os.path.isfile(file):
            await self.master.bell()
        else:
            await self.quit(file)


class AsyncSaveFileDialogue(AsyncFileDialogue):

    """File selection dialogue which checks that the file may be created."""

    title = "Save File Selection Dialogue"

    async def ok_command(self):
        file = self.get_selection()
        if os.path.exists(file):
            if os.path.isdir(file):
                self.master.bell()
                return
            d = AsyncDialogue(
                self.top,
                title="Overwrite Existing File Question",
                text="Overwrite existing file %r?" % (file,),
                bitmap="questhead",
                default=1,
                strings=("Yes", "Cancel"),
            )
            if d.num != 0:
                return
        else:
            head, tail = os.path.split(file)
            if not os.path.isdir(head):
                self.master.bell()
                return
        await self.quit(file)


# For the following classes and modules:
#
# options (all have default values):
#
# - defaultextension: added to filename if not explicitly given
#
# - filetypes: sequence of (label, pattern) tuples.  the same pattern
#   may occur with several patterns.  use "*" as pattern to indicate
#   all files.
#
# - initialdir: initial directory.  preserved by dialogue instance.
#
# - initialfile: initial file (ignored by the open dialogue).  preserved
#   by dialogue instance.
#
# - parent: which window to place the dialogue on top of
#
# - title: dialogue title
#
# - multiple: if true user may select more than one file
#
# options for the directory chooser:
#
# - initialdir, parent, title: see above
#
# - mustexist: if true, user must pick an existing directory
#


class _AsyncDialogue(commondialogue.AsyncDialogue):
    async def _fixoptions(self):
        try:
            # make sure "filetypes" is a tuple
            self.options["filetypes"] = tuple(self.options["filetypes"])
        except KeyError:
            pass

    async def _fixresult(self, widget, result):
        if result:
            # keep directory and filename until next time
            # convert Tcl path objects to strings
            try:
                result = result.string
            except AttributeError:
                # it already is a string
                pass
            path, file = os.path.split(result)
            self.options["initialdir"] = path
            self.options["initialfile"] = file
        self.filename = result  # compatibility
        return result


#
# file dialogues


class AsyncOpen(_AsyncDialogue):
    "Ask for a filename to open"

    command = "tk_getOpenFile"

    async def _fixresult(self, widget, result):
        if isinstance(result, tuple):
            # multiple results:
            result = tuple([getattr(r, "string", r) for r in result])
            if result:
                path, file = os.path.split(result[0])
                self.options["initialdir"] = path
                # don't set initialfile or filename, as we have multiple of these
            return result
        if not widget.tk.wantobjects() and "multiple" in self.options:
            # Need to split result explicitly
            return self._fixresult(widget, widget.tk.splitlist(result))
        return _AsyncDialogue._fixresult(self, widget, result)


class AsyncSaveAs(_AsyncDialogue):
    "Ask for a filename to save as"

    command = "tk_getSaveFile"


# the directory dialogue has its own _fix routines.
class AsyncDirectory(commondialogue.AsyncDialogue):
    "Ask for a directory"

    command = "tk_chooseDirectory"

    async def _fixresult(self, widget, result):
        if result:
            # convert Tcl path objects to strings
            try:
                result = result.string
            except AttributeError:
                # it already is a string
                pass
            # keep directory until next time
            self.options["initialdir"] = result
        self.directory = result  # compatibility
        return result


# convenience stuff


async def askopenfilename(**options):
    "Ask for a filename to open"

    return await AsyncOpen(**options).show()


async def asksaveasfilename(**options):
    "Ask for a filename to save as"

    return await AsyncSaveAs(**options).show()


async def askopenfilenames(**options):
    """Ask for multiple filenames to open
    Returns a list of filenames or empty list if
    cancel button selected
    """
    options["multiple"] = 1
    return await AsyncOpen(**options).show()


# FIXME: are the following perhaps a bit too convenient?


async def askopenfile(mode="r", **options):
    "Ask for a filename to open, and returned the opened file"

    filename = await AsyncOpen(**options).show()
    if filename:
        return open(filename, mode)
    return None


async def askopenfiles(mode="r", **options):
    """Ask for multiple filenames and return the open file
    objects
    returns a list of open file objects or an empty list if
    cancel selected
    """

    files = await askopenfilenames(**options)
    if files:
        ofiles = []
        for filename in files:
            ofiles.append(open(filename, mode))
        files = ofiles
    return files


async def asksaveasfile(mode="w", **options):
    "Ask for a filename to save as, and returned the opened file"

    filename = await AsyncSaveAs(**options).show()
    if filename:
        return open(filename, mode)
    return None


async def askdirectory(**options):
    "Ask for a directory, and return the file name"
    return await AsyncDirectory(**options).show()


# --------------------------------------------------------------------
# test stuff


def test():
    """Simple test program."""
    import asyncio

    root = AsyncTk()
    root.withdraw()
    print("created root")
    fd = AsyncLoadFileDialogue(root)
    print("created load dialogue")
    loadfile = asyncio.get_event_loop().run_until_complete(fd.go(key="test"))
    print("finished load dialogue")
    fd = AsyncSaveFileDialogue(root)
    print("created save dialogue")
    savefile = asyncio.get_event_loop().run_until_complete(fd.go(key="test"))
    print("finished save dialogue")
    print(loadfile, savefile)

    # Since the file name may contain non-ASCII characters, we need
    # to find an encoding that likely supports the file name, and
    # displays correctly on the terminal.

    # Start off with UTF-8
    enc = "utf-8"
    import sys

    # See whether CODESET is defined
    try:
        import locale

        locale.setlocale(locale.LC_ALL, "")
        enc = locale.nl_langinfo(locale.CODESET)
    except (ImportError, AttributeError):
        pass

    # dialogue for opening files

    openfilename = asyncio.get_event_loop().run_until_complete(
        askopenfilename(filetypes=[("all files", "*")])
    )
    try:
        fp = open(openfilename, "r")
        fp.close()
    except:
        print("Could not open File: ")
        print(sys.exc_info()[1])

    print("open", openfilename.encode(enc))

    # dialogue for saving files

    saveasfilename = asyncio.get_event_loop().run_until_complete(asksaveasfilename())
    print("saveas", saveasfilename.encode(enc))


if __name__ == "__main__":
    test()
