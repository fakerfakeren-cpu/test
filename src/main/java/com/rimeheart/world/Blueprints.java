package com.rimeheart.world;

import com.rimeheart.Rimeheart;
import com.rimeheart.registry.ModBlocks;
import com.rimeheart.registry.ModEntities;
import com.rimeheart.world.Blueprint.Palette;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Procedural layout of the Frozen Sanctum: broken pillars and a stairwell on the surface, a buried hall
 * with the Glacial Altar, and a sealed vault behind a hollow wall.
 */
public final class Blueprints {
    public enum Type {
        FROZEN_SANCTUM;

        public static Type byName(String name) {
            return valueOf(name.toUpperCase(Locale.ROOT));
        }

        public String id() {
            return name().toLowerCase(Locale.ROOT);
        }
    }

    public static final ResourceKey<LootTable> SANCTUM_COMMON = loot("chests/sanctum_common");
    public static final ResourceKey<LootTable> SANCTUM_VAULT = loot("chests/sanctum_vault");
    /** Floor Y of the buried hall, relative to the surface origin. */
    public static final int HALL_FLOOR = -10;

    private static final Map<String, Blueprint> CACHE = Collections.synchronizedMap(new LinkedHashMap<>(16, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, Blueprint> eldest) {
            return size() > 12;
        }
    });

    private Blueprints() {}

    private static ResourceKey<LootTable> loot(String path) {
        return ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Rimeheart.MODID, path));
    }

    public static Blueprint get(Type type, long seed) {
        String key = type + ":" + seed;
        Blueprint bp = CACHE.get(key);
        if (bp == null) {
            bp = build(type, seed);
            CACHE.put(key, bp);
        }
        return bp;
    }

    public static Blueprint build(Type type, long seed) {
        Blueprint bp = new Blueprint(RandomSource.create(seed));
        sanctum(bp);
        return bp;
    }

    private static void sanctum(Blueprint bp) {
        RandomSource r = bp.random;
        BlockState bricks = ModBlocks.RIMESTONE_BRICKS.get().defaultBlockState();
        BlockState cracked = ModBlocks.CRACKED_RIMESTONE_BRICKS.get().defaultBlockState();
        BlockState chiseled = ModBlocks.CHISELED_RIMESTONE_BRICKS.get().defaultBlockState();
        BlockState hollow = ModBlocks.HOLLOW_RIMESTONE_BRICKS.get().defaultBlockState();
        BlockState lamp = ModBlocks.FROST_LAMP.get().defaultBlockState();
        BlockState permafrost = ModBlocks.PERMAFROST.get().defaultBlockState();
        BlockState cluster = ModBlocks.RIME_CRYSTAL_CLUSTER.get().defaultBlockState();
        Palette wall = new Palette().add(bricks, 6).add(cracked, 2).add(ModBlocks.RIMESTONE.get().defaultBlockState(), 1);
        Palette floor = new Palette().add(bricks, 4).add(Blocks.PACKED_ICE.defaultBlockState(), 2).add(permafrost, 1);
        Palette ground = new Palette().add(Blocks.SNOW_BLOCK.defaultBlockState(), 3).add(permafrost, 2).add(Blocks.PACKED_ICE.defaultBlockState(), 1);

        // ---------------- surface: frozen plaza, broken pillars, stairwell arch
        bp.fillAir(-10, 1, -18, 10, 7, 10);
        bp.disk(0, 0, 0, 7.5, ground);
        for (int i = 0; i < 8; i++) {
            double a = i * Math.PI / 4 + 0.2;
            int px = (int) Math.round(Math.cos(a) * 9), pz = (int) Math.round(Math.sin(a) * 9);
            int h = 2 + r.nextInt(5);
            for (int y = 0; y <= h; y++) bp.set(px, y, pz, y == h && r.nextBoolean() ? chiseled : wall.pick(r));
            bp.foundation(px, pz);
        }
        for (int x = -2; x <= 2; x++) {
            bp.set(x, 4, -17, chiseled);
            for (int y = 0; y <= 3; y++) {
                if (Math.abs(x) == 2) bp.set(x, y, -17, bricks);
            }
        }
        bp.set(-2, 5, -17, lamp);
        bp.set(2, 5, -17, lamp);

        // ---------------- stairwell: 3 wide, descends south into the hall
        for (int i = 0; i <= 8; i++) {
            int y = -1 - i, z = -16 + i;
            for (int x = -2; x <= 2; x++) {
                for (int yy = y - 1; yy <= y + 4; yy++) {
                    boolean side = Math.abs(x) == 2;
                    boolean roof = yy == y + 4 && y + 4 <= -1;
                    if (side || roof) bp.set(x, yy, z, wall.pick(r));
                    else if (yy == y) bp.set(x, yy, z, Blueprint.stairs(Blocks.STONE_BRICK_STAIRS.defaultBlockState(), Direction.NORTH));
                    else if (yy == y - 1) bp.set(x, yy, z, bricks);
                    else bp.air(x, yy, z);
                }
            }
            if (i % 3 == 1) bp.set(-2, y + 2, z, lamp);
        }

        // ---------------- the buried hall (17 x 17)
        int f = HALL_FLOOR;
        for (int x = -9; x <= 9; x++) {
            for (int z = -9; z <= 9; z++) {
                boolean edge = Math.abs(x) == 9 || Math.abs(z) == 9;
                bp.set(x, f, z, edge ? bricks : floor.pick(r));
                bp.set(x, f + 7, z, (x + z) % 4 == 0 && !edge ? chiseled : wall.pick(r));
                for (int y = f + 1; y <= f + 6; y++) {
                    if (edge) bp.set(x, y, z, wall.pick(r));
                    else bp.air(x, y, z);
                }
            }
        }
        // entrance from the stairwell
        for (int x = -1; x <= 1; x++)
            for (int y = f + 1; y <= f + 3; y++) bp.air(x, y, -9);
        // pillars with lamps
        for (int[] p : new int[][]{{-5, -5}, {5, -5}, {-5, 5}, {5, 5}}) {
            for (int y = f + 1; y <= f + 6; y++) bp.set(p[0], y, p[1], y == f + 4 ? lamp : bricks);
        }
        // dais and the Glacial Altar
        for (int x = -2; x <= 2; x++)
            for (int z = -2; z <= 2; z++) bp.set(x, f + 1, z, Math.abs(x) == 2 || Math.abs(z) == 2 ? chiseled : bricks);
        bp.set(0, f + 2, 0, ModBlocks.GLACIAL_ALTAR.get().defaultBlockState());
        for (int[] p : new int[][]{{-2, -2}, {2, -2}, {-2, 2}, {2, 2}}) bp.set(p[0], f + 2, p[1], lamp);
        // crystal growth along the walls
        for (int i = 0; i < 10; i++) {
            int x = -8 + r.nextInt(17), z = -8 + r.nextInt(17);
            if (Math.abs(x) < 4 && Math.abs(z) < 4) continue;
            if (Math.abs(x) <= 1 && z < -5) continue;
            if (bp.get(x, f + 1, z) == null || bp.get(x, f + 1, z).isAir()) bp.set(x, f + 1, z, cluster);
        }
        bp.chest(-8, f + 1, 7, Direction.EAST, SANCTUM_COMMON);
        bp.chest(8, f + 1, 7, Direction.WEST, SANCTUM_COMMON);
        bp.mob(-4, f + 3, 0, () -> ModEntities.FROST_WRAITH.get());
        bp.mob(4, f + 3, 0, () -> ModEntities.FROST_WRAITH.get());
        bp.mob(0, f + 1, 6, () -> ModEntities.SHARDLING.get());

        // ---------------- the sealed vault, behind a hollow stretch of the east wall
        for (int y = f + 1; y <= f + 2; y++) {
            for (int z = -1; z <= 1; z++) bp.set(9, y, z, hollow);
        }
        bp.set(9, f + 1, -2, cracked);
        bp.set(9, f + 1, 2, cracked);
        for (int x = 10; x <= 15; x++) {
            for (int z = -3; z <= 3; z++) {
                boolean edge = x == 15 || Math.abs(z) == 3;
                bp.set(x, f, z, chiseled);
                bp.set(x, f + 5, z, x == 12 && z == 0 ? lamp : bricks);
                for (int y = f + 1; y <= f + 4; y++) {
                    if (edge) bp.set(x, y, z, bricks);
                    else bp.air(x, y, z);
                }
            }
        }
        bp.chest(14, f + 1, 0, Direction.WEST, SANCTUM_VAULT);
        bp.set(14, f + 1, -2, cluster);
        bp.set(14, f + 1, 2, cluster);
        bp.set(11, f + 1, -2, cluster);
    }
}
