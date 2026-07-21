"""Constraint-aware exam timetabling using backtracking and pruning."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Exam:
    identifier: str
    students: int

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("exam identifier must not be empty")
        if self.students <= 0:
            raise ValueError("exam must have at least one student")


@dataclass(frozen=True, slots=True)
class Room:
    identifier: str
    capacity: int

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("room identifier must not be empty")
        if self.capacity <= 0:
            raise ValueError("room capacity must be positive")


@dataclass(frozen=True, slots=True)
class Placement:
    slot: int
    room: str


@dataclass(frozen=True, slots=True)
class TimetableEvent:
    step: int
    action: str
    exam: str
    slot: int
    room: str
    assigned_count: int


@dataclass(frozen=True, slots=True)
class TimetableResult:
    assignments: dict[str, Placement]
    solved: bool
    nodes_visited: int
    backtracks: int
    forward_prunes: int
    events: tuple[TimetableEvent, ...]


class ExamTimetabler:
    """Assign exams to slot/room pairs under graph-colouring constraints."""

    def __init__(
        self,
        exams: Iterable[Exam],
        conflicts: Iterable[tuple[str, str]],
        slots: int,
        rooms: Iterable[Room],
    ) -> None:
        self.exams = tuple(exams)
        self.rooms = tuple(sorted(rooms, key=lambda room: (-room.capacity, room.identifier)))
        if slots <= 0:
            raise ValueError("slot count must be positive")
        self.slots = slots
        self._validate_unique_identifiers()
        self._exam_by_id = {exam.identifier: exam for exam in self.exams}
        self._conflicts = {exam.identifier: set() for exam in self.exams}
        for left, right in conflicts:
            if left not in self._conflicts or right not in self._conflicts:
                raise ValueError("conflict refers to an unknown exam")
            if left == right:
                raise ValueError("an exam cannot conflict with itself")
            self._conflicts[left].add(right)
            self._conflicts[right].add(left)

    def solve(self, use_pruning: bool = True) -> TimetableResult:
        assignments: dict[str, Placement] = {}
        occupied: set[tuple[int, str]] = set()
        events: list[TimetableEvent] = []
        counters = {"nodes": 0, "backtracks": 0, "prunes": 0}

        solved = self._search(
            assignments,
            occupied,
            events,
            counters,
            use_pruning,
        )
        return TimetableResult(
            assignments=dict(assignments),
            solved=solved,
            nodes_visited=counters["nodes"],
            backtracks=counters["backtracks"],
            forward_prunes=counters["prunes"],
            events=tuple(events),
        )

    def validate(self, assignments: dict[str, Placement]) -> bool:
        """Check whether a complete assignment satisfies every constraint."""

        if set(assignments) != set(self._exam_by_id):
            return False
        occupied: set[tuple[int, str]] = set()
        room_by_id = {room.identifier: room for room in self.rooms}
        for exam_id, placement in assignments.items():
            if not 0 <= placement.slot < self.slots:
                return False
            room = room_by_id.get(placement.room)
            if room is None or room.capacity < self._exam_by_id[exam_id].students:
                return False
            resource = (placement.slot, placement.room)
            if resource in occupied:
                return False
            occupied.add(resource)
            if any(
                neighbour in assignments
                and assignments[neighbour].slot == placement.slot
                for neighbour in self._conflicts[exam_id]
            ):
                return False
        return True

    def _search(
        self,
        assignments: dict[str, Placement],
        occupied: set[tuple[int, str]],
        events: list[TimetableEvent],
        counters: dict[str, int],
        use_pruning: bool,
    ) -> bool:
        if len(assignments) == len(self.exams):
            return True

        exam_id = self._choose_exam(assignments, occupied, use_pruning)
        candidates = self._domain(exam_id, assignments, occupied)
        if use_pruning:
            candidates = self._break_slot_symmetry(candidates, assignments)
            candidates.sort(
                key=lambda placement: self._elimination_score(
                    exam_id,
                    placement,
                    assignments,
                    occupied,
                )
            )

        for placement in candidates:
            counters["nodes"] += 1
            assignments[exam_id] = placement
            occupied.add((placement.slot, placement.room))
            events.append(
                TimetableEvent(
                    step=len(events) + 1,
                    action="assign",
                    exam=exam_id,
                    slot=placement.slot,
                    room=placement.room,
                    assigned_count=len(assignments),
                )
            )

            viable = True
            if use_pruning:
                viable = self._forward_check(assignments, occupied)
                if not viable:
                    counters["prunes"] += 1
            if viable and self._search(
                assignments,
                occupied,
                events,
                counters,
                use_pruning,
            ):
                return True

            occupied.remove((placement.slot, placement.room))
            assignments.pop(exam_id)
            counters["backtracks"] += 1
            events.append(
                TimetableEvent(
                    step=len(events) + 1,
                    action="backtrack",
                    exam=exam_id,
                    slot=placement.slot,
                    room=placement.room,
                    assigned_count=len(assignments),
                )
            )
        return False

    def _choose_exam(
        self,
        assignments: dict[str, Placement],
        occupied: set[tuple[int, str]],
        use_pruning: bool,
    ) -> str:
        unassigned = [
            exam.identifier for exam in self.exams if exam.identifier not in assignments
        ]
        if not use_pruning:
            return unassigned[0]
        return min(
            unassigned,
            key=lambda exam_id: (
                len(self._domain(exam_id, assignments, occupied)),
                -len(self._conflicts[exam_id]),
                exam_id,
            ),
        )

    def _domain(
        self,
        exam_id: str,
        assignments: dict[str, Placement],
        occupied: set[tuple[int, str]],
    ) -> list[Placement]:
        exam = self._exam_by_id[exam_id]
        blocked_slots = {
            assignments[neighbour].slot
            for neighbour in self._conflicts[exam_id]
            if neighbour in assignments
        }
        return [
            Placement(slot, room.identifier)
            for slot in range(self.slots)
            for room in self.rooms
            if room.capacity >= exam.students
            and slot not in blocked_slots
            and (slot, room.identifier) not in occupied
        ]

    def _forward_check(
        self,
        assignments: dict[str, Placement],
        occupied: set[tuple[int, str]],
    ) -> bool:
        return all(
            self._domain(exam.identifier, assignments, occupied)
            for exam in self.exams
            if exam.identifier not in assignments
        )

    def _elimination_score(
        self,
        exam_id: str,
        placement: Placement,
        assignments: dict[str, Placement],
        occupied: set[tuple[int, str]],
    ) -> int:
        before = 0
        after = 0
        for exam in self.exams:
            if exam.identifier in assignments or exam.identifier == exam_id:
                continue
            before += len(self._domain(exam.identifier, assignments, occupied))
        assignments[exam_id] = placement
        occupied.add((placement.slot, placement.room))
        for exam in self.exams:
            if exam.identifier in assignments:
                continue
            after += len(self._domain(exam.identifier, assignments, occupied))
        occupied.remove((placement.slot, placement.room))
        assignments.pop(exam_id)
        return before - after

    def _break_slot_symmetry(
        self,
        candidates: list[Placement],
        assignments: dict[str, Placement],
    ) -> list[Placement]:
        used_slots = {placement.slot for placement in assignments.values()}
        unused_slots = [slot for slot in range(self.slots) if slot not in used_slots]
        first_unused = min(unused_slots, default=None)
        return [
            placement
            for placement in candidates
            if placement.slot in used_slots or placement.slot == first_unused
        ]

    def _validate_unique_identifiers(self) -> None:
        exam_ids = [exam.identifier for exam in self.exams]
        room_ids = [room.identifier for room in self.rooms]
        if len(set(exam_ids)) != len(exam_ids):
            raise ValueError("exam identifiers must be unique")
        if len(set(room_ids)) != len(room_ids):
            raise ValueError("room identifiers must be unique")
        if not self.exams:
            raise ValueError("at least one exam is required")
        if not self.rooms:
            raise ValueError("at least one room is required")
