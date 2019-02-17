from tkinter import *
import asyncio
CENTRE = CENTER
WRITEABLE = WRITABLE
class AsyncTKException(TclError):
    pass

class AsyncMisc:
    """Internal class.
    Base class which defines methods common for interior widgets."""

    # used for generating child widget names
    _last_child_ids = None

    # XXX font command?
    _tclCommands = None

    async def destroy(self):
        """Internal function.
        Delete all Tcl commands created for
        this widget in the Tcl interpreter."""
        self.is_destroyed = True
        if self._tclCommands is not None:
            for name in self._tclCommands:
                #print '- Tkinter: deleted command', name
                self.tk.deletecommand(name)
            self._tclCommands = None

    def deletecommand(self, name):
        """Internal function.
        Delete the Tcl command provided in NAME."""
        #print '- Tkinter: deleted command', name
        self.tk.deletecommand(name)
        try:
            self._tclCommands.remove(name)
        except ValueError:
            pass

    def tk_strictMotif(self, boolean=None):
        """Set Tcl internal variable, whether the look and feel
        should adhere to Motif.
        A parameter of 1 means adhere to Motif (e.g. no colour
        change if mouse passes over slider).
        Returns the set value."""
        return self.tk.getboolean(self.tk.call(
            'set', 'tk_strictMotif', boolean))

    def tk_bisque(self):
        """Change the colour scheme to light brown as used in Tk 3.6 and before."""
        self.tk.call('tk_bisque')

    def tk_setPalette(self, *args, **kw):
        """Set a new colour scheme for all widget elements.
        A single colour as argument will cause that all colours of Tk
        widget elements are derived from this.
        Alternatively several keyword parameters and its associated
        colours can be given. The following keywords are valid:
        activeBackground, foreground, selectColor,
        activeForeground, highlightBackground, selectBackground,
        background, highlightColor, selectForeground,
        disabledForeground, insertBackground, troughColor."""
        self.tk.call(('tk_setPalette',)
              + _flatten(args) + _flatten(list(kw.items())))

    async def wait_variable(self, var):
        """Wait until the variable is modified.
        A parameter of type IntVar, StringVar, DoubleVar or
        BooleanVar must be given."""
        if not isinstance(var, Variable):
            raise AsyncTKException("'var' is not of type Variable")
        target = var.get()
        while var.get() == target:
            await asyncio.sleep(0.01)
    waitvar = wait_variable # XXX b/w compat

    async def wait_window(self, window=None):
        """Wait until a WIDGET is destroyed.
        If no parameter is given self is used."""
        if window is None:
            window = self
        while not window.is_destroyed:
            await asyncio.sleep(0.01)

    async def wait_visibility(self, window=None):
        """Wait until the visibility of a WIDGET changes
        (e.g. it appears).
        If no parameter is given self is used."""
        if window is None:
            window = self
        vis = window.visibility
        while window.visibility != vis:
            await asyncio.sleep(0.01)
    def setvar(self, name='PY_VAR', value='1'):
        """Set Tcl variable NAME to VALUE."""
        self.tk.setvar(name, value)

    def getvar(self, name='PY_VAR'):
        """Return value of Tcl variable NAME."""
        return self.tk.getvar(name)

    def getint(self, s):
        try:
            return self.tk.getint(s)
        except TclError as exc:
            raise ValueError(str(exc))

    def getdouble(self, s):
        try:
            return self.tk.getdouble(s)
        except TclError as exc:
            raise ValueError(str(exc))

    def getboolean(self, s):
        """Return a boolean value for Tcl boolean values true and false given as parameter."""
        try:
            return self.tk.getboolean(s)
        except TclError:
            raise ValueError("invalid literal for getboolean()")

    def focus_set(self):
        """Direct input focus to this widget.
        If the application currently does not have the focus
        this widget will get the focus if the application gets
        the focus through the window manager."""
        self.tk.call('focus', self._w)
    focus = focus_set # XXX b/w compat?

    def focus_force(self):
        """Direct input focus to this widget even if the
        application does not have the focus. Use with
        caution!"""
        self.tk.call('focus', '-force', self._w)

    def focus_get(self):
        """Return the widget which has currently the focus in the
        application.
        Use focus_displayof to allow working with several
        displays. Return None if application does not have
        the focus."""
        name = self.tk.call('focus')
        if name == 'none' or not name: return None
        return self._nametowidget(name)

    def focus_displayof(self):
        """Return the widget which has currently the focus on the
        display where this widget is located.
        Return None if the application does not have the focus."""
        name = self.tk.call('focus', '-displayof', self._w)
        if name == 'none' or not name: return None
        return self._nametowidget(name)

    def focus_lastfor(self):
        """Return the widget which would have the focus if top level
        for this widget gets the focus from the window manager."""
        name = self.tk.call('focus', '-lastfor', self._w)
        if name == 'none' or not name: return None
        return self._nametowidget(name)

    def tk_focusFollowsMouse(self):
        """The widget under mouse will get automatically focus. Can not
        be disabled easily."""
        self.tk.call('tk_focusFollowsMouse')

    def tk_focusNext(self):
        """Return the next widget in the focus order which follows
        widget which has currently the focus.
        The focus order first goes to the next child, then to
        the children of the child recursively and then to the
        next sibling which is higher in the stacking order.  A
        widget is omitted if it has the takefocus resource set
        to 0."""
        name = self.tk.call('tk_focusNext', self._w)
        if not name: return None
        return self._nametowidget(name)

    def tk_focusPrev(self):
        """Return previous widget in the focus order. See tk_focusNext for details."""
        name = self.tk.call('tk_focusPrev', self._w)
        if not name: return None
        return self._nametowidget(name)

    async def after(self, ms, func=None, *args, iscoro=False):
        """Call function once after given time.
        MS specifies the time in milliseconds. FUNC gives the
        function which shall be called. Additional parameters
        are given as parameters to the function call.  Return
        identifier to cancel scheduling with after_cancel."""
        if not func:
            await asyncio.sleep(ms*0.001)
            return None
        else:
            async def callit():
                await asyncio.sleep(ms*0.001)
                if not iscoro:
                    return func(*args)
                else:
                    return await func(*args)
            return asyncio.ensure_future(callit())

    def after_idle(self, func, *args):
        """Call FUNC once if the Tcl main loop has no event to
        process.
        Return an identifier to cancel the scheduling with
        after_cancel."""
        return self.after('idle', func, *args)

    def after_cancel(self, id):
        """Cancel scheduling of function identified with ID.
        Identifier returned by after or after_idle must be
        given as first parameter.
        """
        if not id:
            raise ValueError('id must be a valid identifier returned from '
                             'after or after_idle')
        try:
            data = self.tk.call('after', 'info', id)
            script = self.tk.splitlist(data)[0]
            self.deletecommand(script)
        except TclError:
            pass
        self.tk.call('after', 'cancel', id)

    def bell(self, displayof=0):
        """Ring a display's bell."""
        self.tk.call(('bell',) + self._displayof(displayof))

    # Clipboard handling:
    def clipboard_get(self, **kw):
        """Retrieve data from the clipboard on window's display.
        The window keyword defaults to the root window of the Tkinter
        application.
        The type keyword specifies the form in which the data is
        to be returned and should be an atom name such as STRING
        or FILE_NAME.  Type defaults to STRING, except on X11, where the default
        is to try UTF8_STRING and fall back to STRING.
        This command is equivalent to:
        selection_get(CLIPBOARD)
        """
        if 'type' not in kw and self._windowingsystem == 'x11':
            try:
                kw['type'] = 'UTF8_STRING'
                return self.tk.call(('clipboard', 'get') + self._options(kw))
            except TclError:
                del kw['type']
        return self.tk.call(('clipboard', 'get') + self._options(kw))

    def clipboard_clear(self, **kw):
        """Clear the data in the Tk clipboard.
        A widget specified for the optional displayof keyword
        argument specifies the target display."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'clear') + self._options(kw))

    def clipboard_append(self, string, **kw):
        """Append STRING to the Tk clipboard.
        A widget specified at the optional displayof keyword
        argument specifies the target display. The clipboard
        can be retrieved with selection_get."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'append') + self._options(kw)
              + ('--', string))
    # XXX grab current w/o window argument

    def grab_current(self):
        """Return widget which has currently the grab in this application
        or None."""
        name = self.tk.call('grab', 'current', self._w)
        if not name: return None
        return self._nametowidget(name)

    def grab_release(self):
        """Release grab for this widget if currently set."""
        self.tk.call('grab', 'release', self._w)

    def grab_set(self):
        """Set grab for this widget.
        A grab directs all events to this and descendant
        widgets in the application."""
        self.tk.call('grab', 'set', self._w)

    def grab_set_global(self):
        """Set global grab for this widget.
        A global grab directs all events to this and
        descendant widgets on the display. Use with caution -
        other applications do not get events anymore."""
        self.tk.call('grab', 'set', '-global', self._w)

    def grab_status(self):
        """Return None, "local" or "global" if this widget has
        no, a local or a global grab."""
        status = self.tk.call('grab', 'status', self._w)
        if status == 'none': status = None
        return status

    def option_add(self, pattern, value, priority = None):
        """Set a VALUE (second parameter) for an option
        PATTERN (first parameter).
        An optional third parameter gives the numeric priority
        (defaults to 80)."""
        self.tk.call('option', 'add', pattern, value, priority)

    def option_clear(self):
        """Clear the option database.
        It will be reloaded if option_add is called."""
        self.tk.call('option', 'clear')

    def option_get(self, name, className):
        """Return the value for an option NAME for this widget
        with CLASSNAME.
        Values with higher priority override lower values."""
        return self.tk.call('option', 'get', self._w, name, className)

    def option_readfile(self, fileName, priority = None):
        """Read file FILENAME into the option database.
        An optional second parameter gives the numeric
        priority."""
        self.tk.call('option', 'readfile', fileName, priority)

    def selection_clear(self, **kw):
        """Clear the current X selection."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        self.tk.call(('selection', 'clear') + self._options(kw))

    def selection_get(self, **kw):
        """Return the contents of the current X selection.
        A keyword parameter selection specifies the name of
        the selection and defaults to PRIMARY.  A keyword
        parameter displayof specifies a widget on the display
        to use. A keyword parameter type specifies the form of data to be
        fetched, defaulting to STRING except on X11, where UTF8_STRING is tried
        before STRING."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        if 'type' not in kw and self._windowingsystem == 'x11':
            try:
                kw['type'] = 'UTF8_STRING'
                return self.tk.call(('selection', 'get') + self._options(kw))
            except TclError:
                del kw['type']
        return self.tk.call(('selection', 'get') + self._options(kw))

    def selection_handle(self, command, **kw):
        """Specify a function COMMAND to call if the X
        selection owned by this widget is queried by another
        application.
        This function must return the contents of the
        selection. The function will be called with the
        arguments OFFSET and LENGTH which allows the chunking
        of very long selections. The following keyword
        parameters can be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        name = self._register(command)
        self.tk.call(('selection', 'handle') + self._options(kw)
              + (self._w, name))

    def selection_own(self, **kw):
        """Become owner of X selection.
        A keyword parameter selection specifies the name of
        the selection (default PRIMARY)."""
        self.tk.call(('selection', 'own') +
                 self._options(kw) + (self._w,))

    def selection_own_get(self, **kw):
        """Return owner of X selection.
        The following keyword parameter can
        be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        name = self.tk.call(('selection', 'own') + self._options(kw))
        if not name: return None
        return self._nametowidget(name)

    def send(self, interp, cmd, *args):
        """Send Tcl command CMD to different interpreter INTERP to be executed."""
        return self.tk.call(('send', interp, cmd) + args)

    def lower(self, belowThis=None):
        """Lower this widget in the stacking order."""
        self.tk.call('lower', self._w, belowThis)

    def tkraise(self, aboveThis=None):
        """Raise this widget in the stacking order."""
        self.tk.call('raise', self._w, aboveThis)

    lift = tkraise

    def winfo_atom(self, name, displayof=0):
        """Return integer which represents atom NAME."""
        args = ('winfo', 'atom') + self._displayof(displayof) + (name,)
        return self.tk.getint(self.tk.call(args))

    def winfo_atomname(self, id, displayof=0):
        """Return name of atom with identifier ID."""
        args = ('winfo', 'atomname') \
               + self._displayof(displayof) + (id,)
        return self.tk.call(args)

    def winfo_cells(self):
        """Return number of cells in the colourmap for this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'cells', self._w))

    def winfo_children(self):
        """Return a list of all widgets which are children of this widget."""
        result = []
        for child in self.tk.splitlist(
            self.tk.call('winfo', 'children', self._w)):
            try:
                # Tcl sometimes returns extra windows, e.g. for
                # menus; those need to be skipped
                result.append(self._nametowidget(child))
            except KeyError:
                pass
        return result

    def winfo_class(self):
        """Return window class name of this widget."""
        return self.tk.call('winfo', 'class', self._w)

    def winfo_colourmapfull(self):
        """Return true if at the last colour request the colourmap was full."""
        return self.tk.getboolean(
            self.tk.call('winfo', 'colormapfull', self._w))

    def winfo_containing(self, rootX, rootY, displayof=0):
        """Return the widget which is at the root coordinates ROOTX, ROOTY."""
        args = ('winfo', 'containing') \
               + self._displayof(displayof) + (rootX, rootY)
        name = self.tk.call(args)
        if not name: return None
        return self._nametowidget(name)

    def winfo_depth(self):
        """Return the number of bits per pixel."""
        return self.tk.getint(self.tk.call('winfo', 'depth', self._w))

    def winfo_exists(self):
        """Return true if this widget exists."""
        return self.tk.getint(
            self.tk.call('winfo', 'exists', self._w))

    def winfo_fpixels(self, number):
        """Return the number of pixels for the given distance NUMBER
        (e.g. "3c") as float."""
        return self.tk.getdouble(self.tk.call(
            'winfo', 'fpixels', self._w, number))

    def winfo_geometry(self):
        """Return geometry string for this widget in the form "widthxheight+X+Y"."""
        return self.tk.call('winfo', 'geometry', self._w)

    def winfo_height(self):
        """Return height of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'height', self._w))

    def winfo_id(self):
        """Return identifier ID for this widget."""
        return int(self.tk.call('winfo', 'id', self._w), 0)

    def winfo_interps(self, displayof=0):
        """Return the name of all Tcl interpreters for this display."""
        args = ('winfo', 'interps') + self._displayof(displayof)
        return self.tk.splitlist(self.tk.call(args))

    def winfo_ismapped(self):
        """Return true if this widget is mapped."""
        return self.tk.getint(
            self.tk.call('winfo', 'ismapped', self._w))

    def winfo_manager(self):
        """Return the window manager name for this widget."""
        return self.tk.call('winfo', 'manager', self._w)

    def winfo_name(self):
        """Return the name of this widget."""
        return self.tk.call('winfo', 'name', self._w)

    def winfo_parent(self):
        """Return the name of the parent of this widget."""
        return self.tk.call('winfo', 'parent', self._w)

    def winfo_pathname(self, id, displayof=0):
        """Return the pathname of the widget given by ID."""
        args = ('winfo', 'pathname') \
               + self._displayof(displayof) + (id,)
        return self.tk.call(args)

    def winfo_pixels(self, number):
        """Rounded integer value of winfo_fpixels."""
        return self.tk.getint(
            self.tk.call('winfo', 'pixels', self._w, number))

    def winfo_pointerx(self):
        """Return the x coordinate of the pointer on the root window."""
        return self.tk.getint(
            self.tk.call('winfo', 'pointerx', self._w))

    def winfo_pointerxy(self):
        """Return a tuple of x and y coordinates of the pointer on the root window."""
        return self._getints(
            self.tk.call('winfo', 'pointerxy', self._w))

    def winfo_pointery(self):
        """Return the y coordinate of the pointer on the root window."""
        return self.tk.getint(
            self.tk.call('winfo', 'pointery', self._w))

    def winfo_reqheight(self):
        """Return requested height of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'reqheight', self._w))

    def winfo_reqwidth(self):
        """Return requested width of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'reqwidth', self._w))

    def winfo_rgb(self, colour):
        """Return tuple of decimal values for red, green, blue for
        colour in this widget."""
        return self._getints(
            self.tk.call('winfo', 'rgb', self._w, colour))

    def winfo_rootx(self):
        """Return x coordinate of upper left corner of this widget on the
        root window."""
        return self.tk.getint(
            self.tk.call('winfo', 'rootx', self._w))

    def winfo_rooty(self):
        """Return y coordinate of upper left corner of this widget on the
        root window."""
        return self.tk.getint(
            self.tk.call('winfo', 'rooty', self._w))

    def winfo_screen(self):
        """Return the screen name of this widget."""
        return self.tk.call('winfo', 'screen', self._w)

    def winfo_screencells(self):
        """Return the number of the cells in the colourmap of the screen
        of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'screencells', self._w))

    def winfo_screendepth(self):
        """Return the number of bits per pixel of the root window of the
        screen of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'screendepth', self._w))

    def winfo_screenheight(self):
        """Return the number of pixels of the height of the screen of this widget
        in pixel."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenheight', self._w))

    def winfo_screenmmheight(self):
        """Return the number of pixels of the height of the screen of
        this widget in mm."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenmmheight', self._w))

    def winfo_screenmmwidth(self):
        """Return the number of pixels of the width of the screen of
        this widget in mm."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenmmwidth', self._w))

    def winfo_screenvisual(self):
        """Return one of the strings directcolour, grayscale, pseudocolour,
        staticcolour, staticgray, or truecolour for the default
        colourmodel of this screen."""
        return self.tk.call('winfo', 'screenvisual', self._w)

    def winfo_screenwidth(self):
        """Return the number of pixels of the width of the screen of
        this widget in pixel."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenwidth', self._w))

    def winfo_server(self):
        """Return information of the X-Server of the screen of this widget in
        the form "XmajorRminor vendor vendorVersion"."""
        return self.tk.call('winfo', 'server', self._w)

    def winfo_toplevel(self):
        """Return the toplevel widget of this widget."""
        return self._nametowidget(self.tk.call(
            'winfo', 'toplevel', self._w))

    def winfo_viewable(self):
        """Return true if the widget and all its higher ancestors are mapped."""
        return self.tk.getint(
            self.tk.call('winfo', 'viewable', self._w))

    def winfo_visual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, or truecolor for the
        colourmodel of this widget."""
        return self.tk.call('winfo', 'visual', self._w)

    def winfo_visualid(self):
        """Return the X identifier for the visual for this widget."""
        return self.tk.call('winfo', 'visualid', self._w)

    def winfo_visualsavailable(self, includeids=False):
        """Return a list of all visuals available for the screen
        of this widget.
        Each item in the list consists of a visual name (see winfo_visual), a
        depth and if includeids is true is given also the X identifier."""
        data = self.tk.call('winfo', 'visualsavailable', self._w,
                            'includeids' if includeids else None)
        data = [self.tk.splitlist(x) for x in self.tk.splitlist(data)]
        return [self.__winfo_parseitem(x) for x in data]

    def __winfo_parseitem(self, t):
        """Internal function."""
        return t[:1] + tuple(map(self.__winfo_getint, t[1:]))

    def __winfo_getint(self, x):
        """Internal function."""
        return int(x, 0)

    def winfo_vrootheight(self):
        """Return the height of the virtual root window associated with this
        widget in pixels. If there is no virtual root window return the
        height of the screen."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrootheight', self._w))

    def winfo_vrootwidth(self):
        """Return the width of the virtual root window associated with this
        widget in pixel. If there is no virtual root window return the
        width of the screen."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrootwidth', self._w))

    def winfo_vrootx(self):
        """Return the x offset of the virtual root relative to the root
        window of the screen of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrootx', self._w))

    def winfo_vrooty(self):
        """Return the y offset of the virtual root relative to the root
        window of the screen of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrooty', self._w))

    def winfo_width(self):
        """Return the width of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'width', self._w))

    def winfo_x(self):
        """Return the x coordinate of the upper left corner of this widget
        in the parent."""
        return self.tk.getint(
            self.tk.call('winfo', 'x', self._w))

    def winfo_y(self):
        """Return the y coordinate of the upper left corner of this widget
        in the parent."""
        return self.tk.getint(
            self.tk.call('winfo', 'y', self._w))

    def update(self):
        """Enter event loop until all pending events have been processed by Tcl."""
        self.tk.call('update')

    def update_idletasks(self):
        """Enter event loop until all idle callbacks have been called. This
        will update the display of windows but not process events caused by
        the user."""
        self.tk.call('update', 'idletasks')

    def bindtags(self, tagList=None):
        """Set or get the list of bindtags for this widget.
        With no argument return the list of all bindtags associated with
        this widget. With a list of strings as argument the bindtags are
        set to this list. The bindtags determine in which order events are
        processed (see bind)."""
        if tagList is None:
            return self.tk.splitlist(
                self.tk.call('bindtags', self._w))
        else:
            self.tk.call('bindtags', self._w, tagList)

    def _bind(self, what, sequence, func, add, needcleanup=1):
        """Internal function."""
        if isinstance(func, str):
            self.tk.call(what + (sequence, func))
        elif func:
            funcid = self._register(func, self._substitute,
                        needcleanup)
            cmd = ('%sif {"[%s %s]" == "break"} break\n'
                   %
                   (add and '+' or '',
                funcid, self._subst_format_str))
            self.tk.call(what + (sequence, cmd))
            return funcid
        elif sequence:
            return self.tk.call(what + (sequence,))
        else:
            return self.tk.splitlist(self.tk.call(what))

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC.
        SEQUENCE is a string of concatenated event
        patterns. An event pattern is of the form
        <MODIFIER-MODIFIER-TYPE-DETAIL> where MODIFIER is one
        of Control, Mod2, M2, Shift, Mod3, M3, Lock, Mod4, M4,
        Button1, B1, Mod5, M5 Button2, B2, Meta, M, Button3,
        B3, Alt, Button4, B4, Double, Button5, B5 Triple,
        Mod1, M1. TYPE is one of Activate, Enter, Map,
        ButtonPress, Button, Expose, Motion, ButtonRelease
        FocusIn, MouseWheel, Circulate, FocusOut, Property,
        colourmap, Gravity Reparent, Configure, KeyPress, Key,
        Unmap, Deactivate, KeyRelease Visibility, Destroy,
        Leave and DETAIL is the button number for ButtonPress,
        ButtonRelease and DETAIL is the Keysym for KeyPress and
        KeyRelease. Examples are
        <Control-Button-1> for pressing Control and mouse button 1 or
        <Alt-A> for pressing A and the Alt key (KeyPress can be omitted).
        An event pattern can also be a virtual event of the form
        <<AString>> where AString can be arbitrary. This
        event can be generated by event_generate.
        If events are concatenated they must appear shortly
        after each other.
        FUNC will be called if the event sequence occurs with an
        instance of Event as argument. If the return value of FUNC is
        "break" no further bound function is invoked.
        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function or whether
        it will replace the previous function.
        Bind will return an identifier to allow deletion of the bound function with
        unbind without memory leak.
        If FUNC or SEQUENCE is omitted the bound function or list
        of bound events are returned."""

        return self._bind(('bind', self._w), sequence, func, add)

    def unbind(self, sequence, funcid=None):
        """Unbind for this widget for event SEQUENCE  the
        function identified with FUNCID."""
        self.tk.call('bind', self._w, sequence, '')
        if funcid:
            self.deletecommand(funcid)

    def bind_all(self, sequence=None, func=None, add=None):
        """Bind to all widgets at an event SEQUENCE a call to function FUNC.
        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function or whether
        it will replace the previous function. See bind for the return value."""
        return self._bind(('bind', 'all'), sequence, func, add, 0)

    def unbind_all(self, sequence):
        """Unbind for all widgets for event SEQUENCE all functions."""
        self.tk.call('bind', 'all' , sequence, '')

    def bind_class(self, className, sequence=None, func=None, add=None):
        """Bind to widgets with bindtag CLASSNAME at event
        SEQUENCE a call of function FUNC. An additional
        boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function or
        whether it will replace the previous function. See bind for
        the return value."""

        return self._bind(('bind', className), sequence, func, add, 0)

    def unbind_class(self, className, sequence):
        """Unbind for all widgets with bindtag CLASSNAME for event SEQUENCE
        all functions."""
        self.tk.call('bind', className , sequence, '')

    def mainloop(self, n=0):
        """Call the mainloop of Tk."""
        loop = self.loop or asyncio.get_event_loop()
        async def runme():
            while True:
                await self.tick()
        loop.run_until_complete(runme())

    def quit(self):
        """Quit the Tcl interpreter. All widgets will be destroyed."""
        self.tk.quit()

    def _getints(self, string):
        """Internal function."""
        if string:
            return tuple(map(self.tk.getint, self.tk.splitlist(string)))

    def _getdoubles(self, string):
        """Internal function."""
        if string:
            return tuple(map(self.tk.getdouble, self.tk.splitlist(string)))

    def _getboolean(self, string):
        """Internal function."""
        if string:
            return self.tk.getboolean(string)

    def _displayof(self, displayof):
        """Internal function."""
        if displayof:
            return ('-displayof', displayof)
        if displayof is None:
            return ('-displayof', self._w)
        return ()

    @property
    def _windowingsystem(self):
        """Internal function."""
        try:
            return self._root()._windowingsystem_cached
        except AttributeError:
            ws = self._root()._windowingsystem_cached = \
                        self.tk.call('tk', 'windowingsystem')
            return ws

    def _options(self, cnf, kw = None):
        """Internal function."""
        if kw:
            cnf = _cnfmerge((cnf, kw))
        else:
            cnf = _cnfmerge(cnf)
        res = ()
        for k, v in cnf.items():
            if v is not None:
                if k[-1] == '_': k = k[:-1]
                if callable(v):
                    v = self._register(v)
                elif isinstance(v, (tuple, list)):
                    nv = []
                    for item in v:
                        if isinstance(item, int):
                            nv.append(str(item))
                        elif isinstance(item, str):
                            nv.append(_stringify(item))
                        else:
                            break
                    else:
                        v = ' '.join(nv)
                res = res + ('-'+k, v)
        return res

    def nametowidget(self, name):
        """Return the Tkinter instance of a widget identified by
        its Tcl name NAME."""
        name = str(name).split('.')
        w = self

        if not name[0]:
            w = w._root()
            name = name[1:]

        for n in name:
            if not n:
                break
            w = w.children[n]

        return w

    _nametowidget = nametowidget

    def _register(self, func, subst=None, needcleanup=1):
        """Return a newly created Tcl function. If this
        function is called, the Python function FUNC will
        be executed. An optional function SUBST can
        be given which will be executed before FUNC."""
        f = CallWrapper(func, subst, self).__call__
        name = repr(id(f))
        try:
            func = func.__func__
        except AttributeError:
            pass
        try:
            name = name + func.__name__
        except AttributeError:
            pass
        self.tk.createcommand(name, f)
        if needcleanup:
            if self._tclCommands is None:
                self._tclCommands = []
            self._tclCommands.append(name)
        return name

    register = _register

    def _root(self):
        """Internal function."""
        w = self
        while w.master: w = w.master
        return w
    _subst_format = ('%#', '%b', '%f', '%h', '%k',
             '%s', '%t', '%w', '%x', '%y',
             '%A', '%E', '%K', '%N', '%W', '%T', '%X', '%Y', '%D')
    _subst_format_str = " ".join(_subst_format)

    def _substitute(self, *args):
        """Internal function."""
        if len(args) != len(self._subst_format): return args
        getboolean = self.tk.getboolean

        getint = self.tk.getint
        def getint_event(s):
            """Tk changed behavior in 8.4.2, returning "??" rather more often."""
            try:
                return getint(s)
            except (ValueError, TclError):
                return s

        nsign, b, f, h, k, s, t, w, x, y, A, E, K, N, W, T, X, Y, D = args
        # Missing: (a, c, d, m, o, v, B, R)
        e = Event()
        # serial field: valid for all events
        # number of button: ButtonPress and ButtonRelease events only
        # height field: Configure, ConfigureRequest, Create,
        # ResizeRequest, and Expose events only
        # keycode field: KeyPress and KeyRelease events only
        # time field: "valid for events that contain a time field"
        # width field: Configure, ConfigureRequest, Create, ResizeRequest,
        # and Expose events only
        # x field: "valid for events that contain an x field"
        # y field: "valid for events that contain a y field"
        # keysym as decimal: KeyPress and KeyRelease events only
        # x_root, y_root fields: ButtonPress, ButtonRelease, KeyPress,
        # KeyRelease, and Motion events
        e.serial = getint(nsign)
        e.num = getint_event(b)
        try: e.focus = getboolean(f)
        except TclError: pass
        e.height = getint_event(h)
        e.keycode = getint_event(k)
        e.state = getint_event(s)
        e.time = getint_event(t)
        e.width = getint_event(w)
        e.x = getint_event(x)
        e.y = getint_event(y)
        e.char = A
        try: e.send_event = getboolean(E)
        except TclError: pass
        e.keysym = K
        e.keysym_num = getint_event(N)
        try:
            e.type = EventType(T)
        except ValueError:
            e.type = T
        try:
            e.widget = self._nametowidget(W)
        except KeyError:
            e.widget = W
        e.x_root = getint_event(X)
        e.y_root = getint_event(Y)
        try:
            e.delta = getint(D)
        except (ValueError, TclError):
            e.delta = 0
        return (e,)

    def _report_exception(self):
        """Internal function."""
        exc, val, tb = sys.exc_info()
        root = self._root()
        root.report_callback_exception(exc, val, tb)

    def _getconfigure(self, *args):
        """Call Tcl configure command and return the result as a dict."""
        cnf = {}
        for x in self.tk.splitlist(self.tk.call(*args)):
            x = self.tk.splitlist(x)
            cnf[x[0][1:]] = (x[0][1:],) + x[1:]
        return cnf

    def _getconfigure1(self, *args):
        x = self.tk.splitlist(self.tk.call(*args))
        return (x[0][1:],) + x[1:]

    def _configure(self, cmd, cnf, kw):
        """Internal function."""
        if kw:
            cnf = _cnfmerge((cnf, kw))
        elif cnf:
            cnf = _cnfmerge(cnf)
        if cnf is None:
            return self._getconfigure(_flatten((self._w, cmd)))
        if isinstance(cnf, str):
            return self._getconfigure1(_flatten((self._w, cmd, '-'+cnf)))
        self.tk.call(_flatten((self._w, cmd)) + self._options(cnf))
    # These used to be defined in Widget:

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget.
        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """
        return self._configure('configure', cnf, kw)

    config = configure

    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        return self.tk.call(self._w, 'cget', '-' + key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        """Return a list of all resource names of this widget."""
        splitlist = self.tk.splitlist
        return [splitlist(x)[0][1:] for x in
                splitlist(self.tk.call(self._w, 'configure'))]

    def __str__(self):
        """Return the window path name of this widget."""
        return self._w

    def __repr__(self):
        return '<%s.%s object %s>' % (
            self.__class__.__module__, self.__class__.__qualname__, self._w)

    # Pack methods that apply to the master
    _noarg_ = ['_noarg_']

    def pack_propagate(self, flag=_noarg_):
        """Set or get the status for propagation of geometry information.
        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        is given the current setting will be returned.
        """
        if flag is AsyncMisc._noarg_:
            return self._getboolean(self.tk.call(
                'pack', 'propagate', self._w))
        else:
            self.tk.call('pack', 'propagate', self._w, flag)

    propagate = pack_propagate

    def pack_slaves(self):
        """Return a list of all slaves of this widget
        in its packing order."""
        return [self._nametowidget(x) for x in
                self.tk.splitlist(
                   self.tk.call('pack', 'slaves', self._w))]

    slaves = pack_slaves

    # Place method that applies to the master
    def place_slaves(self):
        """Return a list of all slaves of this widget
        in its packing order."""
        return [self._nametowidget(x) for x in
                self.tk.splitlist(
                   self.tk.call(
                       'place', 'slaves', self._w))]

    # Grid methods that apply to the master

    def grid_anchor(self, anchor=None): # new in Tk 8.5
        """The anchor value controls how to place the grid within the
        master when no row/column has any weight.
        The default anchor is nw."""
        self.tk.call('grid', 'anchor', self._w, anchor)

    anchor = grid_anchor

    def grid_bbox(self, column=None, row=None, col2=None, row2=None):
        """Return a tuple of integer coordinates for the bounding
        box of this widget controlled by the geometry manager grid.
        If COLUMN, ROW is given the bounding box applies from
        the cell with row and column 0 to the specified
        cell. If COL2 and ROW2 are given the bounding box
        starts at that cell.
        The returned integers specify the offset of the upper left
        corner in the master widget and the width and height.
        """
        args = ('grid', 'bbox', self._w)
        if column is not None and row is not None:
            args = args + (column, row)
        if col2 is not None and row2 is not None:
            args = args + (col2, row2)
        return self._getints(self.tk.call(*args)) or None

    bbox = grid_bbox

    def _gridconvvalue(self, value):
        if isinstance(value, (str, _tkinter.Tcl_Obj)):
            try:
                svalue = str(value)
                if not svalue:
                    return None
                elif '.' in svalue:
                    return self.tk.getdouble(svalue)
                else:
                    return self.tk.getint(svalue)
            except (ValueError, TclError):
                pass
        return value

    def _grid_configure(self, command, index, cnf, kw):
        """Internal function."""
        if isinstance(cnf, str) and not kw:
            if cnf[-1:] == '_':
                cnf = cnf[:-1]
            if cnf[:1] != '-':
                cnf = '-'+cnf
            options = (cnf,)
        else:
            options = self._options(cnf, kw)
        if not options:
            return _splitdict(
                self.tk,
                self.tk.call('grid', command, self._w, index),
                conv=self._gridconvvalue)
        res = self.tk.call(
                  ('grid', command, self._w, index)
                  + options)
        if len(options) == 1:
            return self._gridconvvalue(res)

    def grid_columnconfigure(self, index, cnf={}, **kw):
        """Configure column INDEX of a grid.
        Valid resources are minsize (minimum size of the column),
        weight (how much does additional space propagate to this column)
        and pad (how much space to let additionally)."""
        return self._grid_configure('columnconfigure', index, cnf, kw)

    columnconfigure = grid_columnconfigure

    def grid_location(self, x, y):
        """Return a tuple of column and row which identify the cell
        at which the pixel at position X and Y inside the master
        widget is located."""
        return self._getints(
            self.tk.call(
                'grid', 'location', self._w, x, y)) or None

    def grid_propagate(self, flag=_noarg_):
        """Set or get the status for propagation of geometry information.
        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        is given, the current setting will be returned.
        """
        if flag is AsyncMisc._noarg_:
            return self._getboolean(self.tk.call(
                'grid', 'propagate', self._w))
        else:
            self.tk.call('grid', 'propagate', self._w, flag)

    def grid_rowconfigure(self, index, cnf={}, **kw):
        """Configure row INDEX of a grid.
        Valid resources are minsize (minimum size of the row),
        weight (how much does additional space propagate to this row)
        and pad (how much space to let additionally)."""
        return self._grid_configure('rowconfigure', index, cnf, kw)

    rowconfigure = grid_rowconfigure

    def grid_size(self):
        """Return a tuple of the number of column and rows in the grid."""
        return self._getints(
            self.tk.call('grid', 'size', self._w)) or None

    size = grid_size

    def grid_slaves(self, row=None, column=None):
        """Return a list of all slaves of this widget
        in its packing order."""
        args = ()
        if row is not None:
            args = args + ('-row', row)
        if column is not None:
            args = args + ('-column', column)
        return [self._nametowidget(x) for x in
                self.tk.splitlist(self.tk.call(
                   ('grid', 'slaves', self._w) + args))]

    # Support for the "event" command, new in Tk 4.2.
    # By Case Roole.

    def event_add(self, virtual, *sequences):
        """Bind a virtual event VIRTUAL (of the form <<Name>>)
        to an event SEQUENCE such that the virtual event is triggered
        whenever SEQUENCE occurs."""
        args = ('event', 'add', virtual) + sequences
        self.tk.call(args)

    def event_delete(self, virtual, *sequences):
        """Unbind a virtual event VIRTUAL from SEQUENCE."""
        args = ('event', 'delete', virtual) + sequences
        self.tk.call(args)

    def event_generate(self, sequence, **kw):
        """Generate an event SEQUENCE. Additional
        keyword arguments specify parameter of the event
        (e.g. x, y, rootx, rooty)."""
        args = ('event', 'generate', self._w, sequence)
        for k, v in kw.items():
            args = args + ('-%s' % k, str(v))
        self.tk.call(args)

    def event_info(self, virtual=None):
        """Return a list of all virtual events or the information
        about the SEQUENCE bound to the virtual event VIRTUAL."""
        return self.tk.splitlist(
            self.tk.call('event', 'info', virtual))

    # Image related commands

    def image_names(self):
        """Return a list of all existing image names."""
        return self.tk.splitlist(self.tk.call('image', 'names'))

    def image_types(self):
        """Return a list of all available image types (e.g. photo bitmap)."""
        return self.tk.splitlist(self.tk.call('image', 'types'))

class AsyncTk(AsyncMisc, Wm):
    """Toplevel widget of Tk which represents mostly the main window
    of an application. It has an associated Tcl interpreter."""
    _w = '.'

    def __init__(self, screenName=None, baseName=None, className='Tk',
                 useTk=1, sync=0, use=None):
        """Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will
        be created. BASENAME will be used for the identification of the profile file (see
        readprofile).
        It is constructed from sys.argv[0] without extensions if None is given. CLASSNAME
        is the name of the widget class."""
        self.master = None
        self.children = {}
        self._tkloaded = 0
        self.is_destroyed = False
        self.tl_children = []
        # to avoid recursions in the getattr code in case of failure, we
        # ensure that self.tk is always _something_.
        self.tk = None
        if baseName is None:
            import os
            baseName = os.path.basename(sys.argv[0])
            baseName, ext = os.path.splitext(baseName)
            if ext not in ('.py', '.pyc'):
                baseName = baseName + ext
        interactive = 0
        self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
        if useTk:
            self._loadtk()
        if not sys.flags.ignore_environment:
            # Issue #16248: Honor the -E flag to avoid code injection.
            self.readprofile(baseName, className)

    def loadtk(self):
        if not self._tkloaded:
            self.tk.loadtk()
            self._loadtk()

    def _loadtk(self):
        self._tkloaded = 1
        global _default_root
        # Version sanity checks
        tk_version = self.tk.getvar('tk_version')
        if tk_version != _tkinter.TK_VERSION:
            raise RuntimeError("tk.h version (%s) doesn't match libtk.a version (%s)"
                               % (_tkinter.TK_VERSION, tk_version))
        # Under unknown circumstances, tcl_version gets coerced to float
        tcl_version = str(self.tk.getvar('tcl_version'))
        if tcl_version != _tkinter.TCL_VERSION:
            raise RuntimeError("tcl.h version (%s) doesn't match libtcl.a version (%s)" \
                               % (_tkinter.TCL_VERSION, tcl_version))
        # Create and register the tkerror and exit commands
        # We need to inline parts of _register here, _ register
        # would register differently-named commands.
        if self._tclCommands is None:
            self._tclCommands = []
        self.tk.createcommand('tkerror', _tkerror)
        self.tk.createcommand('exit', _exit)
        self._tclCommands.append('tkerror')
        self._tclCommands.append('exit')
        if _support_default_root and not _default_root:
            _default_root = self
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    async def tick(self):
        self.update()
        for i in self.tl_children:
            i.update()

    async def destroy(self):
        """Destroy this and all descendants widgets. This will
        end the application of this Tcl interpreter."""
        self.is_destroyed = True
        for c in list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        await AsyncMisc.destroy(self)
        global _default_root
        if _support_default_root and _default_root is self:
            _default_root = None

    def readprofile(self, baseName, className):
        """Internal function. It reads BASENAME.tcl and CLASSNAME.tcl into
        the Tcl Interpreter and calls exec on the contents of BASENAME.py and
        CLASSNAME.py if such a file exists in the home directory."""
        import os
        if 'HOME' in os.environ: home = os.environ['HOME']
        else: home = os.curdir
        class_tcl = os.path.join(home, '.%s.tcl' % className)
        class_py = os.path.join(home, '.%s.py' % className)
        base_tcl = os.path.join(home, '.%s.tcl' % baseName)
        base_py = os.path.join(home, '.%s.py' % baseName)
        dir = {'self': self}
        exec('from tkinter import *', dir)
        if os.path.isfile(class_tcl):
            self.tk.call('source', class_tcl)
        if os.path.isfile(class_py):
            exec(open(class_py).read(), dir)
        if os.path.isfile(base_tcl):
            self.tk.call('source', base_tcl)
        if os.path.isfile(base_py):
            exec(open(base_py).read(), dir)

    def report_callback_exception(self, exc, val, tb):
        """Report callback exception on sys.stderr.
        Applications may want to override this internal function, and
        should when sys.stderr is None."""
        import traceback
        print("Exception in Tkinter callback", file=sys.stderr)
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)

    def __getattr__(self, attr):
        "Delegate attribute access to the interpreter object"
        return getattr(self.tk, attr)