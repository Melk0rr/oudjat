class LogicalOperation:

    @staticmethod
    def from_str(operator: str, *args) -> int | bool:
        """
        Runs a logical operation based on a given operator

        Args:
            operator (str): the logical operator used to run a specific logical operation
            *args         : arguments to pass to the logical operation

        Returns:
            int | bool: the result of the logical operation that matches the provided operator
        """

        options = {
            "OR": LogicalOperation.logical_or,
            "AND": LogicalOperation.logical_and,
            "XOR": LogicalOperation.logical_xor,
            "XAND": LogicalOperation.logical_xand,
            "NOT": LogicalOperation.logical_not,
            "NOR": LogicalOperation.logical_nor,
            "NAND": LogicalOperation.logical_nand,
        }

        return options[operator](*args)


    @staticmethod
    def logical_or(a: int | bool, b: int | bool) -> int | bool:
        """
        Does an OR operation on provided values.

        Args:
            a (int | bool): The first operand to be compared.
            b (int | bool): The second operand to be compared.

        Returns:
            int | bool: The result of the OR operation between `a` and `b`.
        """

        return a | b

    @staticmethod
    def logical_and(a: int | bool, b: int | bool) -> int | bool:
        """
        Does an AND operation on provided values.

        Args:
            a (int | bool): The first operand to be compared.
            b (int | bool): The second operand to be compared.

        Returns:
            int | bool: The result of the AND operation between `a` and `b`.
        """

        return a & b

    @staticmethod
    def logical_xor(a: int | bool, b: int | bool) -> int | bool:
        """
        Does a XOR operation on provided values.

        Args:
            a (int | bool): The first operand to be compared.
            b (int | bool): The second operand to be compared.

        Returns:
            int | bool: The result of the XOR operation between `a` and `b`.
        """

        return a ^ b

    @staticmethod
    def logical_xand(a: int | bool, b: int | bool) -> int | bool:
        """
        Does a XAND operation on provided values.
        This is defined as the XOR operation between the result of AND between `a` and `b`, and the result of OR between `a` and `b`.

        Args:
            a (int | bool): The first operand to be compared.
            b (int | bool): The second operand to be compared.

        Returns:
            int | bool: The result of the XAND operation between `a` and `b`.
        """

        return LogicalOperation.logical_xor(LogicalOperation.logical_and(a, b), LogicalOperation.logical_or(a, b))

    @staticmethod
    def logical_not(a: int | bool) -> int | bool:
        """
        Does a NOT operation on provided value.

        Args:
            a (int | bool): The operand to be negated.

        Returns:
            int | bool: The result of the NOT operation on `a`.
        """

        return not a if type(a) is bool else ~a

    @staticmethod
    def logical_nor(a: int | bool, b: int | bool) -> int | bool:
        """
        Does a NOR operation on provided values.
        This is defined as the NOT of the result of ORing `a` and `b`.

        Args:
            a (int | bool): The first operand to be compared.
            b (int | bool): The second operand to be compared.

        Returns:
            int | bool: The result of the NOR operation between `a` and `b`.
        """

        return LogicalOperation.logical_not(LogicalOperation.logical_or(a, b))

    @staticmethod
    def logical_nand(a: int | bool, b: int | bool) -> int | bool:
        """
        Does a NAND operation on provided values.
        This is defined as the NOT of the result of ANDing `a` and `b`.

        Args:
            a (int | bool): The first operand to be compared.
            b (int | bool): The second operand to be compared.

        Returns:
            int | bool: The result of the NAND operation between `a` and `b`.
        """

        return LogicalOperation.logical_not(LogicalOperation.logical_and(a, b))


