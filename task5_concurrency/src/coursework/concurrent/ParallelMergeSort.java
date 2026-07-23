package coursework.concurrent;

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Sequential and concurrent bottom-up merge sort implementations.
 *
 * <p>Merge tasks within one pass read a shared source array and write disjoint
 * destination ranges. Only work-queue state is a critical section.</p>
 */
public final class ParallelMergeSort {
    private ParallelMergeSort() {
    }

    public static void sequentialSort(long[] values) {
        requireArray(values);
        if (values.length < 2) {
            return;
        }
        long[] source = Arrays.copyOf(values, values.length);
        long[] destination = new long[values.length];
        sortPasses(source, destination, values, null);
    }

    public static void parallelSort(long[] values, int workerCount) {
        requireArray(values);
        if (workerCount < 1) {
            throw new IllegalArgumentException("workerCount must be positive");
        }
        if (values.length < 2) {
            return;
        }

        long[] source = Arrays.copyOf(values, values.length);
        long[] destination = new long[values.length];
        try (WorkQueue workers = new WorkQueue(workerCount)) {
            sortPasses(source, destination, values, workers);
        }
    }

    public static boolean isSorted(long[] values) {
        requireArray(values);
        for (int index = 1; index < values.length; index++) {
            if (values[index - 1] > values[index]) {
                return false;
            }
        }
        return true;
    }

    private static void sortPasses(
            long[] initialSource,
            long[] initialDestination,
            long[] output,
            WorkQueue workers) {
        long[] source = initialSource;
        long[] destination = initialDestination;

        for (long width = 1; width < output.length; width *= 2) {
            int runWidth = (int) width;
            int mergeCount = (output.length + 2 * runWidth - 1) / (2 * runWidth);
            if (workers == null) {
                for (int mergeIndex = 0; mergeIndex < mergeCount; mergeIndex++) {
                    mergeAtIndex(source, destination, output.length, runWidth, mergeIndex);
                }
            } else {
                int taskCount = Math.min(workers.workerCount(), mergeCount);
                for (int taskIndex = 0; taskIndex < taskCount; taskIndex++) {
                    int firstMerge = taskIndex;
                    long[] taskSource = source;
                    long[] taskDestination = destination;
                    workers.submit(() -> {
                        for (int mergeIndex = firstMerge;
                                mergeIndex < mergeCount;
                                mergeIndex += taskCount) {
                            mergeAtIndex(
                                    taskSource,
                                    taskDestination,
                                    output.length,
                                    runWidth,
                                    mergeIndex);
                        }
                    });
                }
                workers.awaitCompletion();
            }
            long[] temporary = source;
            source = destination;
            destination = temporary;

            // Prevent overflow after the last meaningful power-of-two pass.
            if (width > output.length / 2L) {
                break;
            }
        }
        System.arraycopy(source, 0, output, 0, output.length);
    }

    private static void mergeAtIndex(
            long[] source,
            long[] destination,
            int length,
            int runWidth,
            int mergeIndex) {
        int left = mergeIndex * 2 * runWidth;
        int middle = Math.min(left + runWidth, length);
        int right = Math.min(left + 2 * runWidth, length);
        merge(source, destination, left, middle, right);
    }

    private static void merge(
            long[] source,
            long[] destination,
            int left,
            int middle,
            int right) {
        int first = left;
        int second = middle;
        int output = left;
        while (first < middle && second < right) {
            if (source[first] <= source[second]) {
                destination[output++] = source[first++];
            } else {
                destination[output++] = source[second++];
            }
        }
        while (first < middle) {
            destination[output++] = source[first++];
        }
        while (second < right) {
            destination[output++] = source[second++];
        }
    }

    private static void requireArray(long[] values) {
        if (values == null) {
            throw new IllegalArgumentException("values must not be null");
        }
    }

    /**
     * Fixed worker pool with explicit lock and condition-variable synchronisation.
     */
    private static final class WorkQueue implements AutoCloseable {
        private final Deque<Runnable> tasks = new ArrayDeque<>();
        private final ReentrantLock lock = new ReentrantLock();
        private final Condition workAvailable = lock.newCondition();
        private final Condition allDone = lock.newCondition();
        private final Thread[] workers;
        private int pendingTasks;
        private boolean shutdown;

        WorkQueue(int workerCount) {
            workers = new Thread[workerCount];
            for (int index = 0; index < workerCount; index++) {
                workers[index] = new Thread(this::workerLoop, "merge-worker-" + index);
                workers[index].start();
            }
        }

        int workerCount() {
            return workers.length;
        }

        void submit(Runnable task) {
            lock.lock();
            try {
                if (shutdown) {
                    throw new IllegalStateException("work queue is closed");
                }
                tasks.addLast(task);
                pendingTasks++;
                workAvailable.signal();
            } finally {
                lock.unlock();
            }
        }

        void awaitCompletion() {
            lock.lock();
            try {
                while (pendingTasks > 0) {
                    allDone.awaitUninterruptibly();
                }
            } finally {
                lock.unlock();
            }
        }

        @Override
        public void close() {
            awaitCompletion();
            lock.lock();
            try {
                shutdown = true;
                workAvailable.signalAll();
            } finally {
                lock.unlock();
            }
            for (Thread worker : workers) {
                try {
                    worker.join();
                } catch (InterruptedException error) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException("interrupted while joining workers", error);
                }
            }
        }

        private void workerLoop() {
            while (true) {
                Runnable task;
                lock.lock();
                try {
                    while (tasks.isEmpty() && !shutdown) {
                        workAvailable.awaitUninterruptibly();
                    }
                    if (tasks.isEmpty() && shutdown) {
                        return;
                    }
                    task = tasks.removeFirst();
                } finally {
                    lock.unlock();
                }

                try {
                    task.run();
                } finally {
                    lock.lock();
                    try {
                        pendingTasks--;
                        if (pendingTasks == 0) {
                            allDone.signalAll();
                        }
                    } finally {
                        lock.unlock();
                    }
                }
            }
        }
    }
}
