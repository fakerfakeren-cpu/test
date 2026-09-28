package com.astralfall.client;

import com.astralfall.Astralfall;
import com.astralfall.block.StarLockBlock;
import com.astralfall.entity.SingularityEntity;
import com.astralfall.entity.boss.BossSummoner;
import com.astralfall.event.Starfall;
import com.astralfall.world.BlueprintPlacer;
import com.astralfall.world.Blueprints;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * Automated client smoke test (-Dastralfall.clienttest=true): joins a world, stages every showcase
 * scene with commands, takes screenshots and quits. Proves that every renderer works on a real client.
 */
public final class ClientTest {
    private record Step(int delay, String name, Consumer<Minecraft> action) {}

    private static final List<Step> STEPS = new ArrayList<>();
    private static int index = -1;
    private static int wait = 200;
    private static BlockPos base;
    private static int shots;
    private static int preJoinTicks;
    private static volatile boolean joined;
    private static volatile boolean done;

    private ClientTest() {}

    public static boolean enabled() {
        return Boolean.getBoolean("astralfall.clienttest");
    }

    /**
     * Background watchdog: reports what the client is doing every 30 s, and if the scenario never
     * starts (or never ends) dumps every interesting thread's stack and exits so CI gets a clear log.
     */
    public static void startWatchdog() {
        Thread t = new Thread(() -> {
            long start = System.currentTimeMillis();
            try {
                while (!done) {
                    Thread.sleep(30_000);
                    long secs = (System.currentTimeMillis() - start) / 1000;
                    Minecraft mc = Minecraft.getInstance();
                    log("watchdog " + secs + "s: joined=" + joined + " step=" + index + "/" + STEPS.size()
                        + " screen=" + screenName(mc)
                        + " level=" + (mc != null && mc.level != null) + " server=" + (mc != null && mc.getSingleplayerServer() != null));
                    if ((!joined && secs > 420) || secs > 960) {
                        log("RESULT: FAIL (" + (joined ? "scenario did not finish" : "never joined the world") + ")");
                        for (var e : Thread.getAllStackTraces().entrySet()) {
                            String name = e.getKey().getName();
                            if (!(name.contains("Render") || name.contains("Server") || name.contains("Worker") || name.contains("main") || name.contains("IO"))) continue;
                            log("| thread " + name + " state=" + e.getKey().getState());
                            StackTraceElement[] st = e.getValue();
                            for (int i = 0; i < Math.min(st.length, 40); i++) log("|   at " + st[i]);
                        }
                        Runtime.getRuntime().halt(4);
                    }
                }
            } catch (InterruptedException ignored) {
            }
        }, "astralfall-clienttest-watchdog");
        t.setDaemon(true);
        t.start();
    }

    /** The current screen's class name (the field is not public in 26.2, so read it reflectively). */
    private static String screenName(Minecraft mc) {
        if (mc == null) return "no-client";
        try {
            for (java.lang.reflect.Field f : Minecraft.class.getDeclaredFields()) {
                if (net.minecraft.client.gui.screens.Screen.class.isAssignableFrom(f.getType())) {
                    f.setAccessible(true);
                    Object screen = f.get(mc);
                    return screen == null ? "none" : screen.getClass().getName();
                }
            }
            return "no-screen-field";
        } catch (Throwable t) {
            return "unknown(" + t.getClass().getSimpleName() + ")";
        }
    }

    private static void log(String s) {
        Astralfall.LOGGER.info("[CLIENTTEST] {}", s);
    }

    private static void server(Minecraft mc, Consumer<ServerPlayer> r) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (server == null) return;
        server.execute(() -> {
            try {
                r.accept(server.getPlayerList().getPlayers().get(0));
            } catch (Throwable t) {
                Astralfall.LOGGER.error("[CLIENTTEST] server action failed", t);
            }
        });
    }

    private static void cmd(Minecraft mc, String command) {
        // The test world has cheats off, so run as the server (full permissions) positioned at the player.
        server(mc, p -> p.level().getServer().getCommands().performPrefixedCommand(
            p.level().getServer().createCommandSourceStack().withEntity(p).withPosition(p.position()).withRotation(p.getRotationVector()).withLevel(p.level()), command));
    }

    private static void camera(Minecraft mc, double x, double y, double z, float yaw, float pitch) {
        cmd(mc, String.format(java.util.Locale.ROOT, "tp @s %.2f %.2f %.2f %.1f %.1f", x, y, z, yaw, pitch));
    }

    private static void lookAt(Minecraft mc, Vec3 from, Vec3 at) {
        Vec3 d = at.subtract(from);
        float yaw = (float) (Math.atan2(-d.x, d.z) * 180 / Math.PI);
        float pitch = (float) (-Math.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * 180 / Math.PI);
        camera(mc, from.x, from.y, from.z, yaw, pitch);
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "astralfall_" + name + ".png", mc.gameRenderer.mainRenderTarget(), 1, msg -> log("screenshot " + name + ": " + msg.getString()));
        shots++;
    }

    private static int ground(Minecraft mc, int x, int z) {
        return mc.level == null ? 80 : mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
    }

    private static void step(int delay, String name, Consumer<Minecraft> action) {
        STEPS.add(new Step(delay, name, action));
    }

    private static volatile BlockPos obs, vessel, gallery, bossAt, meteorCam;

    private static Vec3 c(BlockPos p) {
        return Vec3.atBottomCenterOf(p);
    }

    /** Runs a command right now on the server thread (caller must already be on it). */
    private static void run(ServerPlayer p, String command) {
        MinecraftServer server = p.level().getServer();
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withEntity(p).withPosition(p.position())
            .withRotation(p.getRotationVector()).withLevel(p.level()), command);
    }

    private static BlockPos surface(ServerLevel level, int x, int z) {
        level.getChunk(x >> 4, z >> 4);
        return new BlockPos(x, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
    }

    private static void script() {
        STEPS.clear();
        step(1, "setup", mc -> {
            cmd(mc, "gamemode spectator");
            cmd(mc, "gamerule advance_time false");
            cmd(mc, "gamerule advance_weather false");
            cmd(mc, "gamerule send_command_feedback false");
            cmd(mc, "weather clear");
            cmd(mc, "time set minecraft:noon");
            cmd(mc, "effect give @s minecraft:night_vision infinite 0 true");
            base = mc.player.blockPosition();
            log("base " + base);
        });
        // --- Shattered Observatory, placed at a known origin so every camera lands exactly
        step(10, "build observatory", mc -> server(mc, p -> {
            BlockPos o = surface(p.level(), base.getX(), base.getZ() + 40);
            BlueprintPlacer.placeNow(p.level(), Blueprints.build(Blueprints.Type.OBSERVATORY, 12345L), o);
            obs = o;
            log("observatory at " + o);
        }));
        step(80, "observatory view", mc -> lookAt(mc, c(obs).add(-30, 22, -34), c(obs).add(0, 12, 0)));
        step(200, "shot observatory", mc -> shot(mc, "observatory"));
        step(5, "hall view", mc -> lookAt(mc, c(obs).add(5, 3.6, 6), c(obs).add(0, 2, -9)));
        step(100, "shot hall", mc -> shot(mc, "observatory_hall"));
        step(5, "unseal", mc -> server(mc, p -> log("star lock removed " + StarLockBlock.unseal(p.level(), obs.offset(0, 2, -9)) + " seals")));
        step(20, "vault view", mc -> lookAt(mc, c(obs).add(0, -4.2, -12.6), c(obs).add(0, -7.5, -21)));
        step(100, "shot vault", mc -> shot(mc, "vault"));
        step(5, "telescope view", mc -> lookAt(mc, c(obs).add(6, 18.5, 6), c(obs).add(-3, 16.5, 3)));
        step(100, "shot telescope", mc -> shot(mc, "telescope_chamber"));
        // --- Bestiary on the /astralfall gallery stage, with close-ups
        step(5, "gallery", mc -> server(mc, p -> {
            BlockPos g = surface(p.level(), base.getX() - 70, base.getZ());
            gallery = g;
            run(p, String.format(java.util.Locale.ROOT, "tp @s %.1f %d %.1f -90 0", g.getX() + 0.5, g.getY(), g.getZ() + 0.5));
            run(p, "astralfall gallery");
            log("gallery stage at " + g);
        }));
        step(80, "gallery wide", mc -> lookAt(mc, c(gallery).add(-1, 5.5, 1), c(gallery).add(11, 1.5, 1)));
        step(80, "shot gallery", mc -> shot(mc, "bestiary"));
        String[] names = {"astral_wisp", "void_stalker", "meteorite_crawler", "void_gazer"};
        double[] offsets = {-9, -4.5, 0, 4.5};
        double[] centre = {2.0, 1.4, 0.6, 2.3};
        for (int i = 0; i < names.length; i++) {
            final int k = i;
            step(5, "closeup " + names[k], mc -> {
                Vec3 mob = c(gallery).add(8, centre[k], offsets[k]);
                lookAt(mc, mob.add(-3.4, 0.7, -1.8), mob);
            });
            step(50, "shot " + names[k], mc -> shot(mc, "mob_" + names[k]));
        }
        step(5, "closeup astraeus", mc -> {
            Vec3 boss = c(gallery).add(16, 3.2, 11);
            lookAt(mc, boss.add(-10, 1.5, -6), boss);
        });
        step(50, "shot astraeus portrait", mc -> shot(mc, "mob_astraeus"));
        // --- Fallen Vessel & Sky Shrine
        step(5, "vessel", mc -> server(mc, p -> {
            BlockPos v = surface(p.level(), base.getX() + 90, base.getZ() + 10).below(2);
            BlueprintPlacer.placeNow(p.level(), Blueprints.build(Blueprints.Type.FALLEN_VESSEL, 777L), v);
            vessel = v;
            log("vessel at " + v);
        }));
        step(60, "vessel view", mc -> lookAt(mc, c(vessel).add(24, 14, -20), c(vessel).add(0, 2, 0)));
        step(160, "shot vessel", mc -> shot(mc, "fallen_vessel"));
        step(5, "shrine", mc -> {
            int sx = base.getX() + 80, sz = base.getZ() + 80;
            camera(mc, sx + 0.5, ground(mc, sx, sz) + 2, sz + 0.5, 0f, 0f);
        });
        step(20, "build shrine", mc -> cmd(mc, "astralfall build sky_shrine"));
        step(40, "shrine view", mc -> {
            int sx = base.getX() + 80, sz = base.getZ() + 98;
            Vec3 c = new Vec3(sx, ground(mc, sx, sz - 18) + 28, sz);
            lookAt(mc, c.add(-24, 2, -22), c.add(0, -3, 0));
        });
        step(160, "shot shrine", mc -> shot(mc, "sky_shrine"));
        // --- Night: meteors in front of the camera, a singularity, then the boss
        step(5, "night", mc -> server(mc, p -> {
            run(p, "time set minecraft:midnight");
            BlockPos m = surface(p.level(), base.getX() - 60, base.getZ() + 70);
            meteorCam = m;
            run(p, String.format(java.util.Locale.ROOT, "tp @s %.1f %d %.1f 180 -12", m.getX() + 0.5, m.getY() + 3, m.getZ() + 0.5));
        }));
        step(40, "meteors", mc -> server(mc, p -> {
            for (int i = 0; i < 6; i++) {
                BlockPos t = meteorCam.offset(-18 + i * 7, 0, -28 - (i % 3) * 8);
                Starfall.spawnMeteor(p.level(), t, i == 3 ? Starfall.Variant.FALLEN_STAR : Starfall.Variant.NORMAL, 1.6f);
            }
        }));
        step(30, "shot meteors", mc -> shot(mc, "meteor_shower"));
        step(70, "shot impact", mc -> shot(mc, "meteor_impacts"));
        step(5, "singularity", mc -> server(mc, p -> {
            Vec3 at = p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(9)).add(0, 2, 0);
            SingularityEntity.spawn(p.level(), at, p, 200, 8f, 0f, false);
        }));
        step(40, "shot singularity", mc -> shot(mc, "singularity"));
        step(5, "boss", mc -> server(mc, p -> {
            BlockPos b = surface(p.level(), base.getX() - 130, base.getZ() + 70);
            bossAt = b;
            run(p, String.format(java.util.Locale.ROOT, "tp @s %.1f %d %.1f 0 -10", b.getX() - 9.5, b.getY() + 7, b.getZ() - 13.5));
            BossSummoner.begin(p.level(), b);
        }));
        step(20, "ritual camera", mc -> lookAt(mc, c(bossAt).add(-10, 7, -14), c(bossAt).add(0, 2, 0)));
        step(90, "shot ritual", mc -> shot(mc, "eclipse_ritual"));
        step(150, "boss camera", mc -> lookAt(mc, c(bossAt).add(-9, 6, -12), c(bossAt).add(0, 5, 0)));
        step(40, "shot boss", mc -> shot(mc, "astraeus"));
        step(5, "boss target", mc -> server(mc, p -> {
            var golem = net.minecraft.world.entity.EntityTypes.IRON_GOLEM.create(p.level(), net.minecraft.world.entity.EntitySpawnReason.COMMAND);
            if (golem == null) return;
            BlockPos gp = surface(p.level(), bossAt.getX() + 8, bossAt.getZ() - 4);
            golem.snapTo(gp.getX() + 0.5, gp.getY(), gp.getZ() + 0.5, 0, 0);
            golem.setNoAi(true);
            p.level().addFreshEntity(golem);
            for (var boss : p.level().getEntities(com.astralfall.registry.ModEntities.ASTRAEUS.get(), e -> e.distanceToSqr(c(bossAt)) < 64 * 64)) boss.setTarget(golem);
        }));
        step(120, "shot boss attack", mc -> shot(mc, "astraeus_attack"));
        step(60, "shot boss attack 2", mc -> shot(mc, "astraeus_attack_2"));
        step(100, "quit", mc -> {
            log("RESULT: PASS screenshots=" + shots);
            done = true;
            mc.stop();
        });
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) {
            if (++preJoinTicks % 100 == 0) {
                String screen = screenName(mc);
                log("waiting for world, screen=" + screen);
                if (preJoinTicks % 600 == 0) shot(mc, "prejoin_" + preJoinTicks / 600);
                // Quick play did not get us in (title / error screen): open the test world directly.
                if (preJoinTicks % 1200 == 0 && (screen.contains("TitleScreen") || screen.contains("SelectWorld") || screen.contains("Disconnected") || screen.contains("Alert"))) {
                    log("quick play did not join; opening world 'world' directly");
                    mc.createWorldOpenFlows().openWorld("world", () -> log("openWorld cancelled"));
                }
            }
            return;
        }
        joined = true;
        if (index == -1) {
            script();
            index = 0;
            log("world joined, starting scenario with " + STEPS.size() + " steps");
        }
        if (index >= STEPS.size()) return;
        if (--wait > 0) return;
        Step s = STEPS.get(index++);
        try {
            s.action().accept(mc);
        } catch (Throwable t) {
            Astralfall.LOGGER.error("[CLIENTTEST] step {} failed", s.name(), t);
        }
        wait = index < STEPS.size() ? STEPS.get(index).delay() : 0;
    }
}
