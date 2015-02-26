*If you are reading this in plain text, head over to
https://github.com/Kingdread/DC
for a rendered version*

DC
==

![Screenshot](/Screenshot.png?raw=true)

Quoi?
-----

DC is a rewrite of the [microprocessor simulation][original] (german site) by
[Horst Gierhardt][gierhardt], written in Python and open source. It (should)
support everything the original DC.EXE supports.

DC is a little processor simulation with a small assembler instruction set,
designed as a teaching/learning tool to show the internal processes of a CPU.
You can use DC to show how simple loops are implemented with conditional jumps,
but also to demonstrate more complex procedures like subprograms with
parameters and return values or recursion.

Puorquoi?
--------

*Why not?*

Usage
-----

The documentation is not yet finished, you can find a german reference manual
on the [original program's website][original]. You can also find some example
programs on the site.

In the future I will write/translate a manual tailored to this DC
implementation.

Dependencies
------------

* Python 3
* PyQt 5

Installation
------------

No `setup.py` yet, until then just run `python3 start.py` in the git
repository.

License
-------

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

The font (`resource-files/DejaVuSansMono.ttf`) is part of the DejaVu font
family, whose license can be seen [here][deja-license]

Modifying
---------

Feel free to wreak havoc in the source and change whatever you want.

If you would like to see your changes pulled into the repository, you should
adhere to some basic style guidelines as [PEP 8][pep8]. The `Makefile` contains
a `lint` target to run `pylint` and `flake8`. You should try to not introduce
any lint failures.

If you modify anything in `resource-files/`, such as the background image or
the UI layout, you need to regenerate the relevant Python files. The `Makefile`
has targets `window`, `resources` and `all` as a shorthand for both. Thus, if
you modify resources, always run

    make all

---

Have fun!

[original]: http://www.oberstufeninformatik.de/dc/ (Mikroprozessor-Simulation)
[gierhardt]: http://www.gierhardt.de/
[deja-license]: http://dejavu-fonts.org/wiki/License
[pep8]: https://www.python.org/dev/peps/pep-0008/
