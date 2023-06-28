import contextlib
import os
import shutil
import subprocess
import webbrowser
from itertools import chain
from pathlib import Path
from platform import uname

from invoke import task

"""'Makefile' equivalent for invoke tool (invoke or inv).
# Installation
`pip install invoke`
# Usage
> inv test
> inv build
etc...
# Autocompletion
For auto completion, just run:
`source <(inv --print-completion-script bash)`
or
`source <(inv --print-completion-script zsh)`
(or add it to ~/.zshrc or ~/.bashrc)
"""


# UTILS -----------------------------------------------------------------------

def get_platform():
    """Check the platform (Windos, Linux, or WSL)."""
    u = uname()
    if u.system == 'Windows':
        return 'windows'
    elif u.system == 'Linux' and 'microsoft' in u.release:
        return 'wsl'
    else:
        return 'linux'


def get_index_path():
    """Get full path for ./htmlcov/index.html file."""
    platform = get_platform()
    if platform != "wsl":
        return Path('.').resolve() / 'htmlcov' / 'index.html'
    # TODO: this part with .strip().replace() is ugly...
    process = subprocess.run(['wslpath', '-w', '.'], capture_output=True, text=True)
    pathstr = process.stdout.strip().replace('\\', '/')
    return Path(pathstr) / 'htmlcov/index.html'


# TASKS------------------------------------------------------------------------

@task
def lint(c):
    """flake8 - static check for python files"""
    c.run("flake8 .")


@task
def cleantest(c):
    """Clean artifacts like *.pyc, __pycache__, .pytest_cache, etc..."""
    # Find .pyc or .pyo files and delete them
    exclude = ('venv', '.venv')
    p = Path('.')
    genpyc = (i for i in p.glob('**/*.pyc') if not str(i.parent).startswith(exclude))
    genpyo = (i for i in p.glob('**/*.pyo') if not str(i.parent).startswith(exclude))
    artifacts = chain(genpyc, genpyo)
    for art in artifacts:
        os.remove(art)

    # Delete caches folders
    cache1 = p.glob('**/__pycache__')
    cache2 = p.glob('**/.pytest_cache')
    cache3 = p.glob('**/.mypy_cache')
    caches = chain(cache1, cache2, cache3)
    for cache in caches:
        shutil.rmtree(cache)

    # Delete coverage artifacts
    with contextlib.suppress(FileNotFoundError):
        os.remove('.coverage')
        shutil.rmtree('htmlcov')


@task
def cleanbuild(c):
    """Clean dist and build"""
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree('build')
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree('dist')


@task
def cleancomics(c):
    """Clean .cbz and .cbr files"""
    p = Path('.')
    comics = p.glob('**/*.cb[rz]')
    for comic in comics:
        comic.unlink()


@task
def cleandoc(c):
    """Clean documentation files."""
    p = Path('.').resolve() / "docs" / "build"
    print(p)
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(p)


@task(cleantest, cleanbuild, cleancomics)
def clean(c):
    """Equivalent to both cleanbuild and cleantest..."""
    pass


@task
def test(c):
    """Run tests with pytest."""
    c.run("pytest tests/")


@task
def coverage(c):
    """Run unit-tests using pytest, with coverage reporting."""
    # use the browser defined in varenv $BROWSER
    # in WSL, if not set, example :  export BROWSER='/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'  # noqa: E501
    path = get_index_path()
    # c.run('coverage run --source=tests -m pytest')
    # c.run('coverage report -m')
    # c.run('coverage html')
    c.run('pytest --cov . --cov-report html')
    webbrowser.open(path.as_uri())


@task(cleandoc)
def doc(c):
    c.run("pushd docs && make html && popd")
    path = Path('.').resolve() / "docs" / "build" / "html" / "index.html"
    webbrowser.open(path.as_uri())


@task(cleanbuild)
def pyinstaller(c):
    """Build comicsdl with pyinstaller, clean the dist, and make a zip archive."""
    c.run('pyinstaller download-comics.spec')

    # clean tcl
    p = Path('.').resolve() / "dist" / "download-comics"
    tzs = p.glob("tcl/tzdata/*/")
    # print(*tzs, sep='\n')
    for tz in tzs:
        if tz.is_dir() and 'Europe' not in tz.name:
            shutil.rmtree(tz)
        if tz.is_file() and tz.name not in ["CET", "GMT", "GMT-0", "GMT+0", "GMT0",
                                            "Greenwich", "UTC"]:
            tz.unlink()

    euro_tzs = p.glob('**/tcl/tzdata/Europe/*')
    for tz in euro_tzs:
        if tz.name != "Paris":
            tz.unlink()

    encodings = p.glob("tcl/encoding/*")
    # print(*encodings, sep='\n')
    for enc in encodings:
        # print(enc.name)
        if "ascii" not in enc.name and "iso88" not in enc.name and "utf-8" not in enc.name:
            enc.unlink()

    msgs = p.glob("tcl/msgs/*")
    # print(*msgs, sep='\n')
    for msg in msgs:
        if msg.name != "fr.msg":
            msg.unlink()

    # clean tk
    tkmsgs = p.glob("tk/msgs/*")
    # print(*tkmsgs, sep='\n')
    for tkmsg in tkmsgs:
        if tkmsg.name not in ["en_gb.msg", "en.msg", "fr.msg"]:
            tkmsg.unlink()

    # make the zip file
    dist = Path(__file__).parent / "dist"
    shutil.make_archive("download-comics", "zip", dist)


@task
def zip(c):
    """make the zip"""
    dist = Path(__file__).parent / "dist"
    shutil.make_archive("download-comics", "zip", dist)


@task
def run(c):
    """Run the .exe"""
    c.run(".\dist\download-comics\download-comics.exe")


@task
def cleantcltk(c):
    """Clean the dist"""
    p = Path('.').resolve() / "dist" / "download-comics"
    tzs = p.glob("tcl/tzdata/*/")
    # print(*tzs, sep='\n')
    for tz in tzs:
        if tz.is_dir() and 'Europe' not in tz.name:
            shutil.rmtree(tz)
        if tz.is_file() and tz.name not in ["CET", "GMT", "GMT-0", "GMT+0", "GMT0",
                                            "Greenwich", "UTC"]:
            tz.unlink()

    euro_tzs = p.glob('**/tcl/tzdata/Europe/*')
    for tz in euro_tzs:
        if tz.name != "Paris":
            tz.unlink()

    encodings = p.glob("tcl/encoding/*")
    # print(*encodings, sep='\n')
    for enc in encodings:
        # print(enc.name)
        if "ascii" not in enc.name and "iso88" not in enc.name and "utf-8" not in enc.name:
            enc.unlink()

    msgs = p.glob("tcl/msgs/*")
    # print(*msgs, sep='\n')
    for msg in msgs:
        if msg.name != "fr.msg":
            msg.unlink()

    # clean tk
    tkmsgs = p.glob("tk/msgs/*")
    # print(*tkmsgs, sep='\n')
    for tkmsg in tkmsgs:
        if tkmsg.name not in ["en_gb.msg", "en.msg", "fr.msg"]:
            tkmsg.unlink()
