"""Module Description
A
B
C
"""

import importlib
import inspect
import pydoc

from sphinx.pycode import ModuleAnalyzer


__author__ = 'Alexander Weigl'


class DocObject(object):
    """DocObject is a simple documentation object.

    """

    __slots__ = ["name", "documentation", "type", "sub", "argspec"]

    def __init__(self, name=None, doc=None, type=None):
        self.name = name
        self.documentation = doc
        self.type = type
        self.sub = list()

    def append(self, obj):
        if obj is None: return
        assert isinstance(obj, DocObject)
        self.sub.append(obj)

    def get(self, type=None, name=None):
        def create_filter(attrib, value):
            if value is None:
                return lambda x: True
            else:
                return lambda x: getattr(x, attrib) == value

        ftype = create_filter("type", type)
        fname = create_filter("name", name)
        pred = lambda x: ftype(x) and fname(x)
        return list(filter(pred, self.sub))

    def __str__(self):
        return "DocObject: %s, %s" % ( self.name, self.type)


TYPE_FUNCTION = "F"
TYPE_CLASS = "C"
TYPE_VAR = "V"
TYPE_CLASS_VAR = "CV"
TYPE_MODULE = "M"
TYPE_PACKAGE = "P"
TYPE_SPECIAL_VAR = "SV"

SPECIAL_VARIABLES = ("__author__", "__version__", "__date__", "__license__")


def doc_function(func, name):
    doc = pydoc.getdoc(func) or "\n\n"
    a = DocObject(name, doc, TYPE_FUNCTION)
    # a.argspec = inspect.getfullargspec(func)#args.args, args.varargs, args.keywords, args.defaults),
    a.argspec = inspect.formatargspec(*inspect.getfullargspec(func))
    return a


class Module(DocObject):
    def __init__(self, filename, modulename):
        super(Module, self).__init__(modulename, "", TYPE_MODULE)

        self.filename = filename
        """

        """

        self.modulename = modulename
        """

        """

        n = modulename.split(".")
        module = importlib.import_module(modulename)#n[-1], '.'.join(n[:-1]))

        print(module)

        self.documentation = inspect.getdoc(module) or ""

        exported_names = getattr(module, '__all__', None)

        def create_filter(pred):
            def fn(obj):
                try:
                    name = obj.func_name
                except:
                    try:
                        name = obj.__name__
                    except:
                        return True

                a = exported_names and name in exported_names
                try:
                    b = obj.__module__ == module
                except:
                    b = False
                return a and b and pred(obj)

            return fn

        for name, func in inspect.getmembers(module, inspect.isfunction):
            a = doc_function(func, name)
            self.append(a)

        for name, clzz in inspect.getmembers(module, inspect.isclass):
            # attrs = inspect.classify_class_attrs(clzz)
            print("CLAZZ: %s" % name)
            doc = pydoc.getdoc(clzz) or "\n\n"
            a = DocObject(name, doc, TYPE_CLASS)

            for name, func in inspect.getmembers(clzz, inspect.isfunction):
                a.append(doc_function(func, name))

            self.append(a)

        print(self.sub)
        # instances = map(prepdata, inspect.getmembers(module, pydoc.isdata))

        for sv in SPECIAL_VARIABLES:
            if hasattr(module, sv):
                self.append(DocObject(sv, str(getattr(module, sv)), TYPE_SPECIAL_VAR))

        ma = ModuleAnalyzer.for_file(filename, modulename)
        print(ma.attr_docs)
        for (scope, name), doc in ma.find_attr_docs().items():
            d = "\n".join(doc)
            if scope == '':
                self.append(DocObject(name, d, TYPE_VAR))
            else:
                clazz = self.get(TYPE_CLASS, scope)
                if clazz:
                    clazz.append(DocObject(name, d, TYPE_VAR))

    def __str__(self):
        return "Module '%s'" % self.modulename


class Package(Module):
    def __init__(self, filename, modulename):
        super(Package, self).__init__(filename, modulename)
        self.type = TYPE_PACKAGE

    def prepare(self, parent=None):
        super(Package, self).prepare(parent)
        self.filename = "index.rst"

        # for s in self.sub:
        # s.prepare(self)

    def __str__(self):
        return "Package: '%s' (%s)" % (self.modulename, ', '.join(map(str, self.sub)))
