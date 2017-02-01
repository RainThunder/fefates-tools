#!/usr/bin/env python2
#
# The MIT License
#
# Copyright (c) 2017 RainThunder.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
"""Base types used in this project.

A short explanation of hierarchy in this module:
- A Table object includes multiple Row objects.
- A Row object has many type-restricted attributes (cells). Putting a wrong
type object to a cell is disallowed.
- Each attributes is a simple type object, or a collection of them (like
Array, RestrictedDict, Row, Flags).
- Every simple type object has its own type checking in their __init__
method. We need to create simple type classes because Python built-in types
doesn't have type and range checking).
- Array, RestrictedDict is a restricted version of default list and dict,
respectively. Similar to Row, it doesn't allow putting a wrong-type object.
"""

import sys
from collections import OrderedDict
from struct import unpack, pack, error as struct_error
if sys.version_info[0] > 2:
    xrange = range
    unicode = str
    long = int


##############################################################################
# Various data types
##############################################################################
class Integer(long):
    """Basic integer."""
    minvalue = None
    maxvalue = None
    size = None
    fstring = None

    def tohex(self):
        mask = (1 << 8 * self.__class__.size) - 1
        fstring = '0' + str(self.__class__.size * 2) + 'X'
        return unicode('0x' + format(self & mask, fstring))

    def tojsonobject(self):
        """Output JSON object."""
        return self

    def tostring(self):
        """Output string."""
        return unicode(self)


class UnsignedInteger(Integer):
    """Unsigned integer."""
    def __new__(cls, *args, **kwargs):
        v = super(UnsignedInteger, cls).__new__(cls, *args, **kwargs)
        try:
            pack(cls.fstring, v)
        except struct_error:
            raise ValueError('out of range')
        return v


class SignedInteger(Integer):
    """Signed ingeger."""
    def __new__(cls, *args, **kwargs):
        v = super(SignedInteger, cls).__new__(cls, *args, **kwargs)
        if len(args) == 2 or 'base' in kwargs:
            try:
                v = unpack(cls.fstring, pack(cls.fstring.upper(), v))[0]
            except struct_error:
                raise ValueError('out of range')
            v = cls.__new__(cls, v)
        else:
            try:
                pack(cls.fstring, v)
            except struct_error:
                raise ValueError('out of range')
        return v


class U8(UnsignedInteger):
    """unsigned 8-bit integer"""
    size = 1
    fstring = 'B'

    def __new__(cls, *args, **kwargs):
        return super(U8, cls).__new__(cls, *args, **kwargs)


class S8(SignedInteger):
    """signed 8-bit integer"""
    size = 1
    fstring = 'b'

    def __new__(cls, *args, **kwargs):
        return super(S8, cls).__new__(cls, *args, **kwargs)


class U16(UnsignedInteger):
    """unsigned 16-bit integer"""
    size = 2
    fstring = 'H'

    def __new__(cls, *args, **kwargs):
        return super(U16, cls).__new__(cls, *args, **kwargs)


class S16(SignedInteger):
    """signed 16-bit integer"""
    size = 2
    fstring = 'h'

    def __new__(cls, *args, **kwargs):
        return super(S16, cls).__new__(cls, *args, **kwargs)


class U32(UnsignedInteger):
    """unsigned 32-bit integer"""
    size = 4
    fstring = 'I'

    def __new__(cls, *args, **kwargs):
        return super(U32, cls).__new__(cls, *args, **kwargs)


class S32(SignedInteger):
    """signed 32-bit integer"""
    size = 4
    fstring = 'i'

    def __new__(cls, *args, **kwargs):
        return super(S32, cls).__new__(cls, *args, **kwargs)


class Label(unicode):
    """Label type."""
    size = 4
    fstring = 'I'

    def __new__(cls, *args, **kwargs):
        return super(Label, cls).__new__(cls, *args, **kwargs)

    def __str__(self):
        return self

    def tostring(self):
        """Output string."""
        # Use __str__ is quite misleading in this case.
        return self

    def tojsonobject(self):
        """Output JSON object."""
        return self


class Flags(object):
    """Generic flag list.

    In order to use this structure, you must inherit this class and create
    a list of flag names in `names` attribute.
    """
    names = []
    def __init__(self, data):
        """Initialize a flag list.

        `data`: raw flag data (bytes)
        """
        if not isinstance(data, bytes):
            raise TypeError('')
        if len(data) * 8 != len(self.__class__.names):
            raise ValueError('length mismatched')
        flags = []
        for i in xrange(len(data) * 8):
            flags.append((data[i // 8] >> (i % 8)) & 0x1 == 0x1)
        for i in xrange(len(self.__class__.names)):
            setattr(self, self.__class__.names[i], flags[i])

    def __setattr__(self, name, value):
        if name not in self.__class__.names:
            raise AttributeError('unknown flag')
        self.__dict__[name] = bool(value)

    def flatten(self):
        """Flatten this structure."""
        return [self.__dict__[name] for name in self.__class__.names]

    def tobytes(self):
        """Get bytes output from Flags object."""
        output = bytearray(b'\0' * (len(self.__class__.names) // 8))
        for i in xrange(len(self.__class__.names)):
            if self.__dict__[self.__class__.names[i]]:
                output[i // 8] |= (1 << (i % 8))
            else:
                output[i // 8] &= ~(1 << (i % 8))
        return bytes(output)

    def tojsonobject(self):
        """Output JSON object."""
        jsonobj = OrderedDict()
        for attr in self.__class__.names:
            jsonobj[attr] = self.__dict__[attr]
        return jsonobj

    def tostring(self):
        return u'\t'.join([unicode(self.__dict__[a])
                          for a in self.__class__.names])


##############################################################################
# Various collections
##############################################################################
class Array(list):
    """An array-like object.

    This is a collections which is similar to array: fixed length, fixed type
    and random access by index. Inheriting from this class is mandatory. Array
    type and length are defined in `type` and `length` class attribute.
    """
    type = None
    length = None

    def __init__(self, *args, **kwargs):
        """Initialize an array.

        Keyword arguments:
        `hex`: If True, the input is a list of hex strings.

        other params are the same as list.
        """
        cls = self.__class__
        if len(args) > 1:
            raise TypeError('expected at most 1 argument')
        elif len(args) == 1:
            if len(args[0]) != self.__class__.length:
                raise ValueError('number of items are mismatch')
            if 'hex' in kwargs and not isinstance(kwargs['hex'], bool):
                raise TypeError("argument 'hex' must be a bool")
            if 'hex' in kwargs and kwargs['hex']:
                data = [cls.type(item, 16) for item in args[0]]
                del kwargs['hex']
                list.__init__(self, data, **kwargs)
            else:
                data = [cls.type(item) for item in args[0]]
            list.__init__(self, data, **kwargs)
        else:
            list.__init__(self, [cls.type()] * cls.length, **kwargs)

    def __delitem__(self, index):
        raise NotImplementedError

    def __setitem__(self, index, item):
        list.__setitem__(self, index, self.__class__.type(item))

    def append(self, element):
        raise NotImplementedError

    def extends(self, *args):
        raise NotImplementedError

    def insert(self, index, item):
        raise NotImplementedError

    def pop(self, index):
        raise NotImplementedError

    def remove(self, index, item):
        raise NotImplementedError

    def flatten(self):
        """Flatten this structure."""
        return list(self)

    def tohex(self):
        """Output tab-delimited hex string."""
        return u'\t'.join([item.tohex() for item in self])

    def tojsonobject(self):
        return [item.tojsonobject() for item in self]

    def tostring(self):
        """Output tab-delimited string."""
        return u'\t'.join([item.tostring() for item in self])


class RestrictedDict(dict):
    """A dictionary with fixed keys and type-restricted values.

    All keys and value type must be provided when defining the child class.
    This structure also supports get and set the values via attribute
    syntax.
    """
    type = None # Type
    keys = None # List of keys

    def __init__(self, *args, **kwargs):
        """Initialize a new dict."""
        cls = self.__class__
        if len(args) > 1:
            raise TypeError('expected 1 arguments, got %d' % len(args))

        if len(args) == 1:
            if len(args[0]) != len(cls.keys):
                raise ValueError('number of items are mismatch')
            if 'hex' in kwargs and kwargs['hex']:
                data = [cls.type(item, 16) for item in args[0]]
                del kwargs['hex']
            else:
                data = [cls.type(item) for item in args[0]]
            dict.__init__(self, **kwargs)
            for i in xrange(len(cls.keys)):
                dict.__setitem__(self, cls.keys[i], data[i])
        if len(args) == 0:
            dict.__init__(self, **kwargs)
            for i in xrange(len(cls.keys)):
                dict.__setitem__(self, cls.keys[i], cls.type())

    def __delitem__(self, key):
        raise NotImplementedError

    def __getattr__(self, key):
        # Support get value via attribute syntax
        if key in self.__class__.keys:
            return self[key]
        else:
            super(RestrictedDict, self).__getattr__(key)

    def __setattr__(self, key, value):
        # Support set value via attribute syntax
        if key in self.__class__.keys:
            self[key] = value # call __setitem__
        else:
            super(RestrictedDict, self).__setattr__(key, value)

    def __setitem__(self, key, value):
        if key not in self.__class__.keys:
            raise KeyError(str(key))
        dict.__setitem__(self, key, self.__class__.type(value))

    def flatten(self):
        """Flatten this structure."""
        return [self[key] for key in self.__class__.keys]

    def tohex(self):
        """Output tab-delimited hex string."""
        return u'\t'.join([self[key].tohex() for key in self.__class__.keys])

    def tojsonobject(self):
        """Output JSON object."""
        jsonobj = OrderedDict()
        for key in self.keys:
            jsonobj[key] = self[key].tojsonobject()
        return jsonobj

    def tostring(self):
        """Output tab-delimited string."""
        return u'\t'.join([self[key].tostring() for key in self.__class__.keys])


##############################################################################
# Main data structures
##############################################################################
class Row(object):
    """A generic data structure.

    This data structure support setting attribute in various ways:
    - row.name = 'ABC'
    - row['name'] = 'ABC'
    - row[0] = 'ABC' (assume the first attribute is 'name')

    Inheriting from this class is mandatory.
    """
    structure = None
    attributes = [] # A list of all attributes
    size = 4
    fstring = 'I'

    def __init__(self, data):
        """Initialize a new row.

        A `structure` must be a OrderedDict which contains:
        - key: attribute (field) names
        - value: a Structure object

        `data` is a list or tuple that follows the structure.
        """
        if isinstance(data, unicode):
            self.fromstring(data)
        else:
            if len(data) != len(self.__class__.structure):
                raise ValueError('data length does not match with structure ' +
                                 'definition')
            i = 0
            for attr in self.__class__.structure:
                self.__class__.attributes.append(attr)
                t = self.__class__.structure[attr].type
                if issubclass(t, (Row, Flags, Array, RestrictedDict)):
                    self.__dict__[attr] = t(data[i])
                else:
                    self.__setattr__(attr, data[i])
                i += 1

    def __getitem__(self, key):
        if isinstance(key, int):
            key = self.__class__.attributes[key]
        self.__getattr__(self, key)

    def __iter__(self):
        return iter(self.__class__.structure)

    def __len__(self):
        return len(self.__class__.structure)

    def __setattr__(self, name, value):
        # Set new attributes. Collection-type attributes cannot be set.
        try:
            t = self.__class__.structure[name].type
        except KeyError:
            raise AttributeError("Row object has no attribute '" + name + "'")
        if issubclass(t, (Row, Flags, Array, RestrictedDict)):
            raise AttributeError('can\'t set attribute')
        # Leave type checking to data type classes, then assign the new value
        object.__setattr__(self, name, t(value))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self.__class__.attributes[key]
        self.__setattr__(key, value)

    def __str__(self):
        return str([str(self.__dict__[a]) for a in self.__class__.structure])

    def fromstring(self, line):
        """Load data from text. Text must be in unicode format."""
        cells = line.split(u'\t')
        j = 0
        temp_data = []
        for attr in self.__class__.structure:
            st = self.__class__.structure[attr]
            if issubclass(st.type, Array):
                l = st.type.length
                if st.format == Formats.HEX:
                    temp_data.append([st.type.type(c, 16) for c in cells[j:j + l]])
                else:
                    temp_data.append([st.type.type(c) for c in cells[j:j + l]])
            elif issubclass(st.type, RestrictedDict):
                l = len(st.type.keys)
                if st.format == Formats.HEX:
                    temp_data.append([st.type.type(c, 16) for c in cells[j:j + l]])
                else:
                    temp_data.append([st.type.type(c) for c in cells[j:j + l]])
            elif issubclass(st.type, Flags): # TODO
                l = len(st.type.names)
            else:
                l = 1
                if st.format == Formats.HEX:
                    temp_data.append(st.type(cells[j], 16))
                else:
                    temp_data.append(st.type(cells[j]))
            j += l
        self.__init__(temp_data)

    def flatten(self):
        """Flatten the row."""
        temp_data = []
        for attr in self.__class__.structure:
            t = self.__class__.structure[attr].type
            if issubclass(t, (Flags, Array, RestrictedDict, Row)):
                temp_data.extend(self.__dict__[attr].flatten())
            else:
                temp_data.append(self.__dict__[attr])
        return temp_data

    def tojsonobject(self):
        """Output JSON object."""
        jsonobj = OrderedDict()
        for attr in self.__class__.structure:
            jsonobj[attr] = self.__dict__[attr].tojsonobject()
        return jsonobj

    def tostring(self):
        """Output string."""
        output = []
        for attr in self.__class__.structure:
            format = self.__class__.structure[attr].format
            if format == Formats.HEX:
                output.append(self.__dict__[attr].tohex())
            else:
                output.append(self.__dict__[attr].tostring())
        return u'\t'.join(output)

    @classmethod
    def true_size(cls):
        """"""
        st = cls.structure
        return sum([st[attr].type.size for attr in st])

    @classmethod
    def true_fstring(cls):
        """"""
        st = cls.structure
        return '<' + ''.join([st[attr].type.fstring for attr in st])


class Formats(object):
    """Output Formats."""
    HEX = 0
    STR = 1


class Structure(object):
    """Store data structure for Row class."""
    def __init__(self, type, format):
        if type not in (U8, S8, U16, S16, U32, S32, Label) and \
            not issubclass(type, (Flags, Row, Array, RestrictedDict)):
            raise ValueError('invalid input format')
        object.__setattr__(self, 'type', type)
        object.__setattr__(self, 'format', format)

    def __setattr__(self, name, value):
        raise AttributeError('can\'t set attribute')

    def __str__(self): # For debug
        return str(type) + ' ' + str(format)

class Table(list):
    """A generic data structure, contains multiple Row objects.

    It is recommended to inherit from this class rather than use it directly.
    """
    type = None

    def __init__(self, *args, **kwargs):
        list.__init__(self, **kwargs)
        if len(args) > 0:
            if isinstance(args[0], unicode):
                lines = args[0].split(u'\n')
                for line in lines:
                    self.append(self.__class__.type(line))
            else:
                for item in args[0]:
                    self.append(self.__class__.type(item))

    def __setitem__(self, index, item):
        # Set an item to a given position.
        if not isinstance(item, self.__class__.type):
            raise TypeError(self.__class__.__name__ + ' object is required.')
        list.__setitem__(self, index, item)

    def append(self, item):
        """Add a new item to the end of the list."""
        if not isinstance(item, self.__class__.type):
            raise TypeError(self.__class__.__name__ + ' object is required.')
        list.append(self, item)

    def extend(self, item_list):
        """Extend the list by appending all the items in the given list."""
        if not isinstance(item_list, self.__class__):
            raise TypeError('Table object is required')
        list.extend(self, item_list)

    def insert(self, index, item):
        """Insert an item at a given position."""
        list.insert(self, index, self.__class__.type(item))

    def flatten(self):
        """Flatten the table."""
        return [r.flatten() for r in self]

    def tojsonobject(self):
        """Output JSON object."""
        return [r.tojsonobject() for r in self]

    def tostring(self):
        """Output string."""
        return u'\n'.join([r.tostring() for r in self])
