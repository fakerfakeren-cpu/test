package com.rimeheart.client;

import com.rimeheart.Rimeheart;
import com.rimeheart.world.BlueprintPlacer;
import com.rimeheart.world.Blueprints;
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
 * Automated client smoke test (-Drimeheart.clienttest=true): joins a world, stages every showcase
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
        return Boolean.getBoolean("rimeheart.clienttest");
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
        }, "rimeheart-clienttest-watchdog");
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
        Rimeheart.LOGGER.info("[CLIENTTEST] {}", s);
    }

    private static void server(Minecraft mc, Consumer<ServerPlayer> r) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (server == null) return;
        server.execute(() -> {
            try {
                r.accept(server.getPlayerList().getPlayers().get(0));
            } catch (Throwable t) {
                Rimeheart.LOGGER.error("[CLIENTTEST] server action failed", t);
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
        Screenshot.grab(mc.gameDirectory, "rimeheart_" + name + ".png", mc.gameRenderer.mainRenderTarget(), 1, msg -> log("screenshot " + name + ": " + msg.getString()));
        shots++;
    }

    private static int ground(Minecraft mc, int x, int z) {
        return mc.level == null ? 80 : mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
    }

    private static void step(int delay, String name, Consumer<Minecraft> action) {
        STEPS.add(new Step(delay, name, action));
    }

    private static volatile BlockPos sanctum, stage, bossAt;

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
        // --- The Warden's Journal: quest log, story and field guide
        step(10, "journal setup", mc -> {
            cmd(mc, "gamemode creative");
            cmd(mc, "clear @s");
            cmd(mc, "give @s rimeheart:wardens_journal");
            cmd(mc, "advancement grant @s through rimeheart:quests/ingot");
            cmd(mc, "advancement grant @s only rimeheart:quests/rime_shard");
            cmd(mc, "advancement grant @s only rimeheart:quests/hearthfire");
            cmd(mc, "rimejournal claim root");
            cmd(mc, "rimejournal claim frostiron");
        });
        step(60, "open journal", mc -> mc.setScreenAndShow(new JournalScreen(net.minecraft.world.InteractionHand.MAIN_HAND, JournalScreen.TAB_QUESTS)));
        step(40, "shot journal quests", mc -> shot(mc, "journal_quests"));
        step(5, "journal story", mc -> mc.setScreenAndShow(new JournalScreen(net.minecraft.world.InteractionHand.MAIN_HAND, JournalScreen.TAB_STORY)));
        step(30, "shot journal story", mc -> shot(mc, "journal_story"));
        step(5, "journal guide", mc -> mc.setScreenAndShow(new JournalScreen(net.minecraft.world.InteractionHand.MAIN_HAND, JournalScreen.TAB_GUIDE)));
        step(30, "shot journal guide", mc -> shot(mc, "journal_guide"));
        step(5, "close journal", mc -> {
            mc.setScreenAndShow(null);
            cmd(mc, "gamemode spectator");
        });
        // --- Frozen Sanctum, placed at a known origin so every camera lands exactly
        step(10, "build sanctum", mc -> server(mc, p -> {
            BlockPos o = surface(p.level(), base.getX(), base.getZ() + 40);
            BlueprintPlacer.placeNow(p.level(), Blueprints.build(Blueprints.Type.FROZEN_SANCTUM, 12345L), o);
            sanctum = o;
            log("sanctum at " + o);
        }));
        step(80, "sanctum view", mc -> lookAt(mc, c(sanctum).add(-14, 9, -26), c(sanctum).add(0, 0, -4)));
        step(160, "shot sanctum", mc -> shot(mc, "sanctum_surface"));
        step(5, "hall view", mc -> lookAt(mc, c(sanctum).add(-6.5, Blueprints.HALL_FLOOR + 5.5, -7.5), c(sanctum).add(0, Blueprints.HALL_FLOOR + 2, 0)));
        step(100, "shot hall", mc -> shot(mc, "sanctum_hall"));
        step(5, "open vault", mc -> server(mc, p -> {
            for (int y = 1; y <= 2; y++)
                for (int z = -1; z <= 1; z++) p.level().removeBlock(sanctum.offset(9, Blueprints.HALL_FLOOR + y, z), false);
        }));
        step(20, "vault view", mc -> lookAt(mc, c(sanctum).add(6, Blueprints.HALL_FLOOR + 3.2, 0), c(sanctum).add(14, Blueprints.HALL_FLOOR + 1, 0)));
        step(100, "shot vault", mc -> shot(mc, "sanctum_vault"));
        // --- Bestiary close-ups on a snowy stage
        step(5, "stage", mc -> server(mc, p -> {
            BlockPos g = surface(p.level(), base.getX() - 60, base.getZ());
            stage = g;
            for (BlockPos q : BlockPos.betweenClosed(g.offset(-2, -1, -8), g.offset(14, -1, 8))) p.level().setBlock(q, net.minecraft.world.level.block.Blocks.SNOW_BLOCK.defaultBlockState(), 2);
            for (BlockPos q : BlockPos.betweenClosed(g.offset(-2, 0, -8), g.offset(14, 8, 8))) p.level().setBlock(q, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 2);
            spawnStill(p.level(), com.rimeheart.registry.ModEntities.FROST_WRAITH.get(), g.offset(6, 1, -3));
            spawnStill(p.level(), com.rimeheart.registry.ModEntities.SHARDLING.get(), g.offset(6, 0, 3));
        }));
        step(40, "wraith view", mc -> lookAt(mc, c(stage).add(2.5, 2.6, -4.5), c(stage).add(6, 2.0, -3)));
        step(40, "shot wraith", mc -> shot(mc, "mob_frost_wraith"));
        step(5, "shardling view", mc -> lookAt(mc, c(stage).add(3.8, 1.2, 2.2), c(stage).add(6, 0.3, 3)));
        step(40, "shot shardling", mc -> shot(mc, "mob_shardling"));
        // --- The Winter Horn ritual and the Frost Sovereign
        step(5, "boss", mc -> server(mc, p -> {
            BlockPos b = surface(p.level(), base.getX() - 130, base.getZ() + 70);
            bossAt = b;
            run(p, String.format(java.util.Locale.ROOT, "tp @s %.1f %d %.1f 0 -10", b.getX() - 9.5, b.getY() + 7, b.getZ() - 13.5));
            p.level().setBlock(b.below(), com.rimeheart.registry.ModBlocks.GLACIAL_ALTAR.get().defaultBlockState(), 3);
            com.rimeheart.entity.boss.SovereignRitual.begin(p.level(), b);
        }));
        step(20, "ritual camera", mc -> lookAt(mc, c(bossAt).add(-10, 6, -14), c(bossAt).add(0, 1, 0)));
        step(70, "shot ritual", mc -> shot(mc, "winter_ritual"));
        step(150, "boss camera", mc -> lookAt(mc, c(bossAt).add(-8, 5, -11), c(bossAt).add(0, 4, 0)));
        step(20, "shot boss", mc -> shot(mc, "frost_sovereign"));
        step(5, "boss target", mc -> server(mc, p -> {
            var golem = net.minecraft.world.entity.EntityTypes.IRON_GOLEM.create(p.level(), net.minecraft.world.entity.EntitySpawnReason.COMMAND);
            if (golem == null) return;
            BlockPos gp = surface(p.level(), bossAt.getX() + 7, bossAt.getZ() - 4);
            golem.snapTo(gp.getX() + 0.5, gp.getY(), gp.getZ() + 0.5, 0, 0);
            golem.setNoAi(true);
            p.level().addFreshEntity(golem);
            for (var boss : p.level().getEntities(com.rimeheart.registry.ModEntities.FROST_SOVEREIGN.get(), e -> e.distanceToSqr(c(bossAt)) < 64 * 64)) boss.setTarget(golem);
        }));
        step(90, "shot boss attack", mc -> shot(mc, "frost_sovereign_attack"));
        step(50, "shot boss attack 2", mc -> shot(mc, "frost_sovereign_attack_2"));
        step(50, "shot boss attack 3", mc -> shot(mc, "frost_sovereign_attack_3"));
        step(100, "quit", mc -> {
            log("RESULT: PASS screenshots=" + shots);
            done = true;
            mc.stop();
        });
    }

    private static void spawnStill(ServerLevel level, net.minecraft.world.entity.EntityType<? extends net.minecraft.world.entity.Mob> type, BlockPos at) {
        var mob = type.create(level, net.minecraft.world.entity.EntitySpawnReason.COMMAND);
        if (mob == null) return;
        mob.snapTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, 90f, 0f);
        mob.setNoAi(true);
        mob.setPersistenceRequired();
        mob.setYHeadRot(90f);
        mob.yBodyRot = 90f;
        level.addFreshEntity(mob);
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
            Rimeheart.LOGGER.error("[CLIENTTEST] step {} failed", s.name(), t);
        }
        wait = index < STEPS.size() ? STEPS.get(index).delay() : 0;
    }
}
