package org.jabref.logic.autosaveandbackup;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/**
 * Modified class to use only java.util packages.
 */
public class AutosaveManager {

    private static final int DELAY_BETWEEN_AUTOSAVE_ATTEMPTS_IN_SECONDS = 31;

    private static Set<AutosaveManager> runningInstances = new HashSet<>();

    private final BlockingQueue<Runnable> workerQueue;
    private final ExecutorService executor;

    private AutosaveManager() {
        this.workerQueue = new ArrayBlockingQueue<>(1);
        this.executor = new ThreadPoolExecutor(1, 1, 0, TimeUnit.SECONDS, workerQueue);
    }

    public void attemptAutosave() {
        try {
            executor.submit(() -> {
                // Simulate the autosave event
            });
        } catch (RejectedExecutionException e) {
            System.out.println("Rejecting autosave while another save process is already running.");
        }
    }

    private void shutdown() {
        executor.shutdown();
    }

    public static AutosaveManager start() {
        AutosaveManager autosaveManager = new AutosaveManager();
        runningInstances.add(autosaveManager);
        return autosaveManager;
    }

    public static void shutdownAll() {
        for (AutosaveManager instance : runningInstances) {
            instance.shutdown();
        }
        runningInstances.clear();
    }
}
