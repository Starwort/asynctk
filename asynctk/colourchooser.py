from asynctk.commondialogue import AsyncDialogue


class Chooser(AsyncDialogue):
    "Ask for a colour"

    command = "tk_chooseColor"

    async def _fixoptions(self):
        try:
            # make sure initialcolor is a tk colour string
            colour = self.options["initialcolor"]
            if isinstance(colour, tuple):
                # assume an RGB triplet
                self.options["initialcolor"] = "#%02x%02x%02x" % colour
        except KeyError:
            pass

    async def _fixresult(self, widget, result):
        # result can be somethings: an empty tuple, an empty string or
        # a Tcl_Obj, so this somewhat weird check handles that
        if not result or not str(result):
            return None, None  # cancelled

        # to simplify application code, the colour chooser returns
        # an RGB tuple together with the Tk colour string
        r, g, b = widget.winfo_rgb(result)
        return (r / 256, g / 256, b / 256), str(result)


#
# convenience stuff


def askcolour(colour=None, **options):
    "Ask for a colour"

    if colour:
        options = options.copy()
        options["initialcolor"] = colour

    return Chooser(**options).show()
