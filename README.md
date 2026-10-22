# Maupertuis

A small Python library for terminal UIs: it splits the screen into named panes
and tracks which panes need redrawing. Named after the fox Renart's stronghold
in the *Roman de Renart*.

Maupertuis has no dependencies and never touches the terminal. The app does the
rest: the main loop, the framerate, input, detecting resizes, and printing the
string `draw()` returns.

## Installation

Maupertuis requires Python 3.14+ and isn't on PyPI. Install it from GitHub:

```bash
pip install git+https://github.com/ytrebouta/maupertuis
```

or declare it as a dependency in your `pyproject.toml`:

```toml
dependencies = [
    "maupertuis @ git+https://github.com/ytrebouta/maupertuis",
]
```

## Usage

A layout is plain data. A container is a dict with one key, `rows` (stacked top
to bottom) or `cols` (side by side), listing `(node, size)` pairs, where a node
is a pane id or a nested container. A positive size is fixed, `-1` shares the
remaining space, and `0` hides the pane.

Each pane id has a draw function. Maupertuis calls it with the keyword arguments
`x0`, `y0`, `w` and `h` (the pane's position and size), so its parameters must
have those names. It returns a string, here built with ANSI escape codes:

```python
import shutil

from maupertuis import Maupertuis


layout = {'rows': [
	('main',	-1),
	({'cols': [('status', -1), ('clock', 8)]}, 1),
]}


def move(x, y):

	return f'\x1b[{y + 1};{x + 1}H'		# move the cursor (ANSI rows and columns start at 1)


def draw_main(x0, y0, w, h):

	return move(x0, y0) + 'Hello'.ljust(w)


def draw_status(x0, y0, w, h):

	return move(x0, y0) + '\x1b[7m' + 'Ready'.ljust(w) + '\x1b[0m'		# reverse video, then reset


def draw_clock(x0, y0, w, h):

	return move(x0, y0) + '12:00'.rjust(w)


width, height	= shutil.get_terminal_size()
draw_fns		= {'main': draw_main, 'status': draw_status, 'clock': draw_clock}
mp				= Maupertuis(layout, draw_fns, width, height)

print(mp.draw(), end='', flush=True)	# first frame: clear the screen, draw every pane
```

Then, in the app's loop:

- `mp.mark('clock')` when a pane's content changes. The next `draw()` only
  returns the marked panes.
- `mp.build(width, height)` after a resize, detected by comparing
  `shutil.get_terminal_size()` with the previous size. It recomputes the panes,
  and the next `draw()` clears the screen and redraws everything. If the
  terminal is too small for the fixed sizes, `build()` raises `ValueError` and
  keeps the previous panes: skip `draw()` until a later `build()` succeeds.

`draw()` starts a full redraw with an ANSI clear-screen sequence. Pass
`clear_str=` to the constructor to use another one.

## Development

The tests are plain `assert`s in `tests/test_maupertuis.py`. Run them from the
repo root with pytest (`pyproject.toml` puts `src/` on the path):

```bash
pytest
```

or without pytest:

```bash
PYTHONPATH=src python tests/test_maupertuis.py
```

## License

MIT, see [LICENSE](LICENSE).
