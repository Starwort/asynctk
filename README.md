# AsyncTK

[![Licence: GPL v3](https://img.shields.io/badge/Licence-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## What is AsyncTK?

AsyncTK is an asynchronous wrapper for TK/TCL using TKInter and AsyncIO.
It can:

- Initialise and start the event loop
- Run all major TK/TCL commands and widgets, asynchronously!
- Be combined, using class inheritance, with other asynchronous processes and classes!

### Installation

AsyncTK can be installed using `pip install asynctk`, or for the more adventurous, `pip install git+https://github.com/Starwort/asynctk.git`

### Usage

AsyncTK's window is used as TK's is, it's created, and components are placed onto it. Finally, the app's `.mainloop()` method is called, and your program runs. Nothing new there, right? Wrong. By calling `asyncio.ensure_future()` on your coroutines, those coroutines will continue to run, and can interact with the TK window. This means no more `threading` solutions - processes can change the window!

### Future improvements

- Make coroutines the default for callbacks
- Ensure there is no widget lag