package coursework.concurrent;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.SplittableRandom;

/** Reproducible wall-clock benchmark for sequential and concurrent sorting. */
public final class Benchmark {
    private static final int[] FULL_SIZES = {100_000, 500_000, 2_000_000};
    private static final int[] QUICK_SIZES = {1_000, 10_000};
    private static final int[] WORKER_COUNTS = {1, 2, 4, 8};

    private Benchmark() {
    }

    public static void main(String[] args) throws IOException {
        Arguments arguments = Arguments.parse(args);
        warmUp();
        List<Result> results = run(
                arguments.quick ? QUICK_SIZES : FULL_SIZES,
                arguments.trials);
        writeCsv(results, arguments.output);
        printSummary(results);
        System.out.println("\nRaw measurements written to " + arguments.output.toAbsolutePath());
    }

    static List<Result> run(int[] sizes, int trials) {
        List<Result> results = new ArrayList<>();
        for (int size : sizes) {
            long[] input = generate(size, 240_678L + size);
            long[] reference = Arrays.copyOf(input, input.length);
            Arrays.sort(reference);

            for (int trial = 1; trial <= trials; trial++) {
                List<Configuration> configurations = configurations();
                Collections.rotate(configurations, (trial - 1) % configurations.size());
                for (Configuration configuration : configurations) {
                    long[] actual = Arrays.copyOf(input, input.length);
                    long start = System.nanoTime();
                    if (configuration.parallel) {
                        ParallelMergeSort.parallelSort(actual, configuration.workers);
                    } else {
                        ParallelMergeSort.sequentialSort(actual);
                    }
                    long elapsed = System.nanoTime() - start;
                    boolean correct = Arrays.equals(actual, reference)
                            && ParallelMergeSort.isSorted(actual);
                    if (!correct) {
                        throw new IllegalStateException(
                                "incorrect result for " + configuration.label);
                    }
                    results.add(new Result(
                            configuration.label,
                            size,
                            configuration.workers,
                            trial,
                            elapsed,
                            true,
                            Arrays.hashCode(actual)));
                }
            }
        }
        return results;
    }

    static long[] generate(int size, long seed) {
        if (size < 0) {
            throw new IllegalArgumentException("size must not be negative");
        }
        SplittableRandom generator = new SplittableRandom(seed);
        long[] values = new long[size];
        for (int index = 0; index < size; index++) {
            values[index] = generator.nextLong();
        }
        return values;
    }

    private static void warmUp() {
        long[] input = generate(50_000, 240_678L);
        for (int repeat = 0; repeat < 2; repeat++) {
            long[] sequential = Arrays.copyOf(input, input.length);
            ParallelMergeSort.sequentialSort(sequential);
            long[] parallel = Arrays.copyOf(input, input.length);
            ParallelMergeSort.parallelSort(parallel, 4);
        }
    }

    private static List<Configuration> configurations() {
        List<Configuration> configurations = new ArrayList<>();
        configurations.add(new Configuration("Sequential", 1, false));
        for (int workers : WORKER_COUNTS) {
            configurations.add(new Configuration("Parallel", workers, true));
        }
        return configurations;
    }

    private static void writeCsv(List<Result> results, Path output) throws IOException {
        Path parent = output.toAbsolutePath().getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        try (BufferedWriter writer = Files.newBufferedWriter(
                output,
                StandardCharsets.UTF_8)) {
            writer.write("algorithm,elements,workers,trial,total_ns,correct,checksum");
            writer.newLine();
            for (Result result : results) {
                writer.write(String.format(
                        Locale.ROOT,
                        "%s,%d,%d,%d,%d,%s,%d",
                        result.algorithm,
                        result.elements,
                        result.workers,
                        result.trial,
                        result.totalNs,
                        result.correct,
                        result.checksum));
                writer.newLine();
            }
        }
    }

    private static void printSummary(List<Result> results) {
        System.out.println("Task 5 sort benchmark");
        System.out.println("-".repeat(72));
        for (Result result : results) {
            if (result.trial != 1) {
                continue;
            }
            System.out.printf(
                    Locale.ROOT,
                    "%-10s workers=%d n=%9d time=%9.3f ms correct=%s%n",
                    result.algorithm,
                    result.workers,
                    result.elements,
                    result.totalNs / 1_000_000.0,
                    result.correct);
        }
    }

    static final class Result {
        final String algorithm;
        final int elements;
        final int workers;
        final int trial;
        final long totalNs;
        final boolean correct;
        final int checksum;

        Result(
                String algorithm,
                int elements,
                int workers,
                int trial,
                long totalNs,
                boolean correct,
                int checksum) {
            this.algorithm = algorithm;
            this.elements = elements;
            this.workers = workers;
            this.trial = trial;
            this.totalNs = totalNs;
            this.correct = correct;
            this.checksum = checksum;
        }
    }

    private static final class Configuration {
        final String label;
        final int workers;
        final boolean parallel;

        Configuration(String label, int workers, boolean parallel) {
            this.label = label;
            this.workers = workers;
            this.parallel = parallel;
        }
    }

    private static final class Arguments {
        final Path output;
        final int trials;
        final boolean quick;

        Arguments(Path output, int trials, boolean quick) {
            this.output = output;
            this.trials = trials;
            this.quick = quick;
        }

        static Arguments parse(String[] args) {
            Path output = Path.of("experiments", "data", "task5_benchmarks.csv");
            int trials = 5;
            boolean quick = false;
            for (int index = 0; index < args.length; index++) {
                switch (args[index]) {
                    case "--output":
                        output = Path.of(requireValue(args, ++index, "--output"));
                        break;
                    case "--trials":
                        trials = Integer.parseInt(requireValue(args, ++index, "--trials"));
                        break;
                    case "--quick":
                        quick = true;
                        break;
                    default:
                        throw new IllegalArgumentException("unknown argument: " + args[index]);
                }
            }
            if (trials < 1) {
                throw new IllegalArgumentException("trials must be positive");
            }
            return new Arguments(output, trials, quick);
        }

        private static String requireValue(String[] args, int index, String option) {
            if (index >= args.length) {
                throw new IllegalArgumentException(option + " requires a value");
            }
            return args[index];
        }
    }
}
