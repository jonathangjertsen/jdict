from collections import UserDict
import json
import sys

# Prevent importing jdict from versions below 3.6
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    raise Exception("jdict will not behave correctly on Python versions below 3.6.")

class JDict(UserDict):
    """Dictionary extended with convenience methods that depend heavily on dictionaries being ordered by insertion order"""
    # Protect attributes used for housekeeping
    protected_keys = (
        'data',
        '_keys',
        '_values',
        '_items',
        '_keysvalid',
        '_valuesvalid',
        '_itemsvalid',
    )
    
    @staticmethod
    def _first(obj):
        """Helper: Returns the first element in the object"""
        for elem in obj:
            return elem
    
    @staticmethod
    def _last(obj):
        """Helper: Returns the last element in the object"""
        try:
            return obj[-1]
        except IndexError:
            return None
    
    @staticmethod
    def _at(idx, enumiterator):
        """Helper: Returns the n'th element in the enumerated iterator"""
        for _idx, *item in enumiterator:
            if idx == _idx:
                return tuple(item)
        raise IndexError(idx)
    
    def _pop(self, key):
        """Helper: pops the item at the key"""
        if len(self.data) == 0:
            raise IndexError("pop from empty JDict")
        value = self.data[key]
        del self.data[key]
        self._invalidate()
        return key, value
    
    def __init__(self, data=None):
        """Sets attributes used for housekeeping"""
        if data is None:
            data = {}
        self.data = data
        self._cleanse()
        self._invalidate()
    
    def _cleanse(self):
        """Drops everything"""
        self._keys = []
        self._values = []
        self._items = []
    
    def _invalidate(self):
        """Sets all flags to invalid (so the keylist, valuelist and itemlist must be recalculated)"""
        self._keysvalid = False
        self._valuesvalid = False
        self._itemsvalid = False
    
    def _key_is_protected(self, key):
        """Returns whether the key is protected (should not override default __setattr__ for this key)"""
        return key in JDict.protected_keys
    
    def __getattr__(self, key):
        """Makes jdict.x equivalent to jdict['x']"""
        try:
            return self.data[key]
        except KeyError as ke:
            raise AttributeError(key) from ke
    
    def __setattr__(self, key, value):
        """Makes jdict.x = y equivalent to jdict['x'] = y"""
        if self._key_is_protected(key):
            return object.__setattr__(self, key, value)
        else:
            self.data[key] = value
            self._invalidate()

    @property
    def keylist(self):
        """Returns a list of the keys"""
        if not self._keysvalid:
            self._keys = list(self.data)
            self._keysvalid = True
        return self._keys
    
    @property
    def valuelist(self):
        """Returns a list of the values"""
        if not self._valuesvalid:
            self._values = list(self.data.values())
            self._valuesvalid = True
        return self._values
    
    @property
    def itemlist(self):
        """Returns a list of the items ((key, value)-pairs)"""
        if not self._itemsvalid:
            self._items = list(self.data.items())
            self._itemsvalid = True
        return self._items
    
    @property
    def firstitem(self):
        """Returns the first item ((key, value)-pair)"""
        return self._first(self.data.items())
    
    @property
    def firstkey(self):
        """Returns the first key"""
        return self._first(self.data.keys())
    
    @property
    def firstvalue(self):
        """Returns the first value"""
        return self._first(self.data.values())
    
    @property
    def lastitem(self):
        """Returns the last item ((key, value)-pair)"""
        return self._last(self.itemlist)
    
    @property
    def lastkey(self):
        """Returns the last key"""
        return self._last(self.keylist)
    
    @property
    def lastvalue(self):
        """Returns the last value"""
        return self._last(self.valuelist)
    
    @property
    def anyitem(self):
        """Returns an item ((key, value)-pair) with no guarantees about which one it is"""
        return self.firstitem
    
    @property
    def anykey(self):
        """Returns any key with no guarantees about which one it is"""
        return self.firstkey
    
    @property
    def anyvalue(self):
        """Returns any value with no guarantees about which one it is"""
        return self.firstvalue
    
    @property
    def range(self):
        """Returns range(len(self))"""
        return range(len(self))
    
    @property
    def enumkeys(self):
        """Returns (idx, key)-pairs"""
        return enumerate(self.data.keys())
    
    @property
    def enumvalues(self):
        """Returns (idx, value)-pairs"""
        return enumerate(self.data.values())
    
    @property
    def enumitems(self):
        """Returns (idx, key, value)-tuples"""
        return zip(self.range, self.data.keys(), self.data.values())
    
    @property
    def json(self):
        """Returns a JSON representation"""
        return json.dumps(self.data)
    
    @property
    def series(self):
        """Returns a pandas Series representation"""
        import pandas as pd
        return pd.Series(index=self.keylist, data=self.valuelist)
    
    @property
    def datacol(self):
        """Returns a representation as a pandas DataFrame with one column"""
        import pandas as pd
        return pd.DataFrame(self.series)
    
    @property
    def datarow(self):
        """Returns a representation as a pandas DataFrame with one row"""
        import pandas as pd
        return pd.DataFrame(index=[0], data=self.data)
    
    def at(self, idx):
        """Returns the item at the index"""
        return self._at(idx, self.enumitems)
    
    def key_at(self, idx):
        """Returns the key at the index"""
        return self.at(idx)[0]
    
    def value_at(self, idx):
        """Returns the value at the index"""
        return self.at(idx)[1]
    
    def pop_first(self):
        """Pops the first (key, value)-pair and returns it"""
        return self._pop(self.firstkey)
    
    def pop_last(self):
        """Pops the last (key, value)-pair and returns it"""
        return self._pop(self.lastkey)
    
    def pop_first_key(self):
        """Pops the first (key, value)-pair and returns the key"""
        return self.pop_first()[0]
    
    def pop_first_value(self):
        """Pops the first (key, value)-pair and returns the value"""
        return self.pop_first()[1]
    
    def pop_last_key(self):
        """Pops the last (key, value)-pair and returns the key"""
        return self.pop_last()[0]
    
    def pop_last_value(self):
        """Pops the last (key, value)-pair and returns the key"""
        return self.pop_last()[1]