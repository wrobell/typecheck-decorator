import inspect
import typing as tg

import typecheck.framework as fw
import typecheck.tc_predicates as tcp

_dummy = None  # __init__.py must use from...import to avoid 'typecheck' name clash

# TypeChecker must not apply to the stuff from module typing
# which all(?) comes under the following types of types.
# We therefore check for these types separately and register their
# checkers with prepend=True so they are handled first.
typing_typetypes = [tg.GenericMeta,
                    tg.CallableMeta,
                    tg._ProtocolMeta]

def _is_GenericMeta_class(something):
    return (inspect.isclass(something) and
            type(something) == tg.GenericMeta)

class GenericMetaChecker(fw.Checker):
    def __init__(self, tg_class):
        self._cls = tg_class

    def check(self, value, namespace):
        if not isinstance(value, self._cls):
            return False
        metaclass = type(self._cls)
        assert metaclass == tg.GenericMeta
        params = self._cls.__parameters__
        # now check checkable relevant properties of all
        # relevant Generic subclasses from the typing module:
        if isinstance(value, tg.Sequence):
            return self._check_sequence(value, params, namespace)
        elif (isinstance(value, (tg.Mapping, tg.MappingView))):
            return self._check_mapping(value, params, namespace)  # TODO: OK for all MappingViews?
        elif isinstance(value, tg.AbstractSet):
            return self._check_by_iterator(value, params, namespace)
        # tg.Iterable: nothing is checkable, see tg.Iterator
        # tg.Iterator: nothing is checkable: must not read, might be a generator
        # tg.Container: nothing is checkable: would need to guess elements
        else:
            return True

    def _check_by_iterator(self, value, contenttypes, namespace):
        assert False  # TODO: implement _check_by_iterator

    def _check_mapping(self, value, contenttypes, namespace):
        assert False  # TODO: implement _check_mapping

    def _check_sequence(self, value, contenttypes, namespace):
        assert len(contenttypes) == 1
        return tcp.sequence_of(contenttypes[0]).check(value, namespace)

fw.Checker.register(_is_GenericMeta_class, GenericMetaChecker, prepend=True)


def _is_typevar(something):
    return type(something) == tg.TypeVar

class TypeVarChecker(fw.Checker):
    def __init__(self, typevar):
        self.typevar = typevar

    def check(self, value, namespace):
        """
        See whether the TypeVar is bound for the first time
        or is met with _exactly_ the same type as previously.
        Everything else is a type error.
        """
        print("TypeVarChecker.check")
        return namespace.is_compatible(self.typevar, type(value))
        # TODO: more informative error message, showing the TypeVar binding

fw.Checker.register(_is_typevar, TypeVarChecker, prepend=True)
