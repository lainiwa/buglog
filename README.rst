
===============================
BUGlog - log what's bugging you
===============================

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

    pip install --user 'https://github.com/lainiwa/buglog'

    pipx install 'https://github.com/lainiwa/buglog'

Then the util can be run as::

    bug

Upon the first invocation the tool will automatically

* download fzf binary
* and create a template configuration at ``~/.config/buglog/config.py``

Usage
#####

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
.. _`Org mode`: https://orgmode.org/manual/Tracking-your-habits.html

License
#######

Buglog is released under the MIT License.
See the bundled LICENSE file for details.
