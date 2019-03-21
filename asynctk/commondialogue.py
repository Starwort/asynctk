from asynctk import *


class AsyncDialogue:
    command = None

    def __init__(self, master=None, **options):
        self.master = master
        self.options = options
        if not master and options.get("parent") or options.get("master"):
            self.master = options.get("parent") or options.get("master")

    async def _fixoptions(self):
        pass  # hook

    async def _fixresult(self, widget, result):
        return result  # hook

    async def show(self, **options):

        # update instance options
        for k, v in options.items():
            self.options[k] = v

        await self._fixoptions()

        # we need a dummy widget to process the options properly
        # (at least as long as we use Tkinter 1.63)
        w = AsyncFrame(self.master)

        try:

            s = w.tk.call(self.command, *w._options(self.options))

            s = await self._fixresult(w, s)

        finally:

            try:
                # get rid of the widget
                await w.destroy()
            except:
                pass

        return s
