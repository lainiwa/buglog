
===============================
BUGlog - log what's bugging you
===============================

.. image:: https://codecov.io/gh/lainiwa/buglog/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/lainiwa/buglog

This CLI tool is meant to be used as

* pills intake log
* pain diary
* anxiety/CBT diary
* calorie counter
* *and whatever else*

**Note:** the project is pre-alpha quality.

Rationale
#########

Install
#######

Any of these would go::

    pip install --user 'git+https://github.com/lainiwa/buglog'

    pipx install 'git+https://github.com/lainiwa/buglog'  # newer versions

    pipx install --spec 'git+https://github.com/lainiwa/buglog.git' buglog

Then the util can be run as::

    bug

Upon the first invocation the tool will automatically

* download fzf binary
* and create a template configuration at ``~/.config/buglog/config.py``

Usage
#####

.. image:: https://asciinema.org/a/348860.svg
   :target: https://asciinema.org/a/348860

At it's current design the ``bug`` command does not accept any arguments.
Just execute it an you will see the list of the "bugs" you can log
into your personal log/database.

Choose a few with ``Tab`` and press ``Enter``. You will
see a reStructuredText document where you are expected to type in some
parameters of the bug. Fill in the gaps and save and exit the editor.

Then you will be prompted with a dialog, which will lead you to a time picker.
The time you enter can be either in a machine-like format (ex.: ``2020-07-21_10:51:10``)
or in a human readable (say ``today at 4:20``).

All in all, your bugs will be finally saved in the ``~/.local/share/buglog/``
directory in a format ``YYYY-MM-DD_hh:mm:ss_BugClassName.json``.

Currently there is no way to use the data with the means of buglog itself.
However, you can use bash scripting and jq_ to mess with the saved data.

.. _jq: https://github.com/stedolan/jq

Configuration
#############

The configuration file is read from
``${XDG_CONFIG_HOME:-${HOME}/.config}/buglog/config.py``.
In case no such file exists,
buglog will automatically create it from the `template configuration`_.

The configuration file -- exclusive of imports -- consists of flat
Pydantic_ classes, inherited from ``Bug`` model.

Take a look at the example Bug below:

.. code-block:: python

    class Squats(Bug):
        """Excercise: squats"""
        reps: int = Field(1, title="Repetitions", gt=0)
        times: int = Field(..., gt=0)

Let's now line by line. First of all, to create a new Bug we need to derive it
from the ``Bug`` class, so that buglog would know it is a Bug
and not something else.

.. code-block:: python

    class Squats(Bug):

Not the docstring_ part here is completeley optional.
You can choose not to write one, if it feels like the class name is
informative enough.

.. code-block:: python

        """Excercise: squats"""

The ``title`` is also not strictly required: it is used as a more verbose
description compared to a name of the field.

The type ``int`` of the field will be checked against and enforced.

.. code-block:: python

        reps: int = Field(1, title="Repetitions", gt=0)

The first positional argument if the ``Field()`` is the default.
If you do not want the field to have a default -- you should
put `...`_ instead.

Use can specify additional checkers, for example ``gt=0``
means the filed should be *greater-than* zero.

.. _template configuration: buglog/data/config.py
.. _Pydantic: https://github.com/samuelcolvin/pydantic
.. _docstring: https://www.python.org/dev/peps/pep-0257/#one-line-docstrings
.. _...: https://docs.python.org/dev/library/constants.html#Ellipsis

Limitations
###########

Similar Projects
################

* Taskwarrior_: is centered around TODO-based workflow (AFAIK. It's rather complex)
* Dijo_: ???
* Habitctl_: the idea is quiet similar, although the bugs/habits are not parameterized
* Watson_: a time tracker
* `Org mode`_: using Emacs' Org mode to track habits

.. _Taskwarrior: https://github.com/GothenburgBitFactory/taskwarrior
.. _Dijo: https://github.com/NerdyPepper/dijo
.. _Habitctl: https://github.com/blinry/habitctl
.. _Watson: https://github.com/TailorDev/Watson
.. _Org mode: https://orgmode.org/manual/Tracking-your-habits.html

License
#######

Buglog is released under the MIT License.
See the bundled LICENSE_ file for details.

.. _LICENSE: LICENSE
