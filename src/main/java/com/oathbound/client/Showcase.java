package com.oathbound.client;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.Oathbound;
import com.oathbound.client.screen.ChronicleScreen;
import com.oathbound.registry.ModBlocks;
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
    private record Scene(int delay, String name, Consumer<Minecraft> action) {}

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

    private static Mob still(ServerLevel level, EntityType<? extends Mob> type, Vec3 at, float yaw) {
        Mob m = type.create(level, EntitySpawnReason.COMMAND);
        if (m == null) return null;
        m.snapTo(at.x, at.y, at.z, yaw, 0);
        m.setNoAi(true);
        m.setPersistenceRequired();
        m.setYHeadRot(yaw);
        m.yBodyRot = yaw;
        level.addFreshEntity(m);
        return m;
    }

    /**
     * Levels a stage above the terrain: finds the highest ground under the rectangle, lays a floor two blocks above
     * it and clears the air over it, so a lineup never ends up inside a hillside or a cave.
     */
    private static int stage(ServerLevel level, int x0, int z0, int x1, int z1, net.minecraft.world.level.block.state.BlockState floor) {
        int ax = x0 - 2, bx = x1 + 2, az = z0 - 14, bz = z1 + 2;
        // Level.getHeight answers the world's floor for chunks that are not loaded, so load them first
        for (int cx = ax >> 4; cx <= bx >> 4; cx++)
            for (int cz = az >> 4; cz <= bz >> 4; cz++) level.getChunk(cx, cz);
        int y = level.getMinY(), top = level.getMinY();
        for (int x = ax; x <= bx; x++)
            for (int z = az; z <= bz; z++) {
                int h = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
                top = Math.max(top, h);
                if (x >= x0 && x <= x1 && z >= z0 && z <= z1) y = Math.max(y, h);
            }
        y += 2;
        int ceiling = Math.min(top + 2, y + 48);
        var air = net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
        for (int x = ax; x <= bx; x++)
            for (int z = az; z <= bz; z++) {
                if (x >= x0 && x <= x1 && z >= z0 && z <= z1) level.setBlock(new BlockPos(x, y - 1, z), floor, 2);
                for (int yy = y; yy <= Math.max(y + 12, ceiling); yy++) level.setBlock(new BlockPos(x, yy, z), air, 2);
            }
        return y;
    }

    private static BlockPos meadowSpot;
    private static int meadowY = 80;

    /** A patch of temperate country (forest, jungle, plains or meadow) where fireflies fly; found once per run. */
    private static BlockPos temperate(ServerLevel level) {
        if (meadowSpot != null) return meadowSpot;
        for (int i = 0; i < 80; i++) {
            int x = 80 + (i % 20) * 96, z = 1180 + (i / 20) * 256;
            var b = level.getBiome(new BlockPos(x, 70, z));
            if (b.is(net.minecraft.tags.BiomeTags.IS_FOREST) || b.is(net.minecraft.tags.BiomeTags.IS_JUNGLE)
                || b.is(net.minecraft.world.level.biome.Biomes.PLAINS) || b.is(net.minecraft.world.level.biome.Biomes.MEADOW)
                || b.is(net.minecraft.world.level.biome.Biomes.SWAMP)) {
                if (b.is(net.minecraft.tags.BiomeTags.SPAWNS_COLD_VARIANT_FROGS)) continue;
                meadowSpot = new BlockPos(x, 0, z);
                log("temperate stage at " + x + ", " + z);
                return meadowSpot;
            }
        }
        meadowSpot = new BlockPos(80, 0, 1180);
        return meadowSpot;
    }

    /**
     * One shot of a self-test site. Its origin is found from a marker block placed at a known local height in a known
     * column ({@code dx}, {@code dz}), so the frame does not depend on how tall the site is over its centre.
     */
    private static void wild(int site, int dx, int dz, net.minecraft.world.level.block.Block marker, int localY, String shot, double[] eye, double[] look,
                             net.minecraftforge.registries.RegistryObject<net.minecraft.world.level.block.Block> modMarker, int modLocalY) {
        scene(10, shot, mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            var m = modMarker != null ? modMarker.get() : marker;
            int ly = modMarker != null ? modLocalY : localY;
            int x = 80 + site * 90, z = 200;
            level.getChunk((x + dx) >> 4, (z + dz) >> 4);
            int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x + dx, z + dz);
            int oy = top;
            for (int y = top; y > top - 90; y--) {
                if (level.getBlockState(new BlockPos(x + dx, y, z + dz)).is(m)) {
                    oy = y - ly;
                    break;
                }
            }
            Vec3 o = new Vec3(x + 0.5, oy, z + 0.5);
            frame(mc, OW, o.add(eye[0], eye[1], eye[2]), o.add(look[0], look[1], look[2]));
        }));
        scene(130, shot + "_shot", mc -> shoot(mc, shot));
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
            int y = stage(level, x - 2, z - 3, x + 26, z + 3, ModBlocks.WARDSTONE_BRICKS.get().defaultBlockState());
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
        // the wider roster, in two rows: the wilds in front, the things of the night behind
        scene(10, "wilds", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 820;
            run(mc, "time set 1000");
            int y = stage(level, x - 3, z - 4, x + 30, z + 8, net.minecraft.world.level.block.Blocks.GRASS_BLOCK.defaultBlockState());
            for (int dx = -3; dx <= 30; dx += 3) level.setBlock(new BlockPos(x + dx, y, z + 8), ModBlocks.MOONPETAL.get().defaultBlockState(), 2);
            double cx = x + 0.5;
            for (var t : List.of(ModEntities.GLIMMERFAWN, ModEntities.DUSKHARE, ModEntities.MOSSBACK_TORTOISE, ModEntities.LUMEN_BEETLE,
                ModEntities.TIDEWADER, ModEntities.THORNBACK_BOAR, ModEntities.STONEWARDEN, ModEntities.RUNEWISP)) {
                still(level, t.get(), new Vec3(cx, y + (t == ModEntities.RUNEWISP ? 1.2 : 0), z + 0.5), 180f);
                cx += t == ModEntities.STONEWARDEN ? 4.5 : 3.5;
            }
            cx = x + 2.5;
            for (var t : List.of(ModEntities.DROWNED_CHOIRMONK, ModEntities.MIRE_HAG, ModEntities.GRAVE_CRAWLER, ModEntities.GLOAM_STALKER,
                ModEntities.SHADE_WRAITH, ModEntities.LUMENITE_MITE, ModEntities.ASHEN_REVENANT)) {
                still(level, t.get(), new Vec3(cx, y + (t == ModEntities.SHADE_WRAITH ? 0.6 : 0), z + 5.5), 180f);
                cx += 3.8;
            }
            p.teleportTo(level, x + 14, y + 3.0 - 1.62, z - 7, java.util.Set.of(), 0f, 14f, false);
        }));
        scene(130, "wilds_shot", mc -> shoot(mc, "the_wilds"));
        // the wild keepers, awake
        scene(10, "wild_keepers", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 1000;
            int y = stage(level, x - 5, z - 5, x + 26, z + 5, ModBlocks.RUNESTONE_BRICKS.get().defaultBlockState());
            double cx = x + 1.5;
            for (var t : List.of(ModEntities.ELDERHORN, ModEntities.BOG_MOTHER, ModEntities.CINDER_COLOSSUS)) {
                Mob m = t.get().create(level, EntitySpawnReason.COMMAND);
                if (m == null) continue;
                m.snapTo(cx, y, z + 0.5, 160f, 0);
                m.setNoAi(true);
                m.setYHeadRot(160f);
                m.yBodyRot = 160f;
                if (m instanceof com.oathbound.entity.boss.KeeperEntity k) k.wake(level, null);
                level.addFreshEntity(m);
                cx += 10;
            }
            p.teleportTo(level, x + 11.5, y + 3.2 - 1.62, z - 11, java.util.Set.of(), 0f, 8f, false);
        }));
        scene(140, "wild_keepers_shot", mc -> shoot(mc, "wild_keepers"));
        // the land remembers the Order: a waystone, a ruined outpost, a mossy boulder and a glimmer glade on a meadow
        scene(10, "landmarks", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            BlockPos meadow = temperate(level);
            int x = meadow.getX(), z = meadow.getZ();
            int y = stage(level, x - 6, z - 8, x + 30, z + 8, net.minecraft.world.level.block.Blocks.GRASS_BLOCK.defaultBlockState());
            com.oathbound.SelfTest.placeFeature(level, "order_ruin", new BlockPos(x + 12, y, z + 1));
            com.oathbound.SelfTest.placeFeature(level, "waystone", new BlockPos(x + 2, y, z - 2));
            com.oathbound.SelfTest.placeFeature(level, "mossy_boulder", new BlockPos(x + 24, y, z - 3));
            com.oathbound.SelfTest.placeFeature(level, "glimmer_glade", new BlockPos(x + 5, y, z + 3));
            com.oathbound.SelfTest.placeFeature(level, "glimmer_glade", new BlockPos(x + 22, y, z + 4));
            meadowY = y;
            still(level, ModEntities.LANTERNGUARD_PILGRIM.get(), new Vec3(x + 9.5, y, z - 3.5), 200f);
            p.teleportTo(level, x + 12.5, y + 4 - 1.62, z - 11, java.util.Set.of(), 0f, 16f, false);
        }));
        scene(140, "landmarks_shot", mc -> shoot(mc, "landmarks"));
        // a cave lit only by lumenite crystal
        scene(10, "crystal_cave", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 1260;
            level.getChunk(x >> 4, z >> 4);
            int g = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            BlockPos c = new BlockPos(x, g - 22, z);
            var stone = net.minecraft.world.level.block.Blocks.STONE.defaultBlockState();
            var deep = net.minecraft.world.level.block.Blocks.DEEPSLATE.defaultBlockState();
            var air = net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
            java.util.Random r = new java.util.Random(7);
            for (int dx = -10; dx <= 10; dx++)
                for (int dy = -6; dy <= 6; dy++)
                    for (int dz = -10; dz <= 10; dz++) {
                        double d = dx * dx / 90.0 + dy * dy / 26.0 + dz * dz / 90.0 + r.nextDouble() * 0.12;
                        level.setBlock(c.offset(dx, dy, dz), d < 1.0 ? air : (dy < -2 ? deep : stone), 2);
                    }
            for (int i = 0; i < 16; i++) com.oathbound.SelfTest.placeFeature(level, "lumen_clusters", c.offset(r.nextInt(13) - 6, r.nextInt(7) - 3, r.nextInt(13) - 6));
            p.teleportTo(level, x + 0.5, c.getY() - 1.62 + 0.8, z - 7.5, java.util.Set.of(), 0f, 6f, false);
        }));
        scene(140, "crystal_cave_shot", mc -> shoot(mc, "crystal_cave"));
        // fireflies over the meadow on a summer night
        scene(10, "fireflies", mc -> {
            run(mc, "time set 18000");
            onServer(mc, p -> {
                ServerLevel level = p.level().getServer().overworld();
                BlockPos meadow = temperate(level);
                p.teleportTo(level, meadow.getX() + 12.5, meadowY + 1.8 - 1.62, meadow.getZ() - 4, java.util.Set.of(), 0f, 8f, false);
            });
        });
        scene(160, "fireflies_shot", mc -> shoot(mc, "fireflies"));
        scene(5, "day_again", mc -> run(mc, "time set 1000"));
        // the places off the Path (self-test sites 5 to 11), framed from each site's own origin
        wild(5, 0, 0, null, 1, "stags_ring", new double[]{13, 9, 19}, new double[]{1, 3, -1}, ModBlocks.GLYPHED_RUNESTONE, 1);
        wild(6, 0, 0, net.minecraft.world.level.block.Blocks.VERDANT_FROGLIGHT, 9, "bog_mothers_house", new double[]{12, 10, 20}, new double[]{0, 7, 0}, null, 0);
        wild(7, 0, -4, net.minecraft.world.level.block.Blocks.GOLD_BLOCK, 7, "cinder_sanctum", new double[]{20, 14, 28}, new double[]{0, 4, -4}, null, 0);
        wild(7, 0, -4, net.minecraft.world.level.block.Blocks.GOLD_BLOCK, 7, "sanctum_hall", new double[]{0, -8.4, 3}, new double[]{0, -9.5, -12}, null, 0);
        wild(8, 0, 0, net.minecraft.world.level.block.Blocks.CAMPFIRE, 21, "last_watch", new double[]{16, 12, 20}, new double[]{0, 10, 0}, null, 0);
        wild(9, -1, -2, net.minecraft.world.level.block.Blocks.SEA_LANTERN, -1, "tideglass_grotto", new double[]{0, 3.2, 7}, new double[]{0, 2, -7}, null, 0);
        wild(10, 0, 0, net.minecraft.world.level.block.Blocks.SPRUCE_TRAPDOOR, 37, "lumenite_headframe", new double[]{10, 36, 12}, new double[]{0, 33, 0}, null, 0);
        wild(10, 0, 0, net.minecraft.world.level.block.Blocks.SPRUCE_TRAPDOOR, 37, "lumenite_delve", new double[]{-1, 2.6, 0}, new double[]{20, 1.8, 0}, null, 0);
        wild(11, 0, 0, null, 2, "shattered_observatory", new double[]{15, 17, 17}, new double[]{0, 10, 0}, ModBlocks.DUSKIRON_BLOCK, 2);
        scene(5, "dusk_again", mc -> run(mc, "time set 12600"));
        scene(10, "keepers", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 700;
            int y = stage(level, x - 4, z - 4, x + 24, z + 4, ModBlocks.GLOAMSTONE_BRICKS.get().defaultBlockState());
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
        scene(10, "spells", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x = 80, z = 760;
            int y = stage(level, x - 6, z - 7, x + 30, z + 7, ModBlocks.GLOAMSTONE_BRICKS.get().defaultBlockState());
            Vec3 b = new Vec3(x + 0.5, y, z + 0.5);
            SpellMarkEntity.sigil(level, b, 3.5f, SpellMarkEntity.Hue.DAWN, 400);
            SpellMarkEntity.sigil(level, b.add(8, 0, 0), 2.5f, SpellMarkEntity.Hue.ARCANE, 400);
            SpellMarkEntity.pillar(level, b.add(8, 0, 0), 1.2f, SpellMarkEntity.Hue.ARCANE, 400);
            SpellMarkEntity.ring(level, b.add(16, 0, 0), 6f, SpellMarkEntity.Hue.SPIRIT, 170);
            SpellMarkEntity.sigil(level, b.add(16, 0, 0), 1.5f, SpellMarkEntity.Hue.SPIRIT, 400);
            SpellMarkEntity.halo(level, b.add(24, 1.2, 0), 1.6f, SpellMarkEntity.Hue.TIDE, 400);
            SpellMarkEntity.beam(level, b.add(-3, 1.4, -5), b.add(27, 1.4, -5), 0.35f, SpellMarkEntity.Hue.GLOAM, 400);
            SpellMarkEntity.wallSigil(level, b.add(12, 3.6, 6), 2.6f, SpellMarkEntity.Hue.BLOOD, 400, 180f);
            p.teleportTo(level, x + 12, y + 6 - 1.62, z - 15, java.util.Set.of(), 0f, 22f, false);
        }));
        scene(120, "spells_shot", mc -> shoot(mc, "spellcraft"));
        scene(10, "masonry", mc -> onServer(mc, p -> {
            ServerLevel level = p.level().getServer().overworld();
            int x0 = 80, z0 = 880;
            level.getChunk(x0 >> 4, z0 >> 4);
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x0, z0) + 8;
            buildGallery(level, new BlockPos(x0, y, z0));
            p.teleportTo(level, x0 + 17.5, y + 4 - 1.62, z0 - 11.5, java.util.Set.of(), 0f, 18f, false);
        }));
        scene(140, "masonry_shot", mc -> shoot(mc, "masonry"));
        for (String biome : List.of("veilwood", "ashen_reach")) {
            scene(10, biome, mc -> onServer(mc, p -> {
                ServerLevel g = p.level().getServer().getLevel(ModWorldgen.GLOAMING);
                if (g == null) return;
                var key = net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.BIOME,
                    net.minecraft.resources.Identifier.fromNamespaceAndPath(Oathbound.MODID, biome));
                var hit = g.findClosestBiome3d(h -> h.is(key), new BlockPos(0, 64, 0), 4000, 32, 32);
                if (hit == null) return;
                BlockPos at = hit.getFirst();
                // look for solid island ground near the hit, and stand a little above it
                for (int tries = 0; tries < 24; tries++) {
                    BlockPos c = at.offset((tries % 5 - 2) * 12, 0, (tries / 5 - 2) * 12);
                    g.getChunk(c.getX() >> 4, c.getZ() >> 4);
                    int y = g.getHeight(Heightmap.Types.MOTION_BLOCKING, c.getX(), c.getZ());
                    if (y > g.getMinY() + 4) {
                        p.teleportTo(g, c.getX() + 0.5, y + 6 - 1.62, c.getZ() + 0.5, java.util.Set.of(), 30f, 20f, false);
                        return;
                    }
                }
            }));
            scene(150, biome + "_shot", mc -> shoot(mc, "gloaming_" + biome));
        }
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
        // portraits for the Chronicle's quest pages: each quarry close up, at dusk, on the Order's stone
        String[] sitterQuests = {"caldris", "veyl", "hrodgar", "veilhound", "gloamling", "lanternmoth", "forsworn"};
        List<java.util.function.Supplier<? extends EntityType<? extends Mob>>> sitters = List.of(ModEntities.SIR_CALDRIS, ModEntities.ARCHMAGE_VEYL,
            ModEntities.HRODGAR, ModEntities.VEILHOUND, ModEntities.GLOAMLING, ModEntities.LANTERNMOTH, ModEntities.FORSWORN_KNIGHT);
        for (int i = 0; i < sitters.size(); i++) {
            final int n = i;
            final String quest = sitterQuests[i];
            final var type = sitters.get(i);
            scene(10, "portrait_" + quest, mc -> onServer(mc, p -> {
                ServerLevel level = p.level().getServer().overworld();
                if (n == 0) run(mc, "time set 12600");
                int x = 80 + n * 48, z = 1000;
                int y = stage(level, x - 4, z - 6, x + 4, z + 4, ModBlocks.WARDSTONE_BRICKS.get().defaultBlockState());
                double feet = y + ("lanternmoth".equals(quest) ? 1.2 : 0);
                Mob m = still(level, type.get(), new Vec3(x + 0.5, feet, z + 0.5), 180f);
                float h = m == null ? 2f : m.getBbHeight(), w = m == null ? 1f : m.getBbWidth();
                double dist = 2.2 + Math.max(h, w) * 1.35;
                double eye = feet + h * 0.62;
                p.teleportTo(level, x + 0.5, eye - 1.62, z + 0.5 - dist, java.util.Set.of(), 0f, 4f, false);
            }));
            scene(70, "portrait_" + quest + "_shot", mc -> shoot(mc, "portrait_" + quest));
        }
        scene(10, "book_setup", mc -> {
            run(mc, "execute in minecraft:overworld run tp @s 80 120 640");
            run(mc, "gamemode creative");
            run(mc, "give @s oathbound:lantern_chronicle");
            for (String q : List.of("lantern", "wayshrine", "hymn", "oathsteel_arms", "lanternmoth")) run(mc, "oathbound stage " + q);
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
            // the report keeps [CLIENTTEST] lines, so spell the trace out there too
            for (Throwable c = t; c != null; c = c.getCause()) {
                log("  " + (c == t ? "" : "caused by ") + c);
                StackTraceElement[] st = c.getStackTrace();
                for (int i = 0; i < Math.min(12, st.length); i++) log("    at " + st[i]);
            }
        }
        countdown = cursor < SCENES.size() ? SCENES.get(cursor).delay() : 0;
    }

    /** Six bays, one per building family: a wall of its stones, its stairs, slabs and walls in front, lit by lanterns. */
    private static void buildGallery(ServerLevel level, BlockPos o) {
        java.util.List<java.util.List<net.minecraftforge.registries.RegistryObject<net.minecraft.world.level.block.Block>>> bays = java.util.List.of(
            java.util.List.of(ModBlocks.WARDSTONE_BRICKS, ModBlocks.POLISHED_WARDSTONE, ModBlocks.CHISELED_WARDSTONE, ModBlocks.WARDSTONE_BRICK_STAIRS,
                ModBlocks.WARDSTONE_BRICK_SLAB, ModBlocks.WARDSTONE_BRICK_WALL, ModBlocks.WARDSTONE_TILES),
            java.util.List.of(ModBlocks.GLOAMSTONE_BRICKS, ModBlocks.POLISHED_GLOAMSTONE, ModBlocks.CHISELED_GLOAMSTONE, ModBlocks.GLOAMSTONE_BRICK_STAIRS,
                ModBlocks.GLOAMSTONE_BRICK_SLAB, ModBlocks.GLOAMSTONE_BRICK_WALL, ModBlocks.GLOAMSTONE_TILES),
            java.util.List.of(ModBlocks.TIDESTONE_BRICKS, ModBlocks.BARNACLED_TIDESTONE_BRICKS, ModBlocks.CHISELED_TIDESTONE, ModBlocks.TIDESTONE_BRICK_STAIRS,
                ModBlocks.TIDESTONE_BRICK_SLAB, ModBlocks.TIDESTONE_BRICK_WALL, ModBlocks.TIDESTONE),
            java.util.List.of(ModBlocks.BARROWSTONE_BRICKS, ModBlocks.BARROWSTONE, ModBlocks.BONE_INLAID_BARROWSTONE, ModBlocks.BARROWSTONE_BRICK_STAIRS,
                ModBlocks.BARROWSTONE_BRICK_SLAB, ModBlocks.BARROWSTONE_BRICK_WALL, ModBlocks.BARROWSTONE),
            java.util.List.of(ModBlocks.RUNESTONE_BRICKS, ModBlocks.RUNESTONE, ModBlocks.GLYPHED_RUNESTONE, ModBlocks.RUNESTONE_BRICK_STAIRS,
                ModBlocks.RUNESTONE_BRICK_SLAB, ModBlocks.RUNESTONE_BRICK_WALL, ModBlocks.RUNESTONE),
            java.util.List.of(ModBlocks.GLOAMWOOD_PLANKS, ModBlocks.STRIPPED_GLOAMWOOD, ModBlocks.GLOAMWOOD, ModBlocks.GLOAMWOOD_STAIRS,
                ModBlocks.GLOAMWOOD_SLAB, ModBlocks.GLOAMWOOD_FENCE, ModBlocks.GLOAMWOOD_PLANKS));
        net.minecraft.world.level.block.state.BlockState air = net.minecraft.world.level.block.Blocks.AIR.defaultBlockState();
        for (int dx = -2; dx <= 37; dx++)
            for (int dz = -8; dz <= 2; dz++) {
                level.setBlock(o.offset(dx, -1, dz), (dz < -5 ? ModBlocks.GLOAM_MOSS : ModBlocks.POLISHED_WARDSTONE).get().defaultBlockState(), 2);
                for (int dy = 0; dy < 7; dy++) level.setBlock(o.offset(dx, dy, dz), air, 2);
            }
        for (int i = 0; i < bays.size(); i++) {
            var bay = bays.get(i);
            BlockPos b = o.offset(i * 6, 0, 0);
            for (int dx = 0; dx < 5; dx++)
                for (int dy = 0; dy < 4; dy++) {
                    var block = (dx == 2 && dy == 1) ? bay.get(2) : (dy == 3 || dx == 0 || dx == 4) ? bay.get(1) : bay.get(0);
                    level.setBlock(b.offset(dx, dy, 1), block.get().defaultBlockState(), 2);
                }
            for (int dx = 0; dx < 5; dx++) level.setBlock(b.offset(dx, 0, -1), bay.get(6).get().defaultBlockState(), 2);
            level.setBlock(b.offset(1, 0, 0), bay.get(3).get().defaultBlockState(), 2);
            level.setBlock(b.offset(3, 0, 0), bay.get(4).get().defaultBlockState(), 2);
            level.setBlock(b.offset(0, 0, -2), bay.get(5).get().defaultBlockState(), 3);
            level.setBlock(b.offset(4, 0, -2), bay.get(5).get().defaultBlockState(), 3);
            level.setBlock(b.offset(2, 4, 1), (i % 2 == 0 ? ModBlocks.OATHSTEEL_LANTERN : ModBlocks.GLOAM_LANTERN).get().defaultBlockState(), 2);
        }
        // the woodwork bay's door and trapdoor, and the lamps, glass and bars between the bays
        level.setBlock(o.offset(32, 0, 1), ModBlocks.GLOAMWOOD_DOOR.get().defaultBlockState(), 2);
        level.setBlock(o.offset(32, 1, 1), ModBlocks.GLOAMWOOD_DOOR.get().defaultBlockState()
            .setValue(net.minecraft.world.level.block.DoorBlock.HALF, net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER), 2);
        level.setBlock(o.offset(32, 3, 0), ModBlocks.GLOAMWOOD_TRAPDOOR.get().defaultBlockState()
            .setValue(net.minecraft.world.level.block.TrapDoorBlock.HALF, net.minecraft.world.level.block.state.properties.Half.TOP), 2);
        for (int i = 0; i < 5; i++) {
            BlockPos gap = o.offset(i * 6 + 5, 0, 1);
            var fill = switch (i) {
                case 0 -> ModBlocks.LUMENITE_LAMP;
                case 1 -> ModBlocks.GLOAMGLASS;
                case 2 -> ModBlocks.LANTERNGLASS;
                case 3 -> ModBlocks.OATHSTEEL_BARS;
                default -> ModBlocks.GLOAMWOOD_LEAVES;
            };
            for (int dy = 0; dy < 3; dy++) {
                var st = fill.get().defaultBlockState();
                if (st.hasProperty(net.minecraft.world.level.block.RedstoneLampBlock.LIT)) st = st.setValue(net.minecraft.world.level.block.RedstoneLampBlock.LIT, dy == 1);
                if (st.hasProperty(net.minecraft.world.level.block.LeavesBlock.PERSISTENT)) st = st.setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT, true);
                level.setBlock(gap.above(dy), st, 3);
            }
        }
        // a strip of wildflowers, pots and moss carpet along the front
        var flowers = java.util.List.of(ModBlocks.DUSK_LILY, ModBlocks.EMBERROOT, ModBlocks.MOONPETAL, ModBlocks.GLOAM_FERN, ModBlocks.VEILBLOOM,
            ModBlocks.GLOAMWOOD_SAPLING);
        var pots = java.util.List.of(ModBlocks.POTTED_DUSK_LILY, ModBlocks.POTTED_EMBERROOT, ModBlocks.POTTED_MOONPETAL, ModBlocks.POTTED_GLOAM_FERN,
            ModBlocks.POTTED_VEILBLOOM, ModBlocks.POTTED_GLOAMWOOD_SAPLING);
        for (int dx = 0; dx < 36; dx++) {
            BlockPos f = o.offset(dx, 0, -6);
            if (dx % 6 == 5) level.setBlock(f, pots.get((dx / 6) % pots.size()).get().defaultBlockState(), 2);
            else if (dx % 3 == 0) level.setBlock(f, ModBlocks.GLIMMER_MOSS.get().defaultBlockState(), 2);
            else level.setBlock(f, flowers.get((dx / 6) % flowers.size()).get().defaultBlockState(), 2);
        }
    }
}
