package com.oathbound.util;

import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.function.Consumer;

/** Tiny server-side "do this in N ticks" queue, used for melodies, rituals and staged effects. Not persisted. */
public final class Scheduler {
    private record Task(ResourceKey<Level> dimension, long due, Consumer<ServerLevel> action) {}

    private static final List<Task> TASKS = new ArrayList<>();

    private Scheduler() {}

    public static synchronized void later(ServerLevel level, int ticks, Consumer<ServerLevel> action) {
        TASKS.add(new Task(level.dimension(), level.getGameTime() + Math.max(1, ticks), action));
    }

    public static void tick(ServerLevel level) {
        List<Task> due = new ArrayList<>();
        synchronized (Scheduler.class) {
            Iterator<Task> it = TASKS.iterator();
            while (it.hasNext()) {
                Task t = it.next();
                if (t.dimension() == level.dimension() && t.due() <= level.getGameTime()) {
                    due.add(t);
                    it.remove();
                }
            }
        }
        for (Task t : due) {
            try {
                t.action().accept(level);
            } catch (Throwable e) {
                com.oathbound.Oathbound.LOGGER.error("Scheduled task failed", e);
            }
        }
    }
}
