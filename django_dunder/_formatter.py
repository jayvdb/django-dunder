try:
    __builtins__ = builtins
except NameError:
    pass

_DEBUG = False

# Very crude; not really sure about this approach,
# however custom Formatter classes are painful.
# Switch to ast if a better approach isnt found.
def _get_one_invoke(in_str):
    seps = ['__', '(']
    longest_pos = len(in_str)
    for sep in seps:
        pos = in_str.find(sep)
        if pos != -1:
            longest_pos = min(longest_pos, pos)

    invoke_type = in_str[longest_pos] if longest_pos < len(in_str) else '*'

    if _DEBUG:
        print('first parse', in_str, longest_pos, invoke_type)

    if invoke_type == '(':
        args_start_pos = longest_pos
        func_name = in_str[:args_start_pos]
        args_start_pos += 1
        args_end_pos = in_str.find(')', args_start_pos)
        args = in_str[args_start_pos:args_end_pos]
        args = args.split(',') if args else []
        args = [arg.strip() for arg in args]
        remainder = in_str[args_end_pos+1:]
        if remainder:
            # Check there is a sensible separator
            # Note '.' doesnt always reach here; str.format has already done
            # that separation if it found plain attribute names.
            if remainder[0] == '_':
                remainder = remainder.lstrip('_')
            elif remainder[0] in ('.', ','):
                remainder = remainder[1:].lstrip()
            else:
                remainder = None
    else:
        args_end_pos = longest_pos
        if invoke_type == '_':
            current = in_str[:args_end_pos]
            remainder = in_str[args_end_pos+2:]
        else:  # must be '*'
            current = in_str
            remainder = None

        func_name, _, args = current.partition('_')
        args = args.split('_') if args else []

    for i, arg in enumerate(list(args)):
        try:
           args[i] = int(arg)
        except ValueError:
           pass

    if not remainder:
        remainder = None

    if _DEBUG:
        print('parsed', func_name, args, remainder)
    return func_name, args, remainder


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

        func_name, args, remainder = _get_one_invoke(name)

        rv = None

        try:
            attr = getattr(obj, func_name)
        except AttributeError:
            attr = None

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

        if _DEBUG:
            print('invoked {} {!r}(*{}) = {}'.format(func_name, attr, args, rv))

        if rv and rv != obj:
            # Wrapping the return type allows Formatter to handle foo().bar()
            if not isinstance(rv, FormattableObjectWrapper):
                rv = self.__class__(rv)
            return rv

        return self

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
