package coursework.concurrent;

import java.util.Arrays;
import java.util.Random;

public final class ParallelMergeSortTest {
    private ParallelMergeSortTest() {
    }

    public static void main(String[] args) {
        testEdgeCases();
        testFixedValues();
        testRandomValuesAgainstReference();
        testInvalidArguments();
        System.out.println("ParallelMergeSortTest: all checks passed");
    }

    private static void testEdgeCases() {
        for (int workers : new int[] {1, 2, 4, 8}) {
            long[] empty = {};
            ParallelMergeSort.parallelSort(empty, workers);
            require(empty.length == 0, "empty array changed");

            long[] single = {42};
            ParallelMergeSort.parallelSort(single, workers);
            require(Arrays.equals(single, new long[] {42}), "single value changed");
        }
    }

    private static void testFixedValues() {
        long[] input = {5, -1, 5, Long.MAX_VALUE, 0, Long.MIN_VALUE, 3};
        long[] expected = Arrays.copyOf(input, input.length);
        Arrays.sort(expected);

        long[] sequential = Arrays.copyOf(input, input.length);
        ParallelMergeSort.sequentialSort(sequential);
        require(Arrays.equals(sequential, expected), "sequential fixed case failed");

        for (int workers : new int[] {1, 2, 4, 8}) {
            long[] actual = Arrays.copyOf(input, input.length);
            ParallelMergeSort.parallelSort(actual, workers);
            require(Arrays.equals(actual, expected), "parallel fixed case failed");
        }
    }

    private static void testRandomValuesAgainstReference() {
        Random generator = new Random(240678L);
        for (int size : new int[] {2, 3, 31, 1_000, 10_003}) {
            long[] input = generator.longs(size, -1_000_000, 1_000_000).toArray();
            long[] expected = Arrays.copyOf(input, input.length);
            Arrays.sort(expected);

            long[] sequential = Arrays.copyOf(input, input.length);
            ParallelMergeSort.sequentialSort(sequential);
            require(Arrays.equals(sequential, expected), "sequential random case failed");
            require(ParallelMergeSort.isSorted(sequential), "sequential order check failed");

            for (int workers : new int[] {1, 2, 4, 8}) {
                long[] actual = Arrays.copyOf(input, input.length);
                ParallelMergeSort.parallelSort(actual, workers);
                require(Arrays.equals(actual, expected), "parallel random case failed");
                require(ParallelMergeSort.isSorted(actual), "parallel order check failed");
            }
        }
    }

    private static void testInvalidArguments() {
        expectFailure(() -> ParallelMergeSort.sequentialSort(null));
        expectFailure(() -> ParallelMergeSort.parallelSort(null, 2));
        expectFailure(() -> ParallelMergeSort.parallelSort(new long[] {1}, 0));
        expectFailure(() -> ParallelMergeSort.isSorted(null));
    }

    private static void expectFailure(Runnable action) {
        try {
            action.run();
            throw new AssertionError("expected IllegalArgumentException");
        } catch (IllegalArgumentException expected) {
            // Expected path.
        }
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
