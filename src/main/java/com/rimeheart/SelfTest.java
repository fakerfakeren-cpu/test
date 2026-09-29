package com.rimeheart;

import com.rimeheart.entity.boss.FrostSovereignEntity;
import com.rimeheart.entity.boss.SovereignRitual;
import com.rimeheart.entity.mob.ShardlingEntity;
import com.rimeheart.entity.projectile.FrostChargeEntity;
import com.rimeheart.entity.projectile.IceShardEntity;
import com.rimeheart.frost.Frost;
import com.rimeheart.quest.QuestLog;
import com.rimeheart.registry.*;
import com.rimeheart.world.Blueprint;
import com.rimeheart.world.BlueprintPlacer;
import com.rimeheart.world.Blueprints;
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
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Headless integration test, enabled with -Drimeheart.selftest=true. It runs a scripted scenario on a
 * dedicated server (the Frozen Sanctum, every creature and projectile, chill, and the full boss fight),
 * logs each check with a [SELFTEST] prefix and shuts the server down.
 */
public final class SelfTest {
    private static boolean active;
    private static int tick;
    private static final List<String> failures = new ArrayList<>();
    private static int checks;
    private static BlockPos arena;
    private static BlockPos sanctum;
    private static final List<Entity> spawned = new ArrayList<>();
    private static FrostSovereignEntity boss;
    private static LivingEntity dummy;

    private SelfTest() {}

    private static void log(String msg) {
        Rimeheart.LOGGER.info("[SELFTEST] {}", msg);
    }

    private static void check(String name, boolean ok, String detail) {
        checks++;
        if (ok) log("PASS " + name + (detail.isEmpty() ? "" : " (" + detail + ")"));
        else {
            failures.add(name);
            log("FAIL " + name + (detail.isEmpty() ? "" : " (" + detail + ")"));
        }
    }

    private static void step(String name, Runnable r) {
        log("step: " + name + " (tick " + tick + ")");
        try {
            r.run();
        } catch (Throwable t) {
            failures.add(name + " threw " + t);
            Rimeheart.LOGGER.error("[SELFTEST] FAIL {} threw", name, t);
        }
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (!Boolean.getBoolean("rimeheart.selftest")) return;
        active = true;
        MinecraftServer server = event.getServer();
        log("Rimeheart self-test starting on " + server.getServerVersion());
        Thread watchdog = new Thread(() -> {
            try {
                Thread.sleep(6 * 60 * 1000L);
            } catch (InterruptedException e) {
                return;
            }
            if (active) {
                Rimeheart.LOGGER.error("[SELFTEST] WATCHDOG: scenario stalled at tick {}", tick);
                for (var entry : Thread.getAllStackTraces().entrySet()) {
                    String name = entry.getKey().getName();
                    if (!(name.contains("Server") || name.contains("Worker"))) continue;
                    log("| thread " + name + " state=" + entry.getKey().getState());
                    StackTraceElement[] st = entry.getValue();
                    for (int i = 0; i < Math.min(st.length, 40); i++) log("|   at " + st[i]);
                }
                Rimeheart.LOGGER.error("[SELFTEST] RESULT: FAIL (timeout)");
                Runtime.getRuntime().halt(3);
            }
        }, "rimeheart-selftest-watchdog");
        watchdog.setDaemon(true);
        watchdog.start();
    }

    public static void onServerTick(TickEvent.ServerTickEvent.Post event) {
        if (!active) return;
        MinecraftServer server = event.server();
        ServerLevel level = server.overworld();
        tick++;
        if (tick % 100 == 0) {
            int n = 0;
            for (Entity ignored : level.getAllEntities()) n++;
            log("tick " + tick + " entities=" + n);
        }
        try {
            run(server, level);
        } catch (Throwable t) {
            failures.add("tick " + tick + " threw " + t);
            Rimeheart.LOGGER.error("[SELFTEST] unexpected exception", t);
            finish(server);
        }
    }

    private static int surface(ServerLevel level, int x, int z) {
        level.getChunk(x >> 4, z >> 4);
        return level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
    }

    private static void run(MinecraftServer server, ServerLevel level) {
        switch (tick) {
            case 1 -> step("registries", () -> staticChecks(server, level));
            case 5 -> step("sanctum", () -> buildSanctum(level));
            case 20 -> step("spawn creatures", () -> spawnCreatures(level));
            case 30 -> step("chill and weapons", () -> weapons(level));
            case 40 -> step("shardling ambush", () -> {
                BlockPos c = arena.offset(30, 0, 30);
                int y = surface(level, c.getX(), c.getZ());
                int before = level.getEntities(ModEntities.SHARDLING.get(), e -> true).size();
                for (int i = 0; i < 25; i++) {
                    BlockPos p = new BlockPos(c.getX() + (i % 5) * 2, y, c.getZ() + (i / 5) * 2);
                    level.setBlock(p.below(), net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(), 3);
                    level.setBlock(p, ModBlocks.RIME_CRYSTAL_CLUSTER.get().defaultBlockState(), 3);
                    level.destroyBlock(p, true);
                }
                int after = level.getEntities(ModEntities.SHARDLING.get(), e -> true).size();
                check("shardling_ambush", after > before, "shardlings " + before + " -> " + after);
            });
            case 60 -> step("ritual", () -> {
                BlockPos altar = arena.offset(0, 0, -40);
                int y = surface(level, altar.getX(), altar.getZ());
                SovereignRitual.begin(level, new BlockPos(altar.getX(), y, altar.getZ()));
                check("ritual_started", SovereignRitual.isActive(level), "");
                dummy = spawn(level, net.minecraft.world.entity.EntityTypes.IRON_GOLEM, altar.offset(8, 0, 0));
                if (dummy instanceof Mob m) m.setNoAi(true);
            });
            case 280 -> step("boss emerged", () -> {
                List<? extends FrostSovereignEntity> bosses = level.getEntities(ModEntities.FROST_SOVEREIGN.get(), e -> true);
                check("sovereign_spawned", !bosses.isEmpty(), "count=" + bosses.size());
                if (!bosses.isEmpty()) {
                    boss = bosses.get(0);
                    check("sovereign_emerge_finished", boss.getEmerge() == 0, "emerge=" + boss.getEmerge());
                    boss.setTarget(dummy);
                }
            });
            case 700 -> step("boss phase 2", () -> {
                if (boss == null) return;
                log("boss hp before phase 2: " + boss.getHealth() + " attack=" + boss.getAttack() + " golem alive=" + (dummy != null && dummy.isAlive()));
                boss.setHealth(boss.getMaxHealth() * 0.45f);
                if (dummy == null || !dummy.isAlive()) {
                    dummy = spawn(level, net.minecraft.world.entity.EntityTypes.IRON_GOLEM, boss.blockPosition().offset(6, 0, 0));
                    if (dummy instanceof Mob m) m.setNoAi(true);
                }
                boss.setTarget(dummy);
            });
            case 760 -> step("boss phase check", () -> {
                if (boss != null) check("sovereign_phase2", boss.getPhase() >= 2, "phase=" + boss.getPhase());
            });
            case 1150 -> step("boss death", () -> {
                if (boss == null) return;
                float before = boss.getHealth();
                boss.invulnerableTime = 0;
                boss.hurtServer(level, level.damageSources().generic(), 1000f);
                check("sovereign_damage_capped", before - boss.getHealth() <= 40.01f, "took " + (before - boss.getHealth()));
                boss.invulnerableTime = 0;
                boss.setHealth(0.5f);
                boss.hurtServer(level, level.damageSources().generic(), 10f);
                check("sovereign_dies", boss.isDeadOrDying(), "hp=" + boss.getHealth());
            });
            case 1260 -> step("boss loot", () -> {
                if (boss == null) return;
                check("sovereign_removed", boss.isRemoved(), "removed=" + boss.isRemoved());
                AABB box = boss.getBoundingBox().inflate(24, 64, 24);
                List<ItemEntity> drops = level.getEntitiesOfClass(ItemEntity.class, box);
                boolean core = drops.stream().anyMatch(i -> i.getItem().is(ModItems.SOVEREIGN_CORE.get()));
                boolean heart = drops.stream().anyMatch(i -> i.getItem().is(ModItems.GLACIAL_HEART.get()));
                check("sovereign_drops_rewards", core && heart, "drops=" + drops.size());
            });
            case 1280 -> step("survivors", () -> {
                int alive = 0;
                for (Entity e : spawned) if (e.isAlive()) alive++;
                log("test creatures still alive: " + alive + "/" + spawned.size());
            });
            case 1300 -> finish(server);
            default -> {}
        }
        if (tick > 20 && tick % 100 == 0) {
            for (Entity e : spawned) {
                if (e.isAlive() && e.getY() < level.getMinY()) failures.add(e.getType() + " fell out of the world");
            }
        }
    }

    private static <T extends Entity> T spawn(ServerLevel level, EntityType<T> type, BlockPos at) {
        int y = surface(level, at.getX(), at.getZ());
        T e = type.create(level, EntitySpawnReason.COMMAND);
        if (e == null) throw new IllegalStateException("could not create " + type);
        e.snapTo(at.getX() + 0.5, y + 1, at.getZ() + 0.5, 0, 0);
        if (e instanceof Mob m) m.setPersistenceRequired();
        level.addFreshEntity(e);
        spawned.add(e);
        return e;
    }

    private static void staticChecks(MinecraftServer server, ServerLevel level) {
        check("items_registered", ModItems.ITEMS.getEntries().size() >= 44, "items=" + ModItems.ITEMS.getEntries().size());
        check("blocks_registered", ModBlocks.BLOCKS.getEntries().size() >= 13, "blocks=" + ModBlocks.BLOCKS.getEntries().size());
        check("entities_registered", ModEntities.ENTITIES.getEntries().size() == 5, "entities=" + ModEntities.ENTITIES.getEntries().size());
        check("spawn_egg_bound", ModItems.FROST_WRAITH_SPAWN_EGG.get().getDefaultInstance().getComponents().has(net.minecraft.core.component.DataComponents.ENTITY_DATA), "");

        String[] loot = {"chests/sanctum_common", "chests/sanctum_vault", "entities/frost_wraith", "entities/shardling", "entities/frost_sovereign",
            "blocks/frostiron_ore", "blocks/rime_crystal_ore", "blocks/rime_crystal_cluster", "blocks/glacial_altar", "quests/journal"};
        int lootOk = 0;
        for (String l : loot) {
            LootTable t = server.reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Rimeheart.MODID, l)));
            if (t != LootTable.EMPTY) lootOk++;
            else log("missing loot table " + l);
        }
        check("loot_tables_loaded", lootOk == loot.length, lootOk + "/" + loot.length);

        int recipes = 0;
        for (var holder : server.getRecipeManager().getRecipes()) {
            if (holder.id().identifier().getNamespace().equals(Rimeheart.MODID)) recipes++;
        }
        check("recipes_loaded", recipes >= 35, "recipes=" + recipes);

        int quests = 0;
        for (String id : QuestLog.QUESTS.keySet()) {
            if (server.getAdvancements().get(QuestLog.questAdvancement(id)) != null && server.getAdvancements().get(QuestLog.claimedAdvancement(id)) != null) quests++;
            else log("missing quest advancement for " + id);
        }
        check("quests_loaded", quests == QuestLog.QUESTS.size(), quests + "/" + QuestLog.QUESTS.size());

        var structures = server.registryAccess().lookupOrThrow(Registries.STRUCTURE);
        check("sanctum_registered", structures.get(ResourceKey.create(Registries.STRUCTURE, Identifier.fromNamespaceAndPath(Rimeheart.MODID, "frozen_sanctum"))).isPresent(), "");
        var placed = server.registryAccess().lookupOrThrow(Registries.PLACED_FEATURE);
        int ores = 0;
        for (String f : new String[]{"frostiron_ore", "rime_crystal_ore", "rimestone_blob"}) {
            if (placed.get(ResourceKey.create(Registries.PLACED_FEATURE, Identifier.fromNamespaceAndPath(Rimeheart.MODID, f))).isPresent()) ores++;
        }
        check("ore_features_registered", ores == 3, ores + "/3");

        BlockPos spawn = level.getRespawnData().pos();
        arena = new BlockPos(spawn.getX() + 300, 0, spawn.getZ() + 300);
        log("arena at " + arena);
        int acx = (arena.getX() + 32) >> 4, acz = arena.getZ() >> 4;
        int forced = 0;
        for (int cx = acx - 6; cx <= acx + 6; cx++)
            for (int cz = acz - 6; cz <= acz + 6; cz++)
                if (level.setChunkForced(cx, cz, true)) forced++;
        log("force-loaded " + forced + " arena chunks");
        long t0 = System.nanoTime();
        BlockPos found = level.findNearestMapStructure(ModTags.FROZEN_SANCTUM, spawn, 100, false);
        log("nearest natural Frozen Sanctum: " + found + " (" + (System.nanoTime() - t0) / 1_000_000 + " ms)");
    }

    private static void buildSanctum(ServerLevel level) {
        int x = arena.getX() - 60, z = arena.getZ() - 60;
        BlockPos origin = new BlockPos(x, surface(level, x, z), z);
        Blueprint bp = Blueprints.build(Blueprints.Type.FROZEN_SANCTUM, 12345L);
        BlueprintPlacer.placeNow(level, bp, origin);
        int present = 0, sample = 0;
        for (var e : bp.blocks.long2ObjectEntrySet()) {
            if (e.getValue().isAir()) continue;
            if (++sample > 600) break;
            long k = e.getLongKey();
            if (level.getBlockState(origin.offset(BlockPos.getX(k), BlockPos.getY(k), BlockPos.getZ(k))).is(e.getValue().getBlock())) present++;
        }
        check("build_frozen_sanctum", sample > 0 && present >= sample * 0.9, "blocks=" + bp.blocks.size() + " verified=" + present + "/" + Math.min(sample, 600));
        sanctum = origin;
        int f = Blueprints.HALL_FLOOR;
        check("sanctum_altar", level.getBlockState(origin.offset(0, 1, 0)).is(ModBlocks.GLACIAL_ALTAR.get()), "");
        check("sanctum_altar_open_sky", level.canSeeSky(origin.offset(0, 2, 0)), "");
        check("sanctum_hollow_wall", level.getBlockState(origin.offset(9, f + 1, 0)).is(ModBlocks.HOLLOW_RIMESTONE_BRICKS.get()), "");
        int chests = 0;
        for (BlockPos p : BlockPos.betweenClosed(origin.offset(-10, f, -10), origin.offset(16, f + 3, 10))) {
            if (level.getBlockEntity(p) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity) chests++;
        }
        check("sanctum_chests", chests == 3, "chests=" + chests);
    }

    private static void spawnCreatures(ServerLevel level) {
        var wraith = spawn(level, ModEntities.FROST_WRAITH.get(), arena.offset(0, 0, 0));
        var shardling = spawn(level, ModEntities.SHARDLING.get(), arena.offset(6, 0, 0));
        var target = spawn(level, net.minecraft.world.entity.EntityTypes.VILLAGER, arena.offset(6, 0, 8));
        wraith.setTarget(target);
        shardling.setTarget(target);
        check("creatures_spawned", wraith.isAlive() && shardling.isAlive(), "");
        check("winter_creatures_immune", Frost.immune(wraith) && Frost.immune(shardling), "");
    }

    private static void weapons(ServerLevel level) {
        int y = surface(level, arena.getX(), arena.getZ() + 20);
        Vec3 c = new Vec3(arena.getX() + 0.5, y + 1.5, arena.getZ() + 20.5);
        var zombie = spawn(level, net.minecraft.world.entity.EntityTypes.ZOMBIE, BlockPos.containing(c.add(4, 0, 0)));
        boolean frozen = Frost.chill(zombie, 200);
        check("chill_freezes", frozen && Frost.isFrozen(zombie), "ticksFrozen=" + zombie.getTicksFrozen());
        var victim = spawn(level, net.minecraft.world.entity.EntityTypes.ZOMBIE, BlockPos.containing(c.add(-4, 0, 0)));
        IceShardEntity shard = IceShardEntity.shoot(level, null, c.add(0, 0.5, 0), new Vec3(-1, 0, 0), 5f, 80);
        // water pool for the Frost Charge
        BlockPos pool = BlockPos.containing(c.add(0, -1.5, 8));
        for (BlockPos p : BlockPos.betweenClosed(pool.offset(-1, 0, -1), pool.offset(1, 0, 1))) {
            level.setBlock(p, net.minecraft.world.level.block.Blocks.WATER.defaultBlockState(), 3);
            level.setBlock(p.above(), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
        }
        FrostChargeEntity.burst(level, Vec3.atCenterOf(pool).add(0, 1, 0), null);
        check("frost_charge_freezes_water", level.getBlockState(pool).is(net.minecraft.world.level.block.Blocks.FROSTED_ICE), level.getBlockState(pool).toString());
        check("weapon_entities_spawned", shard.isAlive() && victim.isAlive(), "");
    }

    private static void finish(MinecraftServer server) {
        active = false;
        log("checks run: " + checks + ", failures: " + failures.size());
        for (String f : failures) log("  failed: " + f);
        log(failures.isEmpty() ? "RESULT: PASS" : "RESULT: FAIL");
        if (arena != null) {
            ServerLevel level = server.overworld();
            int acx = (arena.getX() + 32) >> 4, acz = arena.getZ() >> 4;
            for (int cx = acx - 6; cx <= acx + 6; cx++)
                for (int cz = acz - 6; cz <= acz + 6; cz++)
                    level.setChunkForced(cx, cz, false);
        }
        server.halt(false);
    }
}
