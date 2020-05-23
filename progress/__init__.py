# Copyright (c) 2012 Giorgos Verigakis <verigak@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import division, print_function

import atexit
from datetime import timedelta
from math import ceil
from sys import stderr

try:
    from time import monotonic
except ImportError:
    from time import time as monotonic

__version__ = '1.5.1'

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'


class Infinite(object):
    file = stderr
    sma_window = 10  # Simple Moving Average window
    check_tty = True
    hide_cursor = True

    def __init__(self, message='', **kwargs):
        self.index = 0
        self.start_ts = monotonic()
        for key, val in kwargs.items():
            setattr(self, key, val)
        self._total_used_ts = 0
        self._width = 0
        self.message = message
        self._shutdown = False
        if self.file and self.is_tty():
            if self.hide_cursor:
                print(HIDE_CURSOR, end='', file=self.file)
                atexit.register(self.finish)
            print(self.message, end='', file=self.file)
            self.file.flush()

    def __getitem__(self, key):
        if key.startswith('_'):
            return None
        return getattr(self, key, None)

    @property
    def elapsed(self):
        return int(monotonic() - self.start_ts) + self._total_used_ts

    @property
    def elapsed_td(self):
        return timedelta(seconds=self.elapsed)

    @property
    def avg(self):
        if self.index > 0:
            return self.elapsed / self.index
        return 0

    def update(self):
        pass

    def start(self):
        pass

    def clearln(self):
        if self.file and self.is_tty():
            print('\r\x1b[K', end='', file=self.file)

    def write(self, s):
        if self.file and self.is_tty():
            line = self.message + s.ljust(self._width)
            print('\r' + line, end='', file=self.file)
            self._width = max(self._width, len(s))
            self.file.flush()

    def writeln(self, line):
        if self.file and self.is_tty():
            self.clearln()
            print(line, end='', file=self.file)
            self.file.flush()

    def finish(self):
        if self.file and self.is_tty():
            self._shutdown = True
            self._total_used_ts = self.elapsed
            print(file=self.file)
            if self.hide_cursor:
                print(SHOW_CURSOR, end='', file=self.file)
                atexit.unregister(self.finish)

    def is_tty(self):
        try:
            return self.file.isatty() if self.check_tty else True
        except AttributeError:
            raise AttributeError(
                '\'{}\' object has no attribute \'isatty\'. Try setting parameter check_tty=False.'.format(self))

    def next(self, n=1):
        if self._shutdown:
            self.start_ts = monotonic()
            self._shutdown = False
        self.index = self.index + n
        self.update()

    def iter(self, it):
        with self:
            for x in it:
                yield x
                self.next()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()


class Progress(Infinite):
    def __init__(self, *args, **kwargs):
        super(Progress, self).__init__(*args, **kwargs)
        self.max = kwargs.get('max', 100)

    @property
    def eta(self):
        return int(ceil(self.avg * self.remaining))

    @property
    def eta_td(self):
        return timedelta(seconds=self.eta)

    @property
    def percent(self):
        return self.progress * 100

    @property
    def progress(self):
        if self.max <= 0:
            return 1
        return min(1, self.index / self.max)

    @property
    def remaining(self):
        return max(self.max - self.index, 0)

    def start(self):
        self.update()

    def goto(self, index):
        incr = index - self.index
        self.next(incr)

    def iter(self, it):
        try:
            self.max = len(it)
        except TypeError:
            pass

        with self:
            for x in it:
                yield x
                self.next()
