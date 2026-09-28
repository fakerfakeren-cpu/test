package com.astralfall;

import com.astralfall.block.StarLockBlock;
import com.astralfall.entity.MeteorEntity;
import com.astralfall.entity.SingularityEntity;
import com.astralfall.entity.boss.AstraeusEntity;
import com.astralfall.entity.boss.BossSummoner;
import com.astralfall.entity.projectile.CrystalShardEntity;
import com.astralfall.entity.projectile.StarBoltEntity;
import com.astralfall.entity.projectile.StarSlashEntity;
import com.astralfall.event.Starfall;
import com.astralfall.registry.*;
import com.astralfall.world.Blueprint;
import com.astralfall.world.BlueprintPlacer;
import com.astralfall.world.Blueprints;
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
 * Headless integration test, enabled with -Dastralfall.selftest=true. It runs a scripted scenario on a
 * dedicated server (every structure, creature, projectile, the Starfall and the full boss fight),
 * logs each check with a [SELFTEST] prefix and shuts the server down.
 */
public final class SelfTest {
    private static boolean active;
    private static int tick;
    private static final List<String> failures = new ArrayList<>();
    private static int checks;
    private static BlockPos arena;
    private static BlockPos observatory;
    private static final List<Entity> spawned = new ArrayList<>();
    private static AstraeusEntity boss;
    private static LivingEntity dummy;

    private SelfTest() {}

    private static void log(String msg) {
        Astralfall.LOGGER.info("[SELFTEST] {}", msg);
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
            Astralfall.LOGGER.error("[SELFTEST] FAIL {} threw", name, t);
        }
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (!Boolean.getBoolean("astralfall.selftest")) return;
        active = true;
        MinecraftServer server = event.getServer();
        log("Astralfall self-test starting on " + server.getServerVersion());
        Thread watchdog = new Thread(() -> {
            try {
                Thread.sleep(6 * 60 * 1000L);
            } catch (InterruptedException e) {
                return;
            }
            if (active) {
                Astralfall.LOGGER.error("[SELFTEST] WATCHDOG: scenario stalled at tick {}", tick);
                for (var entry : Thread.getAllStackTraces().entrySet()) {
                    String name = entry.getKey().getName();
                    if (!(name.contains("Server") || name.contains("Worker"))) continue;
                    log("| thread " + name + " state=" + entry.getKey().getState());
                    StackTraceElement[] st = entry.getValue();
                    for (int i = 0; i < Math.min(st.length, 40); i++) log("|   at " + st[i]);
                }
                Astralfall.LOGGER.error("[SELFTEST] RESULT: FAIL (timeout)");
                Runtime.getRuntime().halt(3);
            }
        }, "astralfall-selftest-watchdog");
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
            Astralfall.LOGGER.error("[SELFTEST] unexpected exception", t);
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
            case 5 -> step("structures", () -> buildStructures(level));
            case 10 -> step("star lock", () -> {
                BlockPos lock = observatory.offset(0, 2, -9);
                boolean isLock = level.getBlockState(lock).is(ModBlocks.STAR_LOCK.get());
                int removed = StarLockBlock.unseal(level, lock);
                check("star_lock_unseals_vault", isLock && removed >= 8, "lock=" + isLock + " removed=" + removed);
            });
            case 20 -> step("spawn creatures", () -> spawnCreatures(level));
            case 30 -> step("weapons", () -> weapons(level));
            case 40 -> step("meteors", () -> {
                for (Starfall.Variant v : new Starfall.Variant[]{Starfall.Variant.NORMAL, Starfall.Variant.FALLEN_STAR, Starfall.Variant.CRAWLER}) {
                    BlockPos target = arena.offset(40 + v.ordinal() * 25, 0, 30);
                    surface(level, target.getX(), target.getZ());
                    Starfall.spawnMeteor(level, target, v, 1.8f);
                }
                Starfall.startStarstorm(level, 200);
                check("starstorm_active", Starfall.isStarstorm(level), "");
            });
            case 200 -> step("meteor impacts", () -> {
                int rock = 0, stars = 0;
                BlockPos c = arena.offset(65, 0, 30);
                c = c.atY(surface(level, c.getX(), c.getZ()));
                for (BlockPos p : BlockPos.betweenClosed(c.offset(-50, -24, -30), c.offset(50, 16, 30))) {
                    var s = level.getBlockState(p);
                    if (s.is(ModBlocks.METEORITE_ROCK.get()) || s.is(ModBlocks.STARMETAL_ORE.get())) rock++;
                    if (s.is(ModBlocks.FALLEN_STAR.get())) stars++;
                }
                check("meteor_craters_created", rock > 5, "meteorite blocks=" + rock);
                check("fallen_star_landed", stars >= 1, "fallen stars=" + stars);
                long meteors = level.getEntities(ModEntities.METEOR.get(), e -> true).size();
                log("meteors in flight: " + meteors);
                Starfall.endStarstorm(level);
            });
            case 210 -> step("boss ritual", () -> {
                BlockPos altar = arena.offset(0, 0, -40);
                int y = surface(level, altar.getX(), altar.getZ());
                BossSummoner.begin(level, new BlockPos(altar.getX(), y, altar.getZ()));
                check("ritual_started", BossSummoner.isRitualActive(level), "");
                dummy = spawn(level, net.minecraft.world.entity.EntityTypes.IRON_GOLEM, altar.offset(8, 0, 0));
                if (dummy instanceof Mob m) m.setNoAi(true);
            });
            case 470 -> step("boss emerged", () -> {
                List<? extends AstraeusEntity> bosses = level.getEntities(ModEntities.ASTRAEUS.get(), e -> true);
                check("astraeus_spawned", !bosses.isEmpty(), "count=" + bosses.size());
                if (!bosses.isEmpty()) {
                    boss = bosses.get(0);
                    check("astraeus_emerge_finished", boss.getEmerge() == 0, "emerge=" + boss.getEmerge());
                    boss.setTarget(dummy);
                }
            });
            case 1100 -> step("boss phase 2", () -> {
                if (boss == null) return;
                log("boss hp before phase 2: " + boss.getHealth() + " attack=" + boss.getAttack());
                boss.setHealth(boss.getMaxHealth() * 0.45f);
                if (dummy != null && !dummy.isAlive()) {
                    dummy = spawn(level, net.minecraft.world.entity.EntityTypes.IRON_GOLEM, boss.blockPosition().offset(6, -4, 0));
                    if (dummy instanceof Mob m) m.setNoAi(true);
                }
                boss.setTarget(dummy);
            });
            case 1150 -> step("boss phase check", () -> {
                if (boss != null) check("astraeus_phase2", boss.getPhase() >= 2, "phase=" + boss.getPhase());
            });
            case 1700 -> step("boss phase 3", () -> {
                if (boss == null) return;
                boss.setHealth(boss.getMaxHealth() * 0.15f);
                if (dummy == null || !dummy.isAlive()) {
                    dummy = spawn(level, net.minecraft.world.entity.EntityTypes.IRON_GOLEM, boss.blockPosition().offset(6, -4, 0));
                    if (dummy instanceof Mob m) m.setNoAi(true);
                }
                boss.setTarget(dummy);
            });
            case 2100 -> step("boss death", () -> {
                if (boss == null) return;
                check("astraeus_phase3", boss.getPhase() >= 3, "phase=" + boss.getPhase());
                float before = boss.getHealth();
                boss.hurtServer(level, level.damageSources().generic(), 1000f);
                check("astraeus_damage_capped", before - boss.getHealth() <= 45.01f, "took " + (before - boss.getHealth()));
                // Next hit lands after the normal invulnerability window, like a second player swing would.
                boss.invulnerableTime = 0;
                boss.setHealth(0.5f);
                boss.hurtServer(level, level.damageSources().generic(), 10f);
                check("astraeus_dies", boss.isDeadOrDying(), "hp=" + boss.getHealth());
            });
            case 2260 -> step("boss loot", () -> {
                if (boss == null) return;
                check("astraeus_removed", boss.isRemoved(), "removed=" + boss.isRemoved());
                AABB box = boss.getBoundingBox().inflate(24, 64, 24);
                List<ItemEntity> drops = level.getEntitiesOfClass(ItemEntity.class, box);
                boolean greatsword = drops.stream().anyMatch(i -> i.getItem().is(ModItems.ECLIPSE_GREATSWORD.get()));
                boolean core = drops.stream().anyMatch(i -> i.getItem().is(ModItems.STELLAR_CORE.get()));
                check("astraeus_drops_rewards", greatsword && core, "drops=" + drops.size());
            });
            case 2280 -> step("survivors", () -> {
                int alive = 0;
                for (Entity e : spawned) if (e.isAlive()) alive++;
                log("test creatures still alive: " + alive + "/" + spawned.size());
            });
            case 2300 -> finish(server);
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
        check("items_registered", ModItems.ITEMS.getEntries().size() >= 58, "items=" + ModItems.ITEMS.getEntries().size());
        check("blocks_registered", ModBlocks.BLOCKS.getEntries().size() >= 24, "blocks=" + ModBlocks.BLOCKS.getEntries().size());
        check("entities_registered", ModEntities.ENTITIES.getEntries().size() == 11, "entities=" + ModEntities.ENTITIES.getEntries().size());
        check("spawn_egg_bound", ModItems.VOID_STALKER_SPAWN_EGG.get().getDefaultInstance().getComponents().has(net.minecraft.core.component.DataComponents.ENTITY_DATA), "");

        String[] loot = {"chests/observatory_common", "chests/observatory_library", "chests/observatory_vault", "chests/fallen_vessel", "chests/sky_shrine",
            "entities/astraeus", "entities/void_stalker", "entities/meteorite_crawler", "entities/void_gazer", "entities/astral_wisp",
            "blocks/starmetal_ore", "blocks/skyshard_cluster", "blocks/fallen_star_block", "quests/journal"};
        int lootOk = 0;
        for (String l : loot) {
            LootTable t = server.reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Astralfall.MODID, l)));
            if (t != LootTable.EMPTY) lootOk++;
            else log("missing loot table " + l);
        }
        check("loot_tables_loaded", lootOk == loot.length, lootOk + "/" + loot.length);

        int recipes = 0;
        for (var holder : server.getRecipeManager().getRecipes()) {
            if (holder.id().identifier().getNamespace().equals(Astralfall.MODID)) recipes++;
        }
        check("recipes_loaded", recipes >= 35, "recipes=" + recipes);

        int adv = 0;
        for (var holder : server.getAdvancements().getAllAdvancements()) {
            if (holder.id().getNamespace().equals(Astralfall.MODID)) adv++;
        }
        check("quests_loaded", adv >= 20, "advancements=" + adv);

        var structures = server.registryAccess().lookupOrThrow(Registries.STRUCTURE);
        int st = 0;
        for (String s : new String[]{"shattered_observatory", "fallen_vessel", "sky_shrine"}) {
            if (structures.get(ResourceKey.create(Registries.STRUCTURE, Identifier.fromNamespaceAndPath(Astralfall.MODID, s))).isPresent()) st++;
        }
        check("structures_registered", st == 3, st + "/3");
        var placed = server.registryAccess().lookupOrThrow(Registries.PLACED_FEATURE);
        check("impact_site_feature", placed.get(ResourceKey.create(Registries.PLACED_FEATURE, Identifier.fromNamespaceAndPath(Astralfall.MODID, "impact_site"))).isPresent(), "");

        BlockPos spawn = level.getRespawnData().pos();
        arena = new BlockPos(spawn.getX() + 300, 0, spawn.getZ() + 300);
        log("arena at " + arena);
        // No player is online, so keep the arena loaded and entity-ticking.
        int acx = (arena.getX() + 32) >> 4, acz = arena.getZ() >> 4;
        int forced = 0;
        for (int cx = acx - 6; cx <= acx + 6; cx++)
            for (int cz = acz - 6; cz <= acz + 6; cz++)
                if (level.setChunkForced(cx, cz, true)) forced++;
        log("force-loaded " + forced + " arena chunks");

        long t0 = System.nanoTime();
        BlockPos found = level.findNearestMapStructure(ModTags.OBSERVATORY, spawn, 100, false);
        log("nearest natural observatory: " + found + " (" + (System.nanoTime() - t0) / 1_000_000 + " ms)");
        check("observatory_locatable", found != null, String.valueOf(found));
        BlockPos vessel = level.findNearestMapStructure(ModTags.FALLEN_VESSEL, spawn, 100, false);
        check("fallen_vessel_locatable", vessel != null, String.valueOf(vessel));
        BlockPos shrine = level.findNearestMapStructure(ModTags.SKY_SHRINE, spawn, 100, false);
        check("sky_shrine_locatable", shrine != null, String.valueOf(shrine));
    }

    private static void buildStructures(ServerLevel level) {
        int i = 0;
        for (Blueprints.Type type : Blueprints.Type.values()) {
            int x = arena.getX() - 150 + i * 90, z = arena.getZ() - 150;
            int y = surface(level, x, z) + (type == Blueprints.Type.SKY_SHRINE ? 40 : type == Blueprints.Type.FALLEN_VESSEL ? -2 : 0);
            BlockPos origin = new BlockPos(x, y, z);
            long t0 = System.nanoTime();
            Blueprint bp = Blueprints.build(type, 12345L + i);
            BlueprintPlacer.placeNow(level, bp, origin);
            long ms = (System.nanoTime() - t0) / 1_000_000;
            int present = 0, sample = 0;
            for (var e : bp.blocks.long2ObjectEntrySet()) {
                if (e.getValue().isAir()) continue;
                if (++sample > 400) break;
                long k = e.getLongKey();
                if (level.getBlockState(origin.offset(BlockPos.getX(k), BlockPos.getY(k), BlockPos.getZ(k))).is(e.getValue().getBlock())) present++;
            }
            check("build_" + type.id(), sample > 0 && present >= sample * 0.9, "blocks=" + bp.blocks.size() + " chests=" + bp.chests.size() + " verified=" + present + "/" + Math.min(sample, 400) + " in " + ms + "ms");
            if (type == Blueprints.Type.OBSERVATORY) observatory = origin;
            i++;
        }
        int chests = 0;
        for (BlockPos p : BlockPos.betweenClosed(observatory.offset(-10, -10, -23), observatory.offset(10, 10, 10))) {
            if (level.getBlockEntity(p) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity) chests++;
        }
        check("observatory_chests", chests >= 6, "chests=" + chests);
        check("observatory_altar", level.getBlockState(observatory.offset(0, 15, 0)).is(ModBlocks.ASTRAL_ALTAR.get()), "");
        check("observatory_telescope", level.getBlockState(observatory.offset(-4, 16, 4)).is(ModBlocks.TELESCOPE_EYEPIECE.get()), "");
    }

    private static void spawnCreatures(ServerLevel level) {
        var wisp = spawn(level, ModEntities.ASTRAL_WISP.get(), arena.offset(0, 0, 0));
        var stalker = spawn(level, ModEntities.VOID_STALKER.get(), arena.offset(6, 0, 0));
        var crawler = spawn(level, ModEntities.METEORITE_CRAWLER.get(), arena.offset(12, 0, 0));
        var gazer = spawn(level, ModEntities.VOID_GAZER.get(), arena.offset(18, 0, 0));
        var target = spawn(level, net.minecraft.world.entity.EntityTypes.VILLAGER, arena.offset(12, 0, 8));
        crawler.setTarget(target);
        gazer.setTarget(target);
        stalker.setTarget(target);
        check("creatures_spawned", wisp.isAlive() && stalker.isAlive() && crawler.isAlive() && gazer.isAlive(), "");
    }

    private static void weapons(ServerLevel level) {
        int y = surface(level, arena.getX(), arena.getZ() + 20);
        Vec3 c = new Vec3(arena.getX() + 0.5, y + 1.5, arena.getZ() + 20.5);
        var victim = spawn(level, net.minecraft.world.entity.EntityTypes.ZOMBIE, BlockPos.containing(c.add(4, 0, 0)));
        var slash = new StarSlashEntity(ModEntities.STAR_SLASH.get(), level);
        slash.setPos(c.x, c.y, c.z);
        slash.setDeltaMovement(1.6, 0, 0);
        level.addFreshEntity(slash);
        StarBoltEntity.shoot(level, null, c.add(0, 2, 0), new Vec3(1, 0, 0), 0, 5f, victim);
        CrystalShardEntity.launch(level, null, c.add(0, 3, 0), victim, 5);
        SingularityEntity.spawn(level, c.add(8, 0, 0), null, 60, 7f, 10f, false);
        var grenade = new com.astralfall.entity.projectile.SingularityGrenadeEntity(ModEntities.SINGULARITY_GRENADE.get(), level);
        grenade.setPos(c.x, c.y + 3, c.z - 6);
        grenade.setDeltaMovement(0, -0.5, 0.2);
        level.addFreshEntity(grenade);
        check("weapon_entities_spawned", slash.isAlive() && victim.isAlive(), "");
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
