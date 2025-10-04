"""
Example demonstrating Position and Range helper methods.

This example shows the new utility methods added to Position and Range
classes that match the VS Code TypeScript API.
"""

from vscode_sockpuppet import VSCodeClient
from vscode_sockpuppet.document import Position, Range


def demonstrate_position_methods():
    """Demonstrate Position helper methods."""
    print("\n" + "=" * 60)
    print("Position Helper Methods")
    print("=" * 60)

    # Create some positions
    pos1 = Position(line=5, character=10)
    pos2 = Position(line=5, character=20)
    pos3 = Position(line=10, character=5)

    print("\nPositions created:")
    print(f"  pos1: {pos1}")
    print(f"  pos2: {pos2}")
    print(f"  pos3: {pos3}")

    # Comparison methods
    print("\nComparison methods:")
    print(f"  pos1.is_before(pos2):         {pos1.is_before(pos2)}")
    print(f"  pos1.is_after(pos2):          {pos1.is_after(pos2)}")
    print(f"  pos1.is_equal(pos1):          {pos1.is_equal(pos1)}")
    print(f"  pos1.is_before_or_equal(pos1): {pos1.is_before_or_equal(pos1)}")

    # Python operators (using __lt__, __eq__, etc.)
    print("\nPython comparison operators:")
    print(f"  pos1 < pos2:  {pos1 < pos2}")
    print(f"  pos1 > pos2:  {pos1 > pos2}")
    print(f"  pos1 == pos1: {pos1 == pos1}")
    print(f"  pos1 <= pos2: {pos1 <= pos2}")
    print(f"  pos1 >= pos2: {pos1 >= pos2}")

    # compare_to method
    print("\ncompare_to method:")
    print(f"  pos1.compare_to(pos2): {pos1.compare_to(pos2)}")
    print(f"  pos2.compare_to(pos1): {pos2.compare_to(pos1)}")
    print(f"  pos1.compare_to(pos1): {pos1.compare_to(pos1)}")

    # Translation
    print("\nTranslation methods:")
    moved = pos1.translate(line_delta=2, character_delta=5)
    print(f"  pos1.translate(2, 5):  {moved}")

    # With methods
    print("\nWith methods (immutable updates):")
    new_line = pos1.with_line(100)
    print(f"  pos1.with_line(100):      {new_line}")
    new_char = pos1.with_character(50)
    print(f"  pos1.with_character(50):  {new_char}")
    print(f"  Original pos1 unchanged:  {pos1}")


def demonstrate_range_methods():
    """Demonstrate Range helper methods."""
    print("\n" + "=" * 60)
    print("Range Helper Methods")
    print("=" * 60)

    # Create some ranges
    range1 = Range(
        start=Position(line=5, character=0),
        end=Position(line=5, character=10),
    )
    range2 = Range(
        start=Position(line=5, character=5),
        end=Position(line=5, character=15),
    )
    range3 = Range(
        start=Position(line=10, character=0),
        end=Position(line=15, character=0),
    )

    print("\nRanges created:")
    print(f"  range1: {range1}")
    print(f"  range2: {range2}")
    print(f"  range3: {range3}")

    # Properties
    print("\nRange properties:")
    print(f"  range1.is_empty:       {range1.is_empty}")
    print(f"  range1.is_single_line: {range1.is_single_line}")
    print(f"  range3.is_single_line: {range3.is_single_line}")

    # Contains (Position)
    pos = Position(line=5, character=7)
    print(f"\nContains position {pos}:")
    print(f"  range1.contains(pos): {range1.contains(pos)}")
    print(f"  range2.contains(pos): {range2.contains(pos)}")
    print(f"  pos in range1:        {pos in range1}")  # Pythonic syntax

    # Contains (Range)
    small_range = Range(
        start=Position(line=5, character=2),
        end=Position(line=5, character=8),
    )
    print(f"\nContains range {small_range}:")
    print(f"  range1.contains(small_range): {range1.contains(small_range)}")
    print(f"  small_range in range1:        {small_range in range1}")  # Pythonic

    # Equality
    range1_copy = Range(
        start=Position(line=5, character=0),
        end=Position(line=5, character=10),
    )
    print("\nEquality:")
    print(f"  range1.is_equal(range1_copy): {range1.is_equal(range1_copy)}")
    print(f"  range1 == range1_copy:        {range1 == range1_copy}")
    print(f"  range1 == range2:             {range1 == range2}")

    # Intersection
    print("\nIntersection of range1 and range2:")
    intersection = range1.intersection(range2)
    print(f"  Result: {intersection}")

    print("\nIntersection of range1 and range3 (no overlap):")
    no_intersection = range1.intersection(range3)
    print(f"  Result: {no_intersection}")

    # Union
    print("\nUnion of range1 and range2:")
    union = range1.union(range2)
    print(f"  Result: {union}")

    # With methods
    print("\nWith methods (immutable updates):")
    new_start = range1.with_start(Position(line=5, character=2))
    print(f"  range1.with_start(5,2): {new_start}")
    new_end = range1.with_end(Position(line=5, character=20))
    print(f"  range1.with_end(5,20):  {new_end}")
    print(f"  Original unchanged:     {range1}")


def demonstrate_with_real_document():
    """Demonstrate using helper methods with real documents."""
    print("\n" + "=" * 60)
    print("Real Document Usage")
    print("=" * 60)

    with VSCodeClient() as client:
        docs = client.workspace.text_documents()

        if not docs:
            print("\nNo open documents. Open a file to see this demo.")
            return

        doc = docs[0]
        print(f"\nWorking with: {doc.file_name}")
        print(f"Lines: {doc.line_count}")

        if doc.line_count > 5:
            # Get a range
            start = Position(line=0, character=0)
            end = Position(line=min(5, doc.line_count - 1), character=0)
            sample_range = Range(start=start, end=end)

            print(f"\nSample range: {sample_range}")
            print(f"  Is single line: {sample_range.is_single_line}")
            print(f"  Is empty: {sample_range.is_empty}")

            # Check if position is in range
            pos = Position(line=2, character=5)
            print(f"\nPosition {pos}:")
            print(f"  In range: {pos in sample_range}")

            # Get text in range
            text = doc.get_text(sample_range)
            print("\nText in range (first 100 chars):")
            print(f"  {repr(text[:100])}")

            # Translate position
            new_pos = pos.translate(line_delta=1)
            print(f"\nTranslate {pos} by 1 line:")
            print(f"  Result: {new_pos}")


def main():
    """Run all demonstrations."""
    print("Position and Range Helper Methods Demo")
    print("=" * 60)

    demonstrate_position_methods()
    demonstrate_range_methods()
    demonstrate_with_real_document()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("\nThese helper methods make Position and Range more")
    print("intuitive and match the VS Code TypeScript API.")


if __name__ == "__main__":
    main()
