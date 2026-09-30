package com.oathbound;

import com.oathbound.block.*;
import com.oathbound.entity.boss.*;
import com.oathbound.entity.mob.*;
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
        SCRIPT.merge(t, step, Consumer::andThen);
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

    /**
     * A dedicated test server has no players, so nothing would keep the test sites loaded or their creatures
     * ticking: force-load every chunk the script touches, as a player standing there would.
     */
    private static void keepLoaded(ServerLevel level, BlockPos centre, int radius) {
        int cx = centre.getX() >> 4, cz = centre.getZ() >> 4, r = (radius + 15) >> 4;
        for (int x = cx - r; x <= cx + r; x++)
            for (int z = cz - r; z <= cz + r; z++) level.setChunkForced(x, z, true);
    }

    private static int ground(ServerLevel level, int x, int z) {
        keepLoaded(level, new BlockPos(x, 0, z), 0);
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

    /** Every item has an item definition and a name, every block a blockstate and a name. */
    private static boolean assetsComplete() {
        com.google.gson.JsonObject lang;
        try (var in = SelfTest.class.getResourceAsStream("/assets/oathbound/lang/en_us.json")) {
            lang = com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (Exception e) {
            log("cannot read en_us.json: " + e);
            return false;
        }
        int missing = 0;
        for (var e : ModItems.ITEMS.getEntries()) {
            String n = e.getId().getPath();
            if (SelfTest.class.getResource("/assets/oathbound/items/" + n + ".json") == null) {
                missing++;
                log("no item definition for " + n);
            }
            if (!lang.has("item.oathbound." + n) && !lang.has("block.oathbound." + n)) {
                missing++;
                log("no name for item " + n);
            }
        }
        for (var e : ModBlocks.BLOCKS.getEntries()) {
            String n = e.getId().getPath();
            if (SelfTest.class.getResource("/assets/oathbound/blockstates/" + n + ".json") == null) {
                missing++;
                log("no blockstate for " + n);
            }
            if (!lang.has("block.oathbound." + n)) {
                missing++;
                log("no name for block " + n);
            }
        }
        for (var e : ModEntities.ENTITIES.getEntries()) {
            if (!lang.has("entity.oathbound." + e.getId().getPath())) {
                missing++;
                log("no name for entity " + e.getId().getPath());
            }
        }
        return missing == 0;
    }

    private static boolean lootExists(MinecraftServer server, String path) {
        var key = ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Oathbound.MODID, path));
        return server.reloadableRegistries().getLootTable(key) != LootTable.EMPTY;
    }

    /**
     * Worldgen only places the off-Path sites where the ground suits them; the test world puts them wherever the row
     * falls (jungle, ocean). Cut each one a clearing of the ground it would have chosen, wide enough for the showcase
     * camera to see it.
     */
    private static void clearing(ServerLevel level, BlockPos c, Sketches.Type t) {
        var air = Blocks.AIR.defaultBlockState();
        boolean shore = t == Sketches.Type.BOG_HUT || t == Sketches.Type.TIDEGLASS_GROTTO;
        var top = switch (t) {
            case CINDER_SANCTUM -> Blocks.SAND.defaultBlockState();
            case TIDEGLASS_GROTTO -> Blocks.SAND.defaultBlockState();
            case BOG_HUT -> Blocks.MUD.defaultBlockState();
            case SHATTERED_OBSERVATORY -> ModBlocks.GLOAM_MOSS.get().defaultBlockState();
            default -> Blocks.GRASS_BLOCK.defaultBlockState();
        };
        var under = t == Sketches.Type.CINDER_SANCTUM || t == Sketches.Type.TIDEGLASS_GROTTO ? Blocks.SANDSTONE.defaultBlockState()
            : t == Sketches.Type.SHATTERED_OBSERVATORY ? ModBlocks.GLOAMSTONE.get().defaultBlockState() : Blocks.DIRT.defaultBlockState();
        int r = 30;
        for (int dx = -r; dx <= r; dx++)
            for (int dz = -r; dz <= r; dz++) {
                if (dx * dx + dz * dz > r * r) continue;
                BlockPos col = c.offset(dx, 0, dz);
                for (int dy = 1; dy <= 32; dy++) level.setBlock(col.above(dy), air, 2 | 16);
                // the shore sites stand at the waterline: open water beyond their footprint
                boolean wet = shore && (t == Sketches.Type.BOG_HUT ? dx * dx + dz * dz > 49 : dz > 7);
                level.setBlock(col, wet ? Blocks.WATER.defaultBlockState() : top, 2 | 16);
                for (int dy = 1; dy <= 4; dy++) level.setBlock(col.below(dy), wet && dy == 1 ? top : under, 2 | 16);
            }
    }

    /** Places one of our configured features, as world generation would. */
    public static boolean placeFeature(ServerLevel level, String id, BlockPos at) {
        var key = ResourceKey.create(Registries.CONFIGURED_FEATURE, Identifier.fromNamespaceAndPath(Oathbound.MODID, id));
        var holder = level.registryAccess().lookupOrThrow(Registries.CONFIGURED_FEATURE).get(key);
        return holder.isPresent() && holder.get().value().place(level, level.getChunkSource().getGenerator(), level.getRandom(), at);
    }

    /** The creature a built site placed as its resident, if it is still there. */
    private static <T extends Entity> T resident(ServerLevel level, Sketches.Type site, Class<T> cls, int radius) {
        BlockPos at = built.get(site);
        if (at == null) return null;
        List<T> found = level.getEntitiesOfClass(cls, new AABB(at).inflate(radius, 24, radius), Entity::isAlive);
        return found.isEmpty() ? null : found.get(0);
    }

    private static List<ItemEntity> drops(ServerLevel level, BlockPos near) {
        return level.getEntitiesOfClass(ItemEntity.class, new AABB(near).inflate(24, 48, 24));
    }

    private static void script() {
        at(1, s -> {
            ServerLevel level = s.overworld();
            check("items_registered", ModItems.ITEMS.getEntries().size() >= 290, ModItems.ITEMS.getEntries().size());
            check("blocks_registered", ModBlocks.BLOCKS.getEntries().size() >= 112, ModBlocks.BLOCKS.getEntries().size());
            check("assets_complete", assetsComplete(), "");
            check("entities_registered", ModEntities.ENTITIES.getEntries().size() >= 39, ModEntities.ENTITIES.getEntries().size());
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
                "entities/hrodgar", "entities/morvane", "entities/gloamling", "entities/forsworn_knight", "blocks/lumenite_ore",
                "entities/glimmerfawn", "entities/duskhare", "entities/mossback_tortoise", "entities/lumen_beetle", "entities/tidewader",
                "entities/thornback_boar", "entities/stonewarden", "entities/runewisp", "entities/drowned_choirmonk", "entities/mire_hag",
                "entities/grave_crawler", "entities/gloam_stalker", "entities/shade_wraith", "entities/lumenite_mite", "entities/ashen_revenant",
                "blocks/duskiron_ore", "blocks/gloamwood_leaves", "blocks/gloamwood_door", "chests/citadel_barracks",
                "entities/elderhorn", "entities/bog_mother", "entities/cinder_colossus", "chests/grove_offering", "chests/bog_hut_larder",
                "chests/cinder_sanctum_vault", "chests/cinder_sanctum_offerings", "chests/watchtower_armory", "chests/watchtower_lookout",
                "chests/tideglass_hoard", "chests/grotto_wreck", "chests/mine_cache", "chests/mine_foreman", "chests/observatory_charts"};
            int ok = 0;
            for (String l : loot) {
                if (lootExists(s, l)) ok++;
                else log("missing loot table " + l);
            }
            check("loot_tables_loaded", ok == loot.length, ok + "/" + loot.length);
            var structures = s.registryAccess().lookupOrThrow(Registries.STRUCTURE);
            int sites = 0;
            for (String id : List.of("grove_shrine", "bog_hut", "cinder_sanctum", "watchtower", "tideglass_grotto", "lumenite_mine", "shattered_observatory")) {
                if (structures.get(ResourceKey.create(Registries.STRUCTURE, Identifier.fromNamespaceAndPath(Oathbound.MODID, id))).isPresent()) sites++;
                else log("missing structure " + id);
            }
            check("wild_structures_registered", sites == 7, sites + "/7");
            // worldgen places things only where these biome tags say: an empty or missing tag means it never appears
            var biomes = s.registryAccess().lookupOrThrow(Registries.BIOME);
            int tagged = 0;
            List<String> biomeTags = List.of("has_structure/grove_shrine", "has_structure/cinder_sanctum", "has_structure/shattered_observatory",
                "has_creature/glimmerfawn", "has_creature/ashen_revenant", "has_flower/moonpetal", "has_landmark/waystone", "has_landmark/lumen_clusters");
            for (String t : biomeTags) {
                var key = net.minecraft.tags.TagKey.create(Registries.BIOME, Identifier.fromNamespaceAndPath(Oathbound.MODID, t));
                var set = biomes.get(key);
                if (set.isPresent() && set.get().size() > 0) tagged++;
                else log("empty biome tag " + t);
            }
            check("worldgen_biome_tags", tagged == biomeTags.size(), tagged + "/" + biomeTags.size());
            var enchantments = s.registryAccess().lookupOrThrow(Registries.ENCHANTMENT);
            int ench = 0;
            for (String e : List.of("gloambane", "dawnfire", "warding", "wayfarer")) {
                if (enchantments.get(ResourceKey.create(Registries.ENCHANTMENT, Identifier.fromNamespaceAndPath(Oathbound.MODID, e))).isPresent()) ench++;
                else log("missing enchantment " + e);
            }
            check("enchantments_loaded", ench == 4, ench + "/4");
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
                keepLoaded(level, new BlockPos(x, 0, z), 40);
                int g = ground(level, x, z);
                if (t.ordinal() > Sketches.Type.THRONE.ordinal()) clearing(level, new BlockPos(x, g, z), t);
                BlockPos at = new BlockPos(x, g - (t == Sketches.Type.LUMENITE_MINE ? 30 : 0), z);
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
        at(30, s -> {
            ServerLevel level = s.overworld();
            check("grove_king_sleeps", resident(level, Sketches.Type.GROVE_SHRINE, ElderhornEntity.class, 6) instanceof ElderhornEntity e && e.isSleeping(), "");
            check("bog_mother_at_home", resident(level, Sketches.Type.BOG_HUT, BogMotherEntity.class, 12) != null, "");
            check("colossus_in_sanctum", resident(level, Sketches.Type.CINDER_SANCTUM, CinderColossusEntity.class, 20) != null, "");
            check("watchtower_warden", resident(level, Sketches.Type.WATCHTOWER, StonewardenEntity.class, 12) != null, "");
            BlockPos grotto = built.get(Sketches.Type.TIDEGLASS_GROTTO);
            check("grotto_shrine", level.getBlockState(grotto.offset(4, 1, -4)).is(Blocks.SPAWNER)
                && level.getBlockState(grotto.offset(0, 1, -7)).is(ModBlocks.CHISELED_TIDESTONE.get()), "");
            BlockPos mine = built.get(Sketches.Type.LUMENITE_MINE);
            check("mine_shaft_and_vein", level.getBlockState(mine.offset(-1, 15, -1)).is(Blocks.LADDER)
                && level.getBlockState(mine.offset(0, 1, -20)).is(Blocks.SPAWNER), "");
            BlockPos obs = built.get(Sketches.Type.SHATTERED_OBSERVATORY);
            check("observatory_telescope", level.getBlockState(obs.offset(0, 2, 0)).is(ModBlocks.DUSKIRON_BLOCK.get())
                && level.getBlockState(obs.offset(4, 7, 2)).is(Blocks.SPAWNER), "");
        });
        // the land remembers the Order: every landmark feature must place on prepared ground
        at(40, s -> {
            ServerLevel level = s.overworld();
            int x = 80, z = 1100;
            keepLoaded(level, new BlockPos(x + 30, 0, z), 48);
            int g = ground(level, x, z);
            for (int dx = -4; dx <= 64; dx++)
                for (int dz = -8; dz <= 8; dz++) {
                    level.setBlock(new BlockPos(x + dx, g, z + dz), Blocks.GRASS_BLOCK.defaultBlockState(), 2 | 16);
                    for (int dy = 1; dy <= 20; dy++) level.setBlock(new BlockPos(x + dx, g + dy, z + dz), Blocks.AIR.defaultBlockState(), 2 | 16);
                    for (int dy = 1; dy <= 3; dy++) level.setBlock(new BlockPos(x + dx, g - dy, z + dz), Blocks.DIRT.defaultBlockState(), 2 | 16);
                }
            int ok = 0;
            String[] ids = {"waystone", "order_ruin", "glimmer_glade", "mossy_boulder"};
            for (int i = 0; i < ids.length; i++) {
                if (placeFeature(level, ids[i], new BlockPos(x + i * 16, g + 1, z))) ok++;
                else log("landmark did not place: " + ids[i]);
            }
            check("landmarks_place", ok == ids.length, ok + "/" + ids.length);
            // a hollow of stone deep enough to be a cave, for the crystals
            BlockPos cave = new BlockPos(x + 56, g - 14, z);
            for (int dx = -5; dx <= 5; dx++)
                for (int dy = -5; dy <= 5; dy++)
                    for (int dz = -5; dz <= 5; dz++) {
                        boolean shell = Math.abs(dx) == 5 || Math.abs(dy) == 5 || Math.abs(dz) == 5;
                        level.setBlock(cave.offset(dx, dy, dz), shell ? Blocks.STONE.defaultBlockState() : Blocks.AIR.defaultBlockState(), 2 | 16);
                    }
            for (int i = 0; i < 6; i++) placeFeature(level, "lumen_clusters", cave);
            int clusters = Puzzles.find(level, cave, 6, ModBlocks.LUMENITE_CLUSTER.get()).size();
            check("lumen_clusters_grow", clusters > 0, "clusters=" + clusters);
        });
        // the wild keepers: each must wake, fall and leave its relic
        int w0 = 460;
        for (var wild : List.of(Sketches.Type.GROVE_SHRINE, Sketches.Type.BOG_HUT, Sketches.Type.CINDER_SANCTUM)) {
            final int base = w0;
            Class<? extends KeeperEntity> cls = switch (wild) {
                case GROVE_SHRINE -> ElderhornEntity.class;
                case BOG_HUT -> BogMotherEntity.class;
                default -> CinderColossusEntity.class;
            };
            var relic = switch (wild) {
                case GROVE_SHRINE -> ModItems.GROVE_KINGS_CROWN;
                case BOG_HUT -> ModItems.BOG_MOTHERS_LANTERN;
                default -> ModItems.CINDER_HEART;
            };
            String name = wild.id();
            at(base, s -> {
                ServerLevel level = s.overworld();
                if (resident(level, wild, cls, 20) instanceof KeeperEntity k) {
                    k.wake(level, null);
                    check(name + "_keeper_wakes", !k.isSleeping(), "");
                } else check(name + "_keeper_wakes", false, "not found");
            });
            at(base + 60, s -> {
                ServerLevel level = s.overworld();
                if (resident(level, wild, cls, 30) instanceof KeeperEntity k) {
                    k.setHealth(1f);
                    k.invulnerableTime = 0;
                    k.hurtServer(level, level.damageSources().generic(), 10f);
                }
            });
            at(base + 90, s -> {
                ServerLevel level = s.overworld();
                BlockPos site = built.get(wild);
                boolean dropped = level.getEntitiesOfClass(ItemEntity.class, new AABB(site).inflate(32, 40, 32)).stream().anyMatch(i -> i.getItem().is(relic.get()));
                check(name + "_keeper_leaves_relic", dropped, "");
            });
            w0 += 110;
        }
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
            keepLoaded(level, new BlockPos(x + 70, 0, z), 90);
            BlockPos base = new BlockPos(x, ground(level, x, z) + 1, z);
            for (var e : List.of(ModEntities.LANTERNMOTH, ModEntities.GLOAMLING, ModEntities.FORSWORN_KNIGHT, ModEntities.BARROW_WIGHT,
                ModEntities.ANIMATED_TOME, ModEntities.VEILHOUND, ModEntities.SPECTRAL_HOUSECARL,
                ModEntities.GLIMMERFAWN, ModEntities.DUSKHARE, ModEntities.MOSSBACK_TORTOISE, ModEntities.LUMEN_BEETLE, ModEntities.TIDEWADER,
                ModEntities.THORNBACK_BOAR, ModEntities.STONEWARDEN, ModEntities.RUNEWISP, ModEntities.DROWNED_CHOIRMONK, ModEntities.MIRE_HAG,
                ModEntities.GRAVE_CRAWLER, ModEntities.GLOAM_STALKER, ModEntities.SHADE_WRAITH, ModEntities.LUMENITE_MITE, ModEntities.ASHEN_REVENANT, ModEntities.GLIMMERSTAG)) {
                spawn(level, e.get(), base);
                base = base.offset(6, 0, 0);
                base = base.atY(ground(level, base.getX(), base.getZ()) + 1);
            }
            var pilgrim = spawn(level, ModEntities.LANTERNGUARD_PILGRIM.get(), base.offset(4, 0, 4));
            int trades = pilgrim.getOffers().size();
            check("pilgrim_trades", trades >= 10, "offers=" + trades);
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
                keepLoaded(level, new BlockPos(x, 0, z), 32);
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
            keepLoaded(g, GloamingTravel.THRONE, 64);
            GloamingTravel.ensureThrone(g);
            arena = GloamingTravel.THRONE;
            int found = 0;
            for (String b : List.of("veilwood", "ashen_reach")) {
                var key = ResourceKey.create(Registries.BIOME, Identifier.fromNamespaceAndPath(Oathbound.MODID, b));
                var hit = g.findClosestBiome3d(h -> h.is(key), GloamingTravel.THRONE, 4000, 64, 64);
                if (hit != null) found++;
                else log("no " + b + " within 4000 blocks of the throne");
            }
            check("gloaming_biomes", found == 2, found + "/2");
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
