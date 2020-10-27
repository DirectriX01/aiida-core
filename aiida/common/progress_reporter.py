# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
# pylint: disable=global-statement,unused-argument
"""Provide a singleton progress reporter implementation.

The interface is inspired by `tqdm <https://github.com/tqdm/tqdm>`,
and indeed a valid implementation is::

    from tqdm import tqdm
    set_progress_reporter(tqdm, bar_format='{l_bar}{bar}{r_bar}')

"""
from functools import partial
from types import TracebackType
from typing import Any, Optional, Type

__all__ = (
    'get_progress_reporter', 'set_progress_reporter', 'set_progress_bar_tqdm', 'ProgressReporterAbstract',
    'TQDM_BAR_FORMAT'
)

TQDM_BAR_FORMAT = '{desc:40.40}{percentage:6.1f}%|{bar}| {n_fmt}/{total_fmt}'


class ProgressReporterAbstract:
    """An abstract class for incrementing a progress reporter.

    This class provides the base interface for any `ProgressReporter` class.

    Example Usage::

        with ProgressReporter(total=10, desc="A process:") as progress:
            for i in range(10):
                progress.set_description_str(f"A process: {i}")
                progress.update()

    """

    def __init__(self, *, total: int, desc: Optional[str] = None, **kwargs: Any):
        """Initialise the progress reporting contextmanager.

        :param total: The number of expected iterations.
        :param desc: A description of the process

        """
        self.total = total
        self.desc = desc
        self.increment = 0

    def __enter__(self) -> 'ProgressReporterAbstract':
        """Enter the contextmanager."""
        return self

    def __exit__(
        self, exctype: Optional[Type[BaseException]], excinst: Optional[BaseException], exctb: Optional[TracebackType]
    ):
        """Exit the contextmanager."""
        return False

    def set_description_str(self, text: Optional[str] = None, refresh: bool = True):
        """Set the text shown by the progress reporter.

        :param text: The text to show
        :param refresh: Force refresh of the progress reporter

        """
        self.desc = text

    def update(self, n: int = 1):  # pylint: disable=invalid-name
        """Update the progress counter.

        :param n: Increment to add to the internal counter of iterations

        """
        self.increment += n


class ProgressReporterNull(ProgressReporterAbstract):
    """A null implementation of the progress reporter.

    This implementation does not output anything.
    """


PROGRESS_REPORTER: Type[ProgressReporterAbstract] = ProgressReporterNull  # pylint: disable=invalid-name


def get_progress_reporter() -> Type[ProgressReporterAbstract]:
    """Return the progress reporter

    Example Usage::

        with get_progress_reporter()(total=10, desc="A process:") as progress:
            for i in range(10):
                progress.set_description_str(f"A process: {i}")
                progress.update()

    """
    global PROGRESS_REPORTER
    return PROGRESS_REPORTER  # type: ignore


def set_progress_reporter(reporter: Optional[Type[ProgressReporterAbstract]] = None, **kwargs: Any):
    """Set the progress reporter implementation

    :param reporter: A progress reporter for a process.  If None, reset to ``ProgressReporterNull``.

    :param kwargs: If present, set a partial function with these kwargs

    The reporter should be a context manager that implements the
    :func:`~aiida.common.progress_reporter.ProgressReporterAbstract` interface.

    Example Usage::

        set_progress_reporter(ProgressReporterNull)
        with get_progress_reporter()(total=10, desc="A process:") as progress:
            for i in range(10):
                progress.set_description_str(f"A process: {i}")
                progress.update()

    """
    global PROGRESS_REPORTER
    if reporter is None:
        PROGRESS_REPORTER = ProgressReporterNull  # type: ignore
    elif kwargs:
        PROGRESS_REPORTER = partial(reporter, **kwargs)  # type: ignore
    else:
        PROGRESS_REPORTER = reporter  # type: ignore


def set_progress_bar_tqdm(bar_format: Optional[str] = TQDM_BAR_FORMAT, leave: Optional[bool] = False, **kwargs: Any):
    """Set a `tqdm <https://github.com/tqdm/tqdm>`__ implementation of the progress reporter interface.

    See :func:`~aiida.common.progress_reporter.set_progress_reporter` for details.

    :param bar_format: Specify a custom bar string format.
    :param leave: If True, keeps all traces of the progressbar upon termination of iteration.
            If `None`, will leave only if `position` is `0`.
    :param kwargs: pass to the tqdm init

    """
    from tqdm import tqdm
    set_progress_reporter(tqdm, bar_format=bar_format, leave=leave, **kwargs)