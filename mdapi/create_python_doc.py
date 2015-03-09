# -*- encoding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals
import sys

from mdapi.models import *

__author__ = "Alexander Weigl"

from path import path
from codecs import open
from jinja2 import Environment, FileSystemLoader

remove_none = lambda seq: filter(lambda x: x is not None, seq)

fldr = path(__file__).parent
env = Environment(loader=FileSystemLoader(fldr))


def indent(string, count=2):
    if string and string.strip():
        i = " " * count
        return i + string.strip().replace("\n", i + "\n")
    return ""


env.filters['indent'] = indent


def quote(string):
    if string and string.strip():
        return "> " + string.strip().replace("\n", "\n> ")
    return ""


env.filters['quote'] = quote


def scan(start):
    """

    :param start: root folder for scanning
    :type start: path
    :return:
    """

    def package(folder, prefix):
        assert isinstance(folder, path)

        filename = folder / "__init__.py"
        if filename.exists():

            name = folder.namebase
            prefix = prefix + [name]
            fullname = '.'.join(prefix)

            print("Found package: %s, %s" % (fullname, filename))
            try:
                p = Package(filename, fullname)

                for fil in folder.files("*.py"):
                    p.append(module(fil, prefix))

                for fold in folder.dirs():
                    p.append(package(fold, prefix))

                return p
            except BaseException as e:
                print(e)
                return None
        else:
            return None

    def module(file, prefix):
        assert isinstance(file, path)
        name = file.namebase

        if name[0] == '_':
            return None

        fullname = '.'.join(prefix + [name])

        print("Found module: %s, %s" % (fullname, file))

        try:
            m = Module(file, fullname)
            return m
        except BaseException as e:
            print(e)
            return None

    return package(start, [])


def create(root, output_dir, method="rst"):
    filename = output_dir / ("%s.%s" % (root.modulename, method))
    content = env.get_template("%s.jinja2" % method).render(module=root,
                                                            TYPE_PACKAGE=TYPE_PACKAGE,
                                                            TYPE_MODULE=TYPE_MODULE,
                                                            TYPE_VAR=TYPE_VAR,
                                                            TYPE_CLASS=TYPE_CLASS,
                                                            TYPE_FUNCTION=TYPE_FUNCTION,
                                                            TYPE_SPECIAL_VAR=TYPE_SPECIAL_VAR)
    print("Write %s" % filename)
    with open(filename, 'w', 'utf-8', 'ignore') as fn:
        fn.write(content)

    for pack in root.get(TYPE_PACKAGE):
        create(pack, output_dir, method)

    for mod in root.get(TYPE_MODULE):
        print(mod)
        create(mod, output_dir, method)


def main():
    sys.path.insert(0, "../msml/src/")
    d = scan(path("../msml/src/msml"))
    create(d, path("docs/"), 'rst')


main()