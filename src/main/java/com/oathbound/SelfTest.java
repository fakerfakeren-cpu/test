package com.oathbound;

import com.oathbound.block.*;
import com.oathbound.entity.boss.*;
import com.oathbound.entity.mob.ForswornKnightEntity;
import com.oathbound.event.GateRite;
import com.oathbound.event.GloamingTravel;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.*;
import com.oathbound.util.Puzzles;
import com.oathbound.world.SketchPlacer;
import com.oathbound.world.Sketches;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Headless integration test ({@code -Doathbound.selftest=true}). On a dedicated server it raises every
 * structure, solves every puzzle, opens the Sundered Gate, builds the Hollow Throne, spawns every creature
 * and plays out each keeper's death and the whole Morvane fight, then prints {@code [SELFTEST] RESULT}.
 */
public final class SelfTest {
    private static boolean active;
    private static int tick;
    private static int checks;
    private static final List<String> failures = new ArrayList<>();
    private static final Map<Integer, Consumer<MinecraftServer>> SCRIPT = new LinkedHashMap<>();
    private static final Map<Sketches.Type, BlockPos> built = new LinkedHashMap<>();
    private static final List<Entity> spawned = new ArrayList<>();
    private static LivingEntity dummy;
    private static MorvaneEntity king;
    private static BlockPos arena;

    private SelfTest() {}

    private static void log(String msg) {
        Oathbound.LOGGER.info("[SELFTEST] {}", msg);
    }

    private static void check(String name, boolean ok, Object detail) {
        checks++;
        String d = String.valueOf(detail);
        if (ok) log("PASS " + name + (d.isEmpty() ? "" : " (" + d + ")"));
        else {
            failures.add(name);
            log("FAIL " + name + (d.isEmpty() ? "" : " (" + d + ")"));
        }
    }

    private static void at(int t, Consumer<MinecraftServer> step) {
        SCRIPT.put(t, step);
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (!Boolean.getBoolean("oathbound.selftest")) return;
        active = true;
        log("Oathbound self-test on " + event.getServer().getServerVersion());
        script();
        Thread watchdog = new Thread(() -> {
            try {
                Thread.sleep(7 * 60 * 1000L);
            } catch (InterruptedException e) {
                return;
            }
            if (active) {
                log("WATCHDOG: stalled at tick " + tick);
                for (var e : Thread.getAllStackTraces().entrySet()) {
                    if (!e.getKey().getName().contains("Server")) continue;
                    for (StackTraceElement st : e.getValue()) log("|  at " + st);
                }
                Oathbound.LOGGER.error("[SELFTEST] RESULT: FAIL (timeout)");
                Runtime.getRuntime().halt(3);
            }
        }, "oathbound-selftest-watchdog");
        watchdog.setDaemon(true);
        watchdog.start();
    }

    public static void onServerTick(TickEvent.ServerTickEvent.Post event) {
        if (!active) return;
        tick++;
        Consumer<MinecraftServer> step = SCRIPT.get(tick);
        if (step == null) return;
        try {
            step.accept(event.server());
        } catch (Throwable t) {
            failures.add("tick " + tick + " threw " + t);
            Oathbound.LOGGER.error("[SELFTEST] step at tick {} threw", tick, t);
        }
    }

    private static int ground(ServerLevel level, int x, int z) {
        level.getChunk(x >> 4, z >> 4);
        return level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
    }

    private static <T extends Entity> T spawn(ServerLevel level, EntityType<T> type, BlockPos pos) {
        T e = type.create(level, EntitySpawnReason.COMMAND);
        if (e == null) throw new IllegalStateException("could not create " + type);
        e.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, 0, 0);
        if (e instanceof Mob m) m.setPersistenceRequired();
        level.addFreshEntity(e);
        spawned.add(e);
        return e;
    }

    private static boolean lootExists(MinecraftServer server, String path) {
        var key = ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Oathbound.MODID, path));
        return server.reloadableRegistries().getLootTable(key) != LootTable.EMPTY;
    }

    private static List<ItemEntity> drops(ServerLevel level, BlockPos near) {
        return level.getEntitiesOfClass(ItemEntity.class, new AABB(near).inflate(24, 48, 24));
    }

    private static void script() {
        at(1, s -> {
            ServerLevel level = s.overworld();
            check("items_registered", ModItems.ITEMS.getEntries().size() >= 90, ModItems.ITEMS.getEntries().size());
            check("blocks_registered", ModBlocks.BLOCKS.getEntries().size() >= 34, ModBlocks.BLOCKS.getEntries().size());
            check("entities_registered", ModEntities.ENTITIES.getEntries().size() >= 18, ModEntities.ENTITIES.getEntries().size());
            check("sounds_registered", ModSounds.SOUNDS.getEntries().size() == ModSounds.NAMES.size(), ModSounds.NAMES.size());
            check("gloaming_dimension_loaded", s.getLevel(ModWorldgen.GLOAMING) != null, "");
            int missing = 0;
            for (String q : QuestLog.QUESTS.keySet()) {
                if (s.getAdvancements().get(QuestLog.questAdvancement(q)) == null) {
                    missing++;
                    log("missing quest advancement " + q);
                }
                if (s.getAdvancements().get(QuestLog.claimedAdvancement(q)) == null) {
                    missing++;
                    log("missing tithe marker " + q);
                }
            }
            for (QuestLog.Boon b : QuestLog.BOONS) if (s.getAdvancements().get(QuestLog.boonAdvancement(b.id())) == null) missing++;
            check("quest_advancements_loaded", missing == 0, "missing=" + missing);
            String[] loot = {"chests/wayshrine_cache", "chests/chapel_reliquary", "chests/chapel_secret", "chests/chapel_nave", "chests/spire_library",
                "chests/spire_alchemy", "chests/spire_sanctum", "chests/spire_secret", "chests/barrow_tomb", "chests/barrow_hoard", "chests/barrow_secret",
                "chests/citadel_armory", "chests/citadel_barracks", "chests/citadel_secret", "entities/sir_caldris", "entities/archmage_veyl",
                "entities/hrodgar", "entities/morvane", "entities/gloamling", "entities/forsworn_knight", "blocks/lumenite_ore"};
            int ok = 0;
            for (String l : loot) {
                if (lootExists(s, l)) ok++;
                else log("missing loot table " + l);
            }
            check("loot_tables_loaded", ok == loot.length, ok + "/" + loot.length);
            // puzzle logic
            BlockPos probe = new BlockPos(123, 64, -456);
            int[] hymn = HymnStoneBlock.hymn(probe);
            boolean noRepeat = true;
            for (int i = 1; i < hymn.length; i++) noRepeat &= hymn[i] != hymn[i - 1];
            check("hymn_is_fair", hymn.length == 5 && noRepeat, java.util.Arrays.toString(hymn));
            int[] ans = CipherLecternBlock.answer(probe);
            check("cipher_answers_distinct", java.util.Arrays.stream(ans).distinct().count() == 4, java.util.Arrays.toString(ans));
        });
        at(5, s -> {
            ServerLevel level = s.overworld();
            BlockPos spawn = BlockPos.ZERO;
            int i = 0;
            for (Sketches.Type t : Sketches.Type.values()) {
                if (t == Sketches.Type.THRONE) continue;
                int x = spawn.getX() + 80 + i * 90, z = spawn.getZ() + 200;
                BlockPos at = new BlockPos(x, ground(level, x, z), z);
                SketchPlacer.placeNow(level, Sketches.draw(t, 1234L + i), at);
                built.put(t, at);
                i++;
            }
            BlockPos shrine = built.get(Sketches.Type.WAYSHRINE);
            check("wayshrine_brazier", level.getBlockState(shrine.above()).is(ModBlocks.WAYSHRINE_BRAZIER.get()), shrine);
            BlockPos chapel = built.get(Sketches.Type.DROWNED_CHAPEL);
            check("chapel_bells", Puzzles.find(level, chapel, 12, ModBlocks.CHAPEL_BELL.get()).size() == 4, "");
            check("chapel_hymn_stone", level.getBlockState(chapel.offset(0, 2, -9)).is(ModBlocks.HYMN_STONE.get()), "");
            BlockPos spire = built.get(Sketches.Type.ARCANIST_SPIRE);
            check("spire_dials", Puzzles.find(level, spire.above(25), 8, ModBlocks.RUNE_DIAL.get()).size() == 4, "");
            check("spire_ward", !Puzzles.find(level, spire.above(28), 6, ModBlocks.ARCANE_WARD.get()).isEmpty(), "");
            BlockPos barrow = built.get(Sketches.Type.BARROW_OF_KINGS);
            check("barrow_tombs", Puzzles.find(level, barrow.offset(0, -10, -9), 6, ModBlocks.SARCOPHAGUS.get()).size() == 3, "");
            BlockPos citadel = built.get(Sketches.Type.SUNDERED_CITADEL);
            check("citadel_keystone", level.getBlockState(citadel.offset(0, 0, -10)).is(ModBlocks.SUNDERED_KEYSTONE.get()), "");
        });
        at(10, s -> {
            ServerLevel level = s.overworld();
            BlockPos chapel = built.get(Sketches.Type.DROWNED_CHAPEL);
            HymnStoneBlock.solve(level, chapel.offset(0, 2, -9), null);
            BlockPos spire = built.get(Sketches.Type.ARCANIST_SPIRE);
            BlockPos lectern = spire.offset(0, 25, -1);
            int[] ans = CipherLecternBlock.answer(lectern);
            for (BlockPos d : Puzzles.find(level, lectern, 12, ModBlocks.RUNE_DIAL.get())) {
                var st = level.getBlockState(d);
                level.setBlock(d, st.setValue(RuneDialBlock.GLYPH, ans[st.getValue(RuneDialBlock.NUMBER)]), 3);
            }
            check("cipher_accepts_answer", CipherLecternBlock.check(level, lectern, null), "");
            BlockPos barrow = built.get(Sketches.Type.BARROW_OF_KINGS);
            List<BlockPos> tombs = SarcophagusBlock.tombs(level, barrow.offset(0, -10, -9));
            int[] roles = SarcophagusBlock.roles(level, barrow.offset(0, -10, -9));
            // exactly one reading of the epitaphs is consistent: the honest king's
            int consistent = 0;
            for (int h = 0; h < 3; h++) {
                boolean s1 = roles[1] != h;          // honest says: accused lies
                boolean s2 = roles[2] == h;          // accused says: boaster is truthful
                boolean s3 = roles[2] == h;          // boaster says: I am truthful
                boolean[] truth = new boolean[3];
                truth[roles[0]] = s1;
                truth[roles[1]] = s2;
                truth[roles[2]] = s3;
                int trues = 0;
                for (boolean b : truth) if (b) trues++;
                if (trues == 1 && truth[h]) consistent++;
            }
            check("epitaph_puzzle_unique", consistent == 1, "consistent readings=" + consistent);
            for (BlockPos t : tombs) {
                if (level.getBlockState(t).getValue(SarcophagusBlock.KING) == roles[0]) SarcophagusBlock.open(level, t, null);
            }
        });
        at(80, s -> {
            ServerLevel level = s.overworld();
            BlockPos chapel = built.get(Sketches.Type.DROWNED_CHAPEL);
            check("hymn_lifts_grate", Puzzles.find(level, chapel, 20, ModBlocks.SEALED_GRATE.get()).isEmpty(), "");
            BlockPos spire = built.get(Sketches.Type.ARCANIST_SPIRE);
            check("cipher_dissolves_ward", Puzzles.find(level, spire.above(28), 8, ModBlocks.ARCANE_WARD.get()).isEmpty(), "");
            BlockPos barrow = built.get(Sketches.Type.BARROW_OF_KINGS);
            check("honest_king_opens_barrow", Puzzles.find(level, barrow.offset(0, -10, -12), 8, ModBlocks.BARROW_SEAL.get()).isEmpty(), "");
            BlockPos keystone = built.get(Sketches.Type.SUNDERED_CITADEL).offset(0, 0, -10);
            int veil = GateRite.openNow(level, keystone);
            check("gate_opens", veil == 35, "veil=" + veil);
        });
        at(90, s -> {
            ServerLevel level = s.overworld();
            int x = 80, z = 420;
            BlockPos base = new BlockPos(x, ground(level, x, z) + 1, z);
            for (var e : List.of(ModEntities.LANTERNMOTH, ModEntities.GLOAMLING, ModEntities.FORSWORN_KNIGHT, ModEntities.BARROW_WIGHT,
                ModEntities.ANIMATED_TOME, ModEntities.VEILHOUND, ModEntities.SPECTRAL_HOUSECARL)) {
                spawn(level, e.get(), base);
                base = base.offset(6, 0, 0);
                base = base.atY(ground(level, base.getX(), base.getZ()) + 1);
            }
            ForswornKnightEntity k = spawn(level, ModEntities.FORSWORN_KNIGHT.get(), base.offset(10, 0, 0));
            k.setNoAi(true);
            k.hurtServer(level, level.damageSources().generic(), 500f);
            check("forsworn_collapses_not_dies", k.isAlive() && k.isFallen(), "alive=" + k.isAlive() + " fallen=" + k.isFallen());
            k.hurtServer(level, level.damageSources().onFire(), 5f);
            check("fire_lays_forsworn_to_rest", k.isDeadOrDying(), "hp=" + k.getHealth());
        });
        // keepers: each must drop its seal
        int t0 = 120;
        for (var keeper : List.of("caldris", "veyl", "hrodgar")) {
            final int base = t0;
            at(base, s -> {
                ServerLevel level = s.overworld();
                int x = 400 + base, z = 520;
                BlockPos at = new BlockPos(x, ground(level, x, z) + 1, z);
                EntityType<? extends KeeperEntity> type = switch (keeper) {
                    case "caldris" -> ModEntities.SIR_CALDRIS.get();
                    case "veyl" -> ModEntities.ARCHMAGE_VEYL.get();
                    default -> ModEntities.HRODGAR.get();
                };
                KeeperEntity k = spawn(level, type, at);
                k.wake(level, null);
                check(keeper + "_awake", !k.isSleeping(), "");
            });
            at(base + 60, s -> {
                ServerLevel level = s.overworld();
                for (Entity e : spawned) {
                    if (e instanceof KeeperEntity k && k.isAlive()) {
                        k.setHealth(1f);
                        k.invulnerableTime = 0;
                        k.hurtServer(level, level.damageSources().generic(), 10f);
                    }
                }
            });
            at(base + 90, s -> {
                ServerLevel level = s.overworld();
                int x = 400 + base, z = 520;
                BlockPos at = new BlockPos(x, ground(level, x, z) + 1, z);
                var seal = switch (keeper) {
                    case "caldris" -> ModItems.SEAL_OF_VALOR.get();
                    case "veyl" -> ModItems.SEAL_OF_WISDOM.get();
                    default -> ModItems.SEAL_OF_SACRIFICE.get();
                };
                boolean dropped = drops(level, at).stream().anyMatch(i -> i.getItem().is(seal));
                check(keeper + "_drops_seal", dropped, "drops=" + drops(level, at).size());
            });
            t0 += 100;
        }
        // the Gloaming and the Hollow King
        at(450, s -> {
            ServerLevel g = s.getLevel(ModWorldgen.GLOAMING);
            if (g == null) return;
            GloamingTravel.ensureThrone(g);
            arena = GloamingTravel.THRONE;
            check("throne_built", g.getBlockState(arena.below()).is(ModBlocks.CHISELED_WARDSTONE.get()), "");
            check("ward_lanterns", Puzzles.find(g, arena, 13, ModBlocks.WARD_LANTERN.get()).size() == 4, "");
            check("return_veil", g.getBlockState(arena.offset(0, 2, 51)).is(ModBlocks.GLOAM_VEIL.get()), "");
            List<? extends MorvaneEntity> kings = g.getEntities(ModEntities.MORVANE.get(), e -> true);
            check("morvane_waits", kings.size() == 1 && kings.get(0).isSleeping(), "count=" + kings.size());
            if (!kings.isEmpty()) {
                king = kings.get(0);
                dummy = spawn(g, net.minecraft.world.entity.EntityTypes.IRON_GOLEM, arena.offset(4, 1, -4));
                ((Mob) dummy).setNoAi(true);
                king.wake(g, null);
                king.setTarget(dummy);
            }
        });
        at(560, s -> {
            if (king == null) return;
            check("morvane_risen", !king.isSleeping() && king.move() != MorvaneEntity.RISING, "move=" + king.move());
            ServerLevel g = s.getLevel(ModWorldgen.GLOAMING);
            check("arena_sealed", g.getBlockState(arena.offset(0, 2, 17)).is(ModBlocks.ARCANE_WARD.get()), "");
            king.setHealth(king.getMaxHealth() * 0.5f);
            king.setTarget(dummy);
        });
        at(700, s -> {
            if (king == null) return;
            check("morvane_phase2", king.phase() == 2, "phase=" + king.phase());
            king.setHealth(king.getMaxHealth() * 0.2f);
            if (!dummy.isAlive()) dummy = spawn(s.getLevel(ModWorldgen.GLOAMING), net.minecraft.world.entity.EntityTypes.IRON_GOLEM, arena.offset(4, 1, -4));
            king.setTarget(dummy);
        });
        at(820, s -> {
            if (king == null) return;
            ServerLevel g = s.getLevel(ModWorldgen.GLOAMING);
            check("morvane_hollow", king.phase() == 3 && king.isHollow(), "phase=" + king.phase() + " hollow=" + king.isHollow());
            float before = king.getHealth();
            king.hurtServer(g, g.damageSources().generic(), 20f);
            check("hollow_is_untouchable", king.getHealth() == before, "");
            for (BlockPos l : Puzzles.find(g, arena, 13, ModBlocks.WARD_LANTERN.get())) {
                WardLanternBlock.relight(g, l);
                king.onLanternLit(g, l, null);
            }
            check("lanterns_unveil_morvane", !king.isHollow() && king.move() == MorvaneEntity.UNVEILED, "move=" + king.move());
        });
        at(840, s -> {
            if (king == null) return;
            ServerLevel g = s.getLevel(ModWorldgen.GLOAMING);
            king.invulnerableTime = 0;
            king.setHealth(1f);
            king.hurtServer(g, g.damageSources().generic(), 30f);
            check("morvane_dies", king.isDeadOrDying(), "hp=" + king.getHealth());
        });
        at(980, s -> {
            if (king == null) return;
            ServerLevel g = s.getLevel(ModWorldgen.GLOAMING);
            check("morvane_removed", king.isRemoved(), "");
            boolean crown = drops(g, king.blockPosition()).stream().anyMatch(i -> i.getItem().is(ModItems.HOLLOW_CROWN.get()));
            boolean blade = drops(g, king.blockPosition()).stream().anyMatch(i -> i.getItem().is(ModItems.DAWNBREAKER.get()));
            check("morvane_rewards", crown && blade, "crown=" + crown + " dawnbreaker=" + blade);
            check("arena_unsealed", !g.getBlockState(arena.offset(0, 2, 17)).is(ModBlocks.ARCANE_WARD.get()), "");
        });
        at(1000, s -> {
            int alive = 0;
            for (Entity e : spawned) if (e.isAlive()) alive++;
            log("creatures alive at end: " + alive + "/" + spawned.size());
            log(checks + " checks, " + failures.size() + " failures");
            if (failures.isEmpty()) log("RESULT: PASS");
            else Oathbound.LOGGER.error("[SELFTEST] RESULT: FAIL {}", failures);
            active = false;
            s.halt(false);
        });
    }
}
