### Python Terminal Tools (ptt)

#### DESCRIPTION

Yet to come.

#### LICENSE

'Python Terminal Tools' is licensed under version 3 of the GNU General Public
License.

#### INSTALLATION

This branch of the 'Python Terminal Tools' contains another branch of the same
repository as a submodule. This submodule must be initialized first.

**in short:** After having cloned this repository do:

    git submodule init
    git submodule update

And everytime you want to update this repository do:

    git submodule update

additionally to the normal pull/fetch requests.

See the README in the ptt directory (the submodules directory), for why this is
done.

#### EXAMPLES

To test this package on the fly, without installing it, You have to make sure,
that python knows, where to find the ptt package when using the examples. This
can be done by specifying the PYTHONPATH environment variable (see the manpage
of the python program).

**in short:** *assuming, that You are in the directory where the ptt package
directory is located* (this should also be the directory, where this readme is
located), You can do this, for example:

    PYTHONPATH=. python3 examples/table.py

#### CONTACT

Benjamin Schnitzler <benjaminschnitzler@googlemail.com>
