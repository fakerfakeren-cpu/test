package com.oathbound.client;

import com.oathbound.Oathbound;
import com.oathbound.client.screen.ChronicleScreen;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModWorldgen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.function.Consumer;

/**
 * Client showcase ({@code -Doathbound.clienttest=true}): joins the self-test world, walks a camera through
 * every structure, lines up the bestiary, wakes each keeper, visits the Hollow Throne, opens every page of the
 * Chronicle, and saves a screenshot of each scene. Proves the renderers, models, textures and GUI on a real client.
 */
public final class Showcase {
    private record Scene(int wait, String name, Consumer<Minecraft> action) {}

    private static final List<Scene> SCENES = new ArrayList<>();
    private static int cursor = -1;
    private static int countdown = 200;
    private static int preJoin;
    private static volatile boolean joined, finished;

    private Showcase() {}

    public static boolean enabled() {
        return Boolean.getBoolean("oathbound.clienttest");
    }

    private static void log(String s) {
        Oathbound.LOGGER.info("[CLIENTTEST] {}", s);
    }

    public static void startWatchdog() {
        Thread t = new Thread(() -> {
            long start = System.currentTimeMillis();
            try {
                while (!finished) {
                    Thread.sleep(30_000);
                    long secs = (System.currentTimeMillis() - start) / 1000;
                    log("watchdog " + secs + "s joined=" + joined + " scene=" + cursor + "/" + SCENES.size());
                    if ((!joined && secs > 480) || secs > 1080) {
                        log("RESULT: FAIL (" + (joined ? "showcase did not finish" : "never joined") + ")");
                        Runtime.getRuntime().halt(4);
                    }
                }
            } catch (InterruptedException ignored) {
            }
        }, "oathbound-showcase-watchdog");
        t.setDaemon(true);
        t.start();
    }

    // ------------------------------------------------------------------ helpers
    private static void onServer(Minecraft mc, Consumer<ServerPlayer> r) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (server == null) return;
        server.execute(() -> {
            try {
                if (!server.getPlayerList().getPlayers().isEmpty()) r.accept(server.getPlayerList().getPlayers().get(0));
            } catch (Throwable e) {
                Oathbound.LOGGER.error("[CLIENTTEST] server action failed", e);
            }
        });
    }

    private static void run(Minecraft mc, String command) {
        onServer(mc, p -> p.level().getServer().getCommands().performPrefixedCommand(
            p.level().getServer().createCommandSourceStack().withEntity(p).withPosition(p.position()).withRotation(p.getRotationVector()).withLevel(p.level()), command));
    }

    /** Puts the spectator camera at {@code eye}, looking at {@code focus}, in the given dimension. */
    private static void frame(Minecraft mc, String dim, Vec3 eye, Vec3 focus) {
        Vec3 d = focus.subtract(eye);
        float yaw = (float) (Math.atan2(-d.x, d.z) * 180 / Math.PI);
        float pitch = (float) (-Math.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)) * 180 / Math.PI);
        run(mc, String.format(Locale.ROOT, "execute in %s run tp @s %.2f %.2f %.2f %.1f %.1f", dim, eye.x, eye.y - 1.62, eye.z, yaw, pitch));
    }

    private static void shoot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "oathbound_" + name + ".png", mc.gameRenderer.mainRenderTarget(), 1, msg -> log("shot " + name + ": " + msg.getString()));
    }

    private static int groundAt(Minecraft mc, int x, int z) {
        return mc.level == null ? 70 : mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
    }

    private static void scene(int wait, String name, Consumer<Minecraft> action) {
        SCENES.add(new Scene(wait, name, action));
    }

    private static void still(ServerLevel level, EntityType<? extends Mob> type, Vec3 at, float yaw) {
        Mob m = type.create(level, EntitySpawnReason.COMMAND);
        if (m == null) return;
        m.snapTo(at.x, at.y, at.z, yaw, 0);
        m.setNoAi(true);
        m.setPersistenceRequired();
        m.setYHeadRot(yaw);
        m.yBodyRot = yaw;
        level.addFreshEntity(m);
    }

    // ------------------------------------------------------------------ the tour
    private static final String OW = "minecraft:overworld", GL = "oathbound:gloaming";

    /** Structure origins used by the self-test (x = 80 + i * 90, z = 200). */
    private static Vec3 site(Minecraft mc, int i) {
        int x = 80 + i * 90, z = 200;
        return new Vec3(x + 0.5, groundAt(mc, x, z), z + 0.5);
    }

    private static void script() {
        scene(20, "setup", mc -> {
            run(mc, "gamemode spectator");
            run(mc, "gamerule advance_time false");
            run(mc, "gamerule advance_weather false");
            run(mc, "gamerule send_command_feedback false");
            run(mc, "weather clear");
            run(mc, "time set 12600");
            mc.options.hideGui = true;
        });
        scene(60, "wayshrine", mc -> {
            Vec3 s = site(mc, 0);
            frame(mc, OW, s.add(9, 6, 10), s.add(0, 2, 0));
        });
        scene(120, "wayshrine_shot", mc -> shoot(mc, "wayshrine"));
        scene(10, "chapel", mc -> {
            Vec3 s = site(mc, 1);
            frame(mc, OW, s.add(16, 12, 22), s.add(0, 4, 0));
        });
        scene(140, "chapel_shot", mc -> shoot(mc, "drowned_chapel"));
        scene(10, "chapel_nave", mc -> {
            Vec3 s = site(mc, 1);
            frame(mc, OW, s.add(0, 4, 10), s.add(0, 2, -9));
        });
        scene(100, "chapel_nave_shot", mc -> shoot(mc, "chapel_bells"));
        scene(10, "spire", mc -> {
            Vec3 s = site(mc, 2);
            frame(mc, OW, s.add(22, 20, 26), s.add(0, 22, 0));
        });
        scene(140, "spire_shot", mc -> shoot(mc, "arcanist_spire"));
        scene(10, "dials", mc -> {
            Vec3 s = site(mc, 2);
            frame(mc, OW, s.add(0, 27.5, -3), s.add(0, 25.5, 3));
        });
        scene(100, "dials_shot", mc -> shoot(mc, "rune_dials"));
        scene(10, "barrow", mc -> {
            Vec3 s = site(mc, 3);
            frame(mc, OW, s.add(14, 9, 22), s.add(0, 2, 0));
        });
        scene(140, "barrow_shot", mc -> shoot(mc, "barrow_of_kings"));
        scene(10, "tombs", mc -> {
            Vec3 s = site(mc, 3);
            frame(mc, OW, s.add(0, -7.5, -3.5), s.add(0, -9.5, -9));
        });
        scene(100, "tombs_shot", mc -> shoot(mc, "hall_of_kings"));
        scene(10, "citadel", mc -> {
            Vec3 s = site(mc, 4);
            frame(mc, OW, s.add(0, 5, 8), s.add(0, 4, -10));
        });
        scene(140, "citadel_shot", mc -> shoot(mc, "sundered_gate"));
        scene(10, "bestiary", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 640;
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z) + 12;
            for (int dx = -2; dx <= 26; dx++)
                for (int dz = -3; dz <= 3; dz++) level.setBlock(new BlockPos(x + dx, y - 1, z + dz), com.oathbound.registry.ModBlocks.WARDSTONE_BRICKS.get().defaultBlockState(), 2);
            float yaw = 180f;
            double cx = x + 0.5;
            for (var t : List.of(ModEntities.LANTERNMOTH, ModEntities.GLOAMLING, ModEntities.FORSWORN_KNIGHT, ModEntities.BARROW_WIGHT, ModEntities.ANIMATED_TOME,
                ModEntities.VEILHOUND, ModEntities.SPECTRAL_HOUSECARL)) {
                still(level, t.get(), new Vec3(cx, y + (t == ModEntities.LANTERNMOTH || t == ModEntities.ANIMATED_TOME ? 1.5 : 0), z + 0.5), yaw);
                cx += 3.5;
            }
            p.teleportTo(level, x + 11, y + 2.2 - 1.62 + 0.3, z - 9.5, java.util.Set.of(), 0f, 8f, false);
        }));
        scene(120, "bestiary_shot", mc -> shoot(mc, "bestiary"));
        scene(10, "keepers", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 700;
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z) + 12;
            for (int dx = -4; dx <= 24; dx++)
                for (int dz = -4; dz <= 4; dz++) level.setBlock(new BlockPos(x + dx, y - 1, z + dz), com.oathbound.registry.ModBlocks.GLOAMSTONE_BRICKS.get().defaultBlockState(), 2);
            double cx = x + 0.5;
            for (var t : List.of(ModEntities.SIR_CALDRIS, ModEntities.ARCHMAGE_VEYL, ModEntities.HRODGAR)) {
                Mob m = t.get().create(level, EntitySpawnReason.COMMAND);
                if (m == null) continue;
                m.snapTo(cx, y + (t == ModEntities.ARCHMAGE_VEYL ? 1 : 0), z + 0.5, 180f, 0);
                m.setNoAi(true);
                m.setYHeadRot(180f);
                m.yBodyRot = 180f;
                if (m instanceof com.oathbound.entity.boss.KeeperEntity k) k.wake(level, null);
                level.addFreshEntity(m);
                cx += 8;
            }
            p.teleportTo(level, x + 8, y + 3 - 1.62 + 0.5, z - 13, java.util.Set.of(), 0f, 10f, false);
        }));
        scene(140, "keepers_shot", mc -> shoot(mc, "seal_keepers"));
        scene(10, "gloaming", mc -> onServer(mc, p -> {
            ServerLevel g = p.level().getServer().getLevel(ModWorldgen.GLOAMING);
            if (g == null) return;
            com.oathbound.event.GloamingTravel.ensureThrone(g);
            if (g.getEntities(ModEntities.MORVANE.get(), e -> e.isAlive()).isEmpty()) {
                var m = ModEntities.MORVANE.get().create(g, EntitySpawnReason.COMMAND);
                if (m != null) {
                    m.snapTo(0.5, 72.5, -12.4, 0f, 0f);
                    m.setHome(com.oathbound.event.GloamingTravel.THRONE);
                    g.addFreshEntity(m);
                }
            }
        }));
        scene(40, "throne", mc -> frame(mc, GL, new Vec3(0.5, 78, 26), new Vec3(0.5, 72, -8)));
        scene(160, "throne_shot", mc -> shoot(mc, "hollow_throne"));
        scene(10, "king", mc -> frame(mc, GL, new Vec3(3.5, 74.5, -3), new Vec3(0.5, 73.5, -10.5)));
        scene(100, "king_shot", mc -> shoot(mc, "morvane"));
        scene(10, "island", mc -> frame(mc, GL, new Vec3(40, 110, 90), new Vec3(0, 70, 0)));
        scene(160, "island_shot", mc -> shoot(mc, "the_gloaming"));
        scene(10, "book_setup", mc -> {
            run(mc, "execute in minecraft:overworld run tp @s 80 120 640");
            run(mc, "gamemode creative");
            run(mc, "give @s oathbound:lantern_chronicle");
            for (String q : List.of("lantern", "wayshrine", "hymn", "oathsteel_arms", "lanternmoth")) run(mc, "oathbound stage " + q);
            mc.options.hideGui = false;
        });
        String[] tabs = {"path", "story", "tithes", "bestiary", "armory"};
        int[] ids = {ChronicleScreen.TAB_PATH, ChronicleScreen.TAB_STORY, ChronicleScreen.TAB_TITHES, ChronicleScreen.TAB_BESTIARY, ChronicleScreen.TAB_ARMORY};
        for (int i = 0; i < tabs.length; i++) {
            final int tab = ids[i];
            final String name = tabs[i];
            scene(i == 0 ? 80 : 10, "book_" + name, mc -> mc.setScreenAndShow(new ChronicleScreen(net.minecraft.world.InteractionHand.MAIN_HAND, tab)));
            scene(40, "book_" + name + "_shot", mc -> shoot(mc, "chronicle_" + name));
        }
        scene(20, "finish", mc -> {
            mc.setScreenAndShow(null);
            log("RESULT: PASS");
            finished = true;
            mc.stop();
        });
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) {
            if (++preJoin % 100 == 0) log("waiting for world");
            if (preJoin % 1200 == 0) {
                log("quick play did not join; opening 'world' directly");
                mc.createWorldOpenFlows().openWorld("world", () -> log("open cancelled"));
            }
            return;
        }
        joined = true;
        if (cursor == -1) {
            script();
            cursor = 0;
            log("world joined, " + SCENES.size() + " scenes");
        }
        if (cursor >= SCENES.size() || --countdown > 0) return;
        Scene s = SCENES.get(cursor++);
        log("scene " + s.name());
        try {
            s.action().accept(mc);
        } catch (Throwable t) {
            Oathbound.LOGGER.error("[CLIENTTEST] scene {} failed", s.name(), t);
        }
        countdown = cursor < SCENES.size() ? SCENES.get(cursor).wait() : 0;
    }
}
