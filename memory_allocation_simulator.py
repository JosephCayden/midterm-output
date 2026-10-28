#!/usr/bin/env python3
"""
The Memory Allocation Laboratory
Operating Systems LEC - Midterm

Run with:
    python memory_allocation_simulator.py

Assumptions:
- Initial holes are separate free regions in address order.
- Allocations split a selected hole.
- Each process receives exactly its requested size.
- Deallocation merges adjacent free segments within the same
  original hole.
- Internal fragmentation is 0 KB for this variable-sized model.
- External fragmentation = total free memory - largest free hole.
"""

from dataclasses import dataclass

INITIAL_HOLES = [100, 500, 200, 300, 600]

REQUESTS = [
    ("allocate", "P1", 212),
    ("allocate", "P2", 417),
    ("allocate", "P3", 112),
    ("allocate", "P4", 426),
    ("free", "P2", 0),
    ("allocate", "P5", 200),
]


@dataclass
class Segment:
    size: int
    process: str | None = None


def choose_hole(groups, requested_size, strategy):
    """Find a suitable free hole based on the allocation strategy."""
    candidates = []

    for group_index, group in enumerate(groups):
        for segment_index, segment in enumerate(group):
            if (
                segment.process is None
                and segment.size >= requested_size
            ):
                candidates.append(
                    (group_index, segment_index, segment.size)
                )

    if not candidates:
        return None

    if strategy == "First-Fit":
        chosen = candidates[0]

    elif strategy == "Best-Fit":
        chosen = min(candidates, key=lambda item: item[2])

    elif strategy == "Worst-Fit":
        chosen = max(candidates, key=lambda item: item[2])

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return chosen[0], chosen[1]


def coalesce(group):
    """Merge adjacent free segments within one original hole."""
    merged = []

    for segment in group:
        if (
            merged
            and merged[-1].process is None
            and segment.process is None
        ):
            merged[-1].size += segment.size
        else:
            merged.append(
                Segment(segment.size, segment.process)
            )

    return merged


def run_strategy(strategy):
    """Simulate the requests using the selected strategy."""
    groups = [
        [Segment(size)]
        for size in INITIAL_HOLES
    ]

    allocated = {}
    outcomes = []

    for action, process_id, size in REQUESTS:

        if action == "allocate":
            chosen = choose_hole(
                groups, size, strategy
            )

            if chosen is None:
                outcomes.append(
                    f"{process_id}={size} KB REJECTED"
                )
                continue

            group_index, segment_index = chosen
            hole = groups[group_index][segment_index]

            remainder = hole.size - size

            # Replace the free hole with the allocated segment.
            groups[group_index][segment_index] = Segment(
                size, process_id
            )

            # Keep any remaining space as a free segment.
            if remainder > 0:
                groups[group_index].insert(
                    segment_index + 1,
                    Segment(remainder)
                )

            allocated[process_id] = size

            outcomes.append(
                f"{process_id}={size} KB allocated"
            )

        elif action == "free":

            if process_id not in allocated:
                outcomes.append(
                    f"{process_id} not allocated; nothing to free"
                )
                continue

            # Mark the process's segment as free.
            for group in groups:
                for index, segment in enumerate(group):
                    if segment.process == process_id:
                        group[index] = Segment(segment.size)
                        break

            del allocated[process_id]

            # Merge neighboring free segments.
            groups = [
                coalesce(group)
                for group in groups
            ]

            outcomes.append(
                f"{process_id} deallocated"
            )

    segments = [
        segment
        for group in groups
        for segment in group
    ]

    total_free = sum(
        segment.size
        for segment in segments
        if segment.process is None
    )

    largest_hole = max(
        (
            segment.size
            for segment in segments
            if segment.process is None
        ),
        default=0
    )

    external_fragmentation = (
        total_free - largest_hole
    )

    memory_map = " | ".join(
        (
            f"{segment.process}({segment.size})"
            if segment.process
            else f"FREE({segment.size})"
        )
        for segment in segments
    )

    return {
        "strategy": strategy,
        "outcomes": outcomes,
        "memory_map": memory_map,
        "total_free": total_free,
        "largest_hole": largest_hole,
        "external_fragmentation": external_fragmentation,
        "internal_fragmentation": 0,
        "live_processes": sorted(allocated),
    }


def main():
    print("MEMORY ALLOCATION LABORATORY")
    print("=" * 60)

    print("Initial holes (KB):", INITIAL_HOLES)

    print("\nRequest sequence:")
    for action, process_id, size in REQUESTS:
        if action == "allocate":
            print(f"  Allocate {process_id}: {size} KB")
        else:
            print(f"  Deallocate {process_id}")

    strategies = [
        "First-Fit",
        "Best-Fit",
        "Worst-Fit"
    ]

    for strategy in strategies:
        result = run_strategy(strategy)

        print("\n" + "=" * 60)
        print(result["strategy"])
        print("=" * 60)

        print("\nAllocation outcomes:")

        for outcome in result["outcomes"]:
            print("  ", outcome)

        print("\nFinal memory map:")
        print(" ", result["memory_map"])

        print("\nMemory statistics:")
        print(
            f"  Total free memory: "
            f"{result['total_free']} KB"
        )
        print(
            f"  Largest free hole: "
            f"{result['largest_hole']} KB"
        )
        print(
            f"  External fragmentation: "
            f"{result['external_fragmentation']} KB"
        )
        print(
            f"  Internal fragmentation: "
            f"{result['internal_fragmentation']} KB"
        )
        print(
            "  Live processes:",
            ", ".join(result["live_processes"])
        )

    print("\nSimulation completed.")


if __name__ == "__main__":
    main()