class CustomMetaEnum(type):
    def __new__(self, name, bases, namespace):
        # Create empty dict to hold constants (ex. A = 1)
        fields = {}

        # Copy constants from the namespace to the fields dict.
        fields = {k: v for k, v in namespace.items()}

        # In case we're about to create a subclass, copy all constants from the base classes' _fields
        for base in bases:
            fields.update(base._fields)

        # Save constants as _fields in the new class' namespace.
        namespace["_fields"] = fields
        return super().__new__(self, name, bases, namespace)

    def __iter__(self):
        return iter([{k: v} for k, v in self._fields.items() if k in self._member_names_])

    def test(self):
        print(self.__name__)

    @property
    def _member_names_(self):
        all_member_names = list(self._fields.keys())
        filtered_member_names = list(filter(lambda n: "__" not in n, all_member_names))

        return filtered_member_names

