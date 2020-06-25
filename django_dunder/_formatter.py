try:
    __builtins__ = builtins
except NameError:
    pass


class FormattableObjectWrapper(object):

    __slots__ = '_obj'

    def __new__(cls, obj):
        assert not isinstance(obj, FormattableObjectWrapper)

        self = super(FormattableObjectWrapper, cls).__new__(cls)
        self._obj = obj
        return self

    def ellipsis(self, width=100):
        tail = '...'
        obj = self._obj
        if isinstance(width, str):
            width = int(width)
        try:
            if len(obj) > width:
                rv = obj[:width - len(tail)] + tail
                return rv
        except Exception:
            return self    

    def __getattr__(self, name):
        obj = self._obj
        attr = None
        remainder = None
        rv = None

        func_name = None
        args_start_pos = name.find('(')
        if args_start_pos != -1:
            args_end_pos = name.find(')', args_start_pos)
            args = name[args_start_pos+1:args_end_pos]
            args = [args] if args else []
            func_name = name[:args_start_pos]
            remainder = name[args_end_pos:]

        if not func_name:
            next_func_start_pos = name.find('__')
            if next_func_start_pos != -1:
                remainder = name[next_func_start_pos+2:]
                current = name[:next_func_start_pos]
            else:
                current = name
            func_name, _, args = current.partition('_')
            args = args.split('_') if args else []

        try:
            attr = getattr(obj, func_name)
        except AttributeError:
            pass

        # e.g. round
        if not attr:
            attr = __builtins__.get(func_name, None)
            if attr:
                args.insert(0, obj)

        # e.g. ellipsis
        if not attr:
            attr = self.__class__.__dict__.get(func_name, None)
            if attr:
                args.insert(0, self)

        if attr and (args or callable(attr)):
            try:
                rv = attr(*args)
                if rv is self:
                    rv = None
            except Exception:
                pass

        if remainder:
            if rv:
                rv = getattr(FormattableObjectWrapper(rv), remainder)
            else:
                # Wasnt doable; try next
                rv = getattr(self, remainder)

        if rv and rv != obj:
            return rv

        return obj

    def __str__(self):
        return str(self._obj)

    def __repr__(self):
        return repr(self._obj)

    def __getitem__(self, key):
        if isinstance(key, str) and ':' in key:
            parts = key.split(':')
            parts = [int(part) for part in parts]
            key = slice(*parts)
        try:
            rv = self._obj.__getitem__(key)
            return rv
        except Exception:
            return str(self._obj)
