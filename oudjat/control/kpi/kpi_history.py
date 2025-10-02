"""A module to track KPI history."""

from datetime import datetime

from oudjat.utils import ColorPrint

from .kpi import KPI
from .kpi_comparator import KPIComparator, KPIComparatorTendency


class KPIHistoryNode:
    """
    A class that describes a node in a KPIHistory.
    """

    def __init__(self, kpi: KPI) -> None:
        """
        Return a new instance of KPIHistoryNode.

        Args:
            kpi (KPI)            : the KPI that compose the node
            prev (KPIHistoryNode): previous node in the history
            next (KPIHistoryNode): next node in the history
        """

        self._kpi: KPI = kpi
        self._prev: KPIHistoryNode | None = None
        self._next: KPIHistoryNode | None = None

    @property
    def kpi(self) -> KPI:
        """
        Return the node's KPI instance.

        Returns:
            kpi (KPI): kpi instance of the current node
        """

        return self._kpi

    @property
    def prev(self) -> "KPIHistoryNode | None":
        """
        Return the previous history node.

        Returns:
            KPIHistoryNode | None: previous node in the KPI history
        """

        return self._prev

    @prev.setter
    def prev(self, new_node: "KPIHistoryNode | None") -> None:
        """
        Change the reference to the previous history node.

        Args:
            new_node (KPIHistoryNode): new previous node ref
        """

        self._prev = new_node

    @property
    def next(self) -> "KPIHistoryNode | None":
        """
        Return the next history node.

        Returns:
            KPIHistoryNode | None: next node in the KPI history
        """

        return self._next

    @next.setter
    def next(self, new_node: "KPIHistoryNode | None") -> None:
        """
        Change the reference to the next history node.

        Args:
            new_node (KPIHistoryNode): new next node ref
        """

        self._next = new_node

    def compare_next(self) -> KPIComparator:
        """
        Generate a KPIComparator instance with the next node.

        Returns:
            KPIComparator: KPI comparator instance for current node kpi and next node kpi
        """

        if self.next is None:
            raise ValueError(
                f"{__class__.__name__}.compare_next::Next history node is None. Can't compare it !"
            )

        return KPIComparator(self.kpi, self.next.kpi)

    def compare_prev(self) -> KPIComparator:
        """
        Generate a KPIComparator instance with the next node.

        Returns:
            KPIComparator: KPI comparator instance for current node kpi and next node kpi
        """

        if self.prev is None:
            raise ValueError(
                f"{__class__.__name__}.compare_next::Previous history node is None. Can't compare it !"
            )

        return KPIComparator(self.prev.kpi, self.kpi)


class KPIHistory:
    """KPIEvolution class to handle."""

    def __init__(self, name: str, kpis: list[KPI] | None = None) -> None:
        """
        Create a new instance of KPIHistory.

        Args:
            name (str)                : The name of the object instance.
            kpis (list[KPI], optional): A list of KPI objects to initialize with. Defaults to an empty list.
        """

        self._name: str = name
        self._begin: KPIHistoryNode | None
        self._end: KPIHistoryNode | None
        self._size: int = 0

        if kpis is not None:
            for kpi in kpis:
                self.insert_by_date(kpi)

    @property
    def name(self):
        """
        Return the name of KPIHistory.

        Returns:
            str: name given to the current KPIHistory instance
        """

        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Set a new name for the current KPIHistory instance.

        Args:
            new_name (str): new value for the name of this KPIHistory
        """

        self._name = new_name

    @property
    def size(self) -> int:
        """
        Return the size of the current KPIHistory.

        Returns:
            int: the number of KPIHistoryNode in the current KPIHistory instance
        """

        return self._size

    @property
    def is_empty(self) -> bool:
        """
        Return whether the history is empty or not.

        Returns:
            bool: True if the history is empty. False otherwise
        """

        return self._end is None

    def set_kpis(self, kpis: list[KPI]) -> None:
        """
        Setter for the kpi list. Updates the list of KPIs in the class.

        Args:
            kpis (List[KPI], optional): A list of KPI objects to set. Defaults to an empty list.
        """

        self.clear()

        for kpi in kpis:
            self.insert_by_date(kpi)

    def append(self, kpi: KPI) -> None:
        """
        Append a new KPI into the history.

        Args:
            kpi (KPI): new kpi to append
        """

        new_node = KPIHistoryNode(kpi)

        if self.is_empty:
            self._begin = new_node
            self._end = new_node

        else:
            assert self._end is not None

            self._end.next = new_node
            new_node.prev = self._end
            self._end = new_node

        self._size += 1

    def prepend(self, kpi: KPI) -> None:
        """
        Prepend a new KPI into the history.

        Args:
            kpi (KPI): new kpi to prepend
        """

        new_node = KPIHistoryNode(kpi)

        if self.is_empty:
            self._begin = new_node
            self._end = new_node

        else:
            assert self._begin is not None

            self._begin.prev = new_node
            new_node.next = self._begin
            self._begin = new_node

        self._size += 1

    def insert_by_date(self, kpi: KPI) -> None:
        """
        Insert a new kpi in the history based on its date.

        Args:
            kpi (KPI): kpi to insert
        """

        if self.is_empty:
            self.append(kpi)

        else:
            assert self._begin is not None
            tmp = self._begin

            while tmp is not None:
                if kpi.date >= tmp.kpi.date:
                    if tmp.next is None:
                        self.append(kpi)

                    elif tmp.prev is None:
                        self.prepend(kpi)

                    else:
                        new_node = KPIHistoryNode(kpi)

                        tmp.prev.next = new_node
                        tmp.next.prev = new_node

                        new_node.prev = tmp.prev
                        new_node.next = tmp

                        self._size += 1

                else:
                    tmp = tmp.next

    def pop_back(self) -> None:
        """
        Remove the last history element.
        """
        if not self.is_empty:
            assert self._end is not None

            if self._begin is self._end:
                self._end.prev = None
                self._end.next = None
                self._begin = None
                self._end = None

            else:
                assert self._end.prev is not None

                tmp = self._end

                self._end = self._end.prev
                self._end.next = None

                tmp.prev = None
                tmp.next = None
                tmp = None

            self._size -= 1

    def clear(self) -> None:
        """
        Clear the current history list.
        """

        while not self.is_empty:
            self.pop_back()

    def build(self, detailed: bool = False) -> None:
        """Build the history of KPIs by comparing each pair in order based on their dates."""

        if not self.is_empty:
            tmp = self._begin
            while tmp is not None:
    def logs(self, detailed: bool = False) -> list[str]:
        """
        Return a list of log strings based on the current history content.

        Returns:
            list[str]: a list of strings representing comparison between each KPI
        """

        logs: list[str] = []

        def logs_cb(node: KPIHistoryNode | None) -> None:
            if node is not None:
                if self._begin is self._end:
                    logs.append(str(node.kpi) if detailed else f"{node.kpi.value}%")

                else:
                    compare: KPIComparator = node.compare_next()
                    logs.append(str(compare) if detailed else f"{compare.tendency}")

        self.go_through(logs_cb)
        return logs

    def tendency(self) -> KPIComparatorTendency:
        """
        Return the tendency of the current KPIHistory.

        Each KPIComparator gives a tendency from a KPI A to a KPI B.
        A KPIHistory tendency results from the tendencies of all the comparisons of the KPIs in the history.

        Args:
            argument_name: type and description.

        Returns:
            KPIComparatorTendency: tendency computed out from the comparison of each KPI.
        """

        tendency = KPIComparatorTendency.EQ
        if not self.is_empty:
            tendency_counts: dict[str, int] = {"INC": 0, "DEC": 0, "EQ": 0}

            tmp = self._begin
            while tmp is not None:
                if self._begin is not self._end:
                    tendency_counts[f"{tmp.compare_next().tendency}"] += 1

                tmp = tmp.next

            tendency_str: str = max(tendency_counts, key=lambda t: tendency_counts[t])
            tendency = KPIComparatorTendency[tendency_str]

        return tendency

    def print_history(self) -> None:
        """Print the history of KPIs by calling each comparator's print method to display their comparison results."""

        comparator_len = len(self.comparators)
        if comparator_len == 0:
            self.build_history()

        ColorPrint.blue(f"\n {self.name} History")

        for i in range(comparator_len):
            self.comparators[i].print_tendency(
                print_first_value=(i == 0), sfx=(i == comparator_len - 1) and "\n" or ""
            )
