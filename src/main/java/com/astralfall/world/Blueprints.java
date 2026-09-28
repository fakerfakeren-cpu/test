package com.astralfall.world;

import com.astralfall.Astralfall;
import com.astralfall.registry.ModBlocks;
import com.astralfall.registry.ModEntities;
import com.astralfall.world.Blueprint.Palette;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/** Procedural layouts for every Astralfall structure. */
public final class Blueprints {
    public enum Type {
        OBSERVATORY, FALLEN_VESSEL, SKY_SHRINE, CRATER;

        public static Type byName(String name) {
            return valueOf(name.toUpperCase(Locale.ROOT));
        }

        public String id() {
            return name().toLowerCase(Locale.ROOT);
        }
    }

    public static final ResourceKey<LootTable> OBSERVATORY_COMMON = loot("chests/observatory_common");
    public static final ResourceKey<LootTable> OBSERVATORY_LIBRARY = loot("chests/observatory_library");
    public static final ResourceKey<LootTable> OBSERVATORY_VAULT = loot("chests/observatory_vault");
    public static final ResourceKey<LootTable> FALLEN_VESSEL = loot("chests/fallen_vessel");
    public static final ResourceKey<LootTable> SKY_SHRINE = loot("chests/sky_shrine");

    private static final Map<String, Blueprint> CACHE = Collections.synchronizedMap(new LinkedHashMap<>(16, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, Blueprint> eldest) {
            return size() > 12;
        }
    });

    private Blueprints() {}

    private static ResourceKey<LootTable> loot(String path) {
        return ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Astralfall.MODID, path));
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
        switch (type) {
            case OBSERVATORY -> observatory(bp);
            case FALLEN_VESSEL -> vessel(bp);
            case SKY_SHRINE -> shrine(bp);
            case CRATER -> crater(bp);
        }
        return bp;
    }

    // ------------------------------------------------------------------ helpers
    private static BlockState s(net.minecraft.world.level.block.Block b) {
        return b.defaultBlockState();
    }

    private static BlockState hangingLantern() {
        return Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, true);
    }

    private static Direction tangent(double angle) {
        return Blueprint.outward(-Math.sin(angle), Math.cos(angle));
    }

    // ================================================================== OBSERVATORY
    private static void observatory(Blueprint bp) {
        RandomSource r = bp.random;
        BlockState BR = s(ModBlocks.ASTRAL_BRICKS.get());
        BlockState CR = s(ModBlocks.CRACKED_ASTRAL_BRICKS.get());
        BlockState CH = s(ModBlocks.CHISELED_ASTRAL_BRICKS.get());
        BlockState GL = s(ModBlocks.ASTRAL_GLASS.get());
        BlockState SLAB = s(ModBlocks.ASTRAL_BRICK_SLAB.get());
        BlockState STAIR = s(ModBlocks.ASTRAL_BRICK_STAIRS.get());
        BlockState SM = s(ModBlocks.STARMETAL_BLOCK.get());
        BlockState SEALED = s(ModBlocks.SEALED_ASTRAL_BRICKS.get());
        Palette wall = new Palette().add(BR, 10).add(CR, 4).add(s(ModBlocks.OVERGROWN_ASTRAL_BRICKS.get()), 2);
        Palette floor = new Palette().add(BR, 9).add(CR, 3).add(s(ModBlocks.OVERGROWN_ASTRAL_BRICKS.get()), 1);
        Palette dome = new Palette().add(GL, 7).add(BR, 1);
        bp.foundationState = BR;

        // clear the site, lay the plinth
        for (int x = -21; x <= 21; x++)
            for (int z = -21; z <= 21; z++) {
                double d = Math.sqrt(x * x + z * z);
                if (d > 20.6) continue;
                for (int y = 1; y <= 14; y++) bp.air(x, y, z);
                if (d <= 19.5) {
                    bp.set(x, 0, z, floor.pick(r));
                    bp.set(x, -1, z, BR);
                    bp.foundation(x, z);
                } else {
                    bp.set(x, 0, z, Blueprint.stairs(STAIR, Blueprint.outward(x, z).getOpposite()));
                    bp.set(x, -1, z, BR);
                    bp.foundation(x, z);
                }
            }
        // courtyard inlay: ring + eight rays tipped with gold
        bp.ring(0, 0, 0, 10.0, 10.9, Palette.of(CH));
        for (int k = 0; k < 8; k++) {
            double a = k * Math.PI / 4;
            for (double d = 11; d <= 18; d += 0.5) bp.set((int) Math.round(Math.cos(a) * d), 0, (int) Math.round(Math.sin(a) * d), CH);
            bp.set((int) Math.round(Math.cos(a) * 18.5), 0, (int) Math.round(Math.sin(a) * 18.5), s(Blocks.GOLD_BLOCK));
        }
        // entrance path & lamp posts (south)
        bp.fill(-1, 0, 10, 1, 0, 20, CH);
        for (int sx : new int[]{-3, 3}) {
            bp.fill(sx, 1, 16, sx, 3, 16, BR);
            bp.set(sx, 4, 16, s(Blocks.LANTERN));
        }
        // colonnade of (partly ruined) pillars
        int[] heights = new int[12];
        for (int k = 0; k < 12; k++) {
            double a = k * Math.PI / 6 + Math.PI / 12;
            int px = (int) Math.round(Math.cos(a) * 16), pz = (int) Math.round(Math.sin(a) * 16);
            boolean broken = r.nextFloat() < 0.35f;
            int h = broken ? 2 + r.nextInt(3) : 8;
            heights[k] = h;
            for (int y = 1; y <= h; y++) bp.set(px, y, pz, y == h && broken ? CR : (y == 1 || y == h ? CH : wall.pick(r)));
            if (!broken) bp.set(px, h + 1, pz, s(Blocks.LANTERN));
            if (broken) {
                double t = a + Math.PI / 2;
                int len = 3 + r.nextInt(3);
                for (int i = 1; i <= len; i++) bp.set((int) Math.round(px + Math.cos(t) * i), 1, (int) Math.round(pz + Math.sin(t) * i), i % 2 == 0 ? CR : BR);
            }
        }
        for (int k = 0; k < 12; k++) {
            int n = (k + 1) % 12;
            if (heights[k] == 8 && heights[n] == 8) {
                double a1 = k * Math.PI / 6 + Math.PI / 12, a2 = n * Math.PI / 6 + Math.PI / 12;
                bp.line(Math.cos(a1) * 16, 9, Math.sin(a1) * 16, Math.cos(a2) * 16, 9, Math.sin(a2) * 16, 0, Palette.of(SLAB));
            }
        }

        // ------------------------------------------------ main tower
        for (int y = 1; y <= 21; y++) {
            bp.disk(0, y, 0, 8.4, Palette.of(s(Blocks.AIR)));
            bp.ring(0, y, 0, 8.5, 9.6, wall);
        }
        bp.disk(0, 7, 0, 8.6, floor);
        bp.disk(0, 14, 0, 8.6, floor);
        bp.ring(0, 6, 0, 8.5, 9.6, Palette.of(CH));
        bp.ring(0, 13, 0, 8.5, 9.6, Palette.of(CH));
        // windows
        int[][] windowRows = {{2, 4}, {9, 11}, {16, 19}};
        for (int[] rows : windowRows) {
            for (int k = 0; k < 8; k++) {
                double a = k * Math.PI / 4 + Math.PI / 8;
                for (double off = -0.12; off <= 0.12; off += 0.12) {
                    int wx = (int) Math.round(Math.cos(a + off) * 9), wz = (int) Math.round(Math.sin(a + off) * 9);
                    for (int y = rows[0]; y <= rows[1]; y++) bp.set(wx, y, wz, GL);
                }
            }
        }
        // doorway (south)
        bp.fillAir(-1, 1, 8, 1, 4, 10);
        bp.fill(-2, 1, 9, -2, 5, 9, CH);
        bp.fill(2, 1, 9, 2, 5, 9, CH);
        bp.fill(-2, 5, 9, 2, 5, 9, CH);

        // spiral staircases along the wall
        stairRun(bp, STAIR, BR, 0, 2.3, 7);
        stairRun(bp, STAIR, BR, 7, 2.3 + Math.PI, 7);

        // ------------------------------------------------ floor 1: entrance hall
        bp.disk(0, 0, 0, 2.6, Palette.of(CH));
        bp.set(0, 0, 0, s(Blocks.GOLD_BLOCK));
        for (int k = 0; k < 4; k++) {
            double a = k * Math.PI / 2 + Math.PI / 4;
            for (double d = 3; d <= 6; d += 0.5) bp.set((int) Math.round(Math.cos(a) * d), 0, (int) Math.round(Math.sin(a) * d), CH);
            int px = (int) Math.round(Math.cos(a) * 5), pz = (int) Math.round(Math.sin(a) * 5);
            bp.fill(px, 1, pz, px, 6, pz, CH);
        }
        bp.set(3, 6, 0, hangingLantern());
        bp.set(-3, 6, 0, hangingLantern());
        bp.set(0, 6, 3, hangingLantern());
        bookshelfArc(bp, 1, 3, Math.toRadians(200), Math.toRadians(240));
        bookshelfArc(bp, 1, 3, Math.toRadians(300), Math.toRadians(340));
        bp.chest(6, 1, 3, Direction.WEST, OBSERVATORY_COMMON);
        bp.chest(-6, 1, 3, Direction.EAST, OBSERVATORY_COMMON);
        bp.spawner(-6, 1, -3, ModEntities.VOID_STALKER);
        // the Star Lock and the sealed floor over the vault stairs
        bp.set(0, 2, -9, s(ModBlocks.STAR_LOCK.get()));
        bp.set(-1, 2, -9, CH);
        bp.set(1, 2, -9, CH);
        bp.set(0, 1, -9, CH);
        bp.set(0, 3, -9, CH);
        bp.fill(-1, 0, -7, 0, 0, -4, SEALED);

        // ------------------------------------------------ vault (secret, underground)
        for (int k = 0; k <= 7; k++) {
            int z = -4 - k, y = -1 - k;
            bp.fill(-1, y, z, 0, y, z, Blueprint.stairs(STAIR, Direction.SOUTH));
            bp.fill(-1, y - 1, z, 0, y - 1, z, BR);
            int top = Math.min(-1, y + 3);
            if (top >= y + 1) bp.fillAir(-1, y + 1, z, 0, top, z);
            bp.fill(-2, y - 1, z, -2, top + 1, z, BR);
            bp.fill(1, y - 1, z, 1, top + 1, z, BR);
            if (y + 4 < 0) bp.fill(-1, y + 4, z, 0, y + 4, z, BR);
        }
        bp.fill(-7, -10, -23, 7, -2, -11, BR);
        bp.fillAir(-6, -8, -22, 6, -3, -12);
        bp.fill(-6, -9, -22, 6, -9, -12, BR);
        bp.fillAir(-1, -8, -11, 0, -6, -11);
        bp.ring(0, -9, -17, 3.4, 4.2, Palette.of(CH));
        for (int k = 0; k < 4; k++) {
            double a = k * Math.PI / 2;
            for (double d = 0; d <= 3; d += 0.5) bp.set((int) Math.round(Math.cos(a) * d), -9, -17 + (int) Math.round(Math.sin(a) * d), s(Blocks.GOLD_BLOCK));
        }
        for (int[] c : new int[][]{{-6, -22}, {6, -22}, {-6, -12}, {6, -12}}) bp.fill(c[0], -8, c[1], c[0], -3, c[1], CH);
        bp.set(0, -8, -17, SM);
        bp.set(0, -7, -17, s(ModBlocks.STAR_JAR.get()));
        bp.set(0, -8, -21, CH);
        bp.set(0, -7, -21, s(ModBlocks.FALLEN_STAR.get()));
        bp.chest(-4, -8, -21, Direction.SOUTH, OBSERVATORY_VAULT);
        bp.chest(4, -8, -21, Direction.SOUTH, OBSERVATORY_VAULT);
        bp.set(-4, -3, -17, hangingLantern());
        bp.set(4, -3, -17, hangingLantern());
        bp.fill(-6, -8, -20, -6, -6, -14, s(Blocks.BOOKSHELF));
        bp.fill(6, -8, -20, 6, -6, -14, s(Blocks.BOOKSHELF));
        bp.set(-1, -9, -13, s(ModBlocks.GRAVITY_RUNE.get()));
        bp.set(0, -9, -14, s(ModBlocks.GRAVITY_RUNE.get()));
        bp.mob(-4, -8, -14, ModEntities.VOID_STALKER);
        bp.mob(4, -8, -14, ModEntities.VOID_STALKER);

        // ------------------------------------------------ floor 2: the archive
        bookshelfArc(bp, 8, 10, Math.toRadians(20), Math.toRadians(110));
        bookshelfArc(bp, 8, 10, Math.toRadians(160), Math.toRadians(250));
        bookshelfArc(bp, 8, 10, Math.toRadians(290), Math.toRadians(340));
        bp.chest(5, 8, -4, Direction.WEST, OBSERVATORY_LIBRARY);
        bp.chest(-5, 8, 4, Direction.EAST, OBSERVATORY_LIBRARY);
        bp.set(0, 7, 0, CH);
        bp.spawner(0, 8, 0, ModEntities.VOID_GAZER);
        for (int i = 0; i < 4; i++) {
            double a = r.nextDouble() * Math.PI * 2;
            bp.set((int) Math.round(Math.cos(a) * 4), 7, (int) Math.round(Math.sin(a) * 4), s(ModBlocks.GRAVITY_RUNE.get()));
        }
        for (int i = 0; i < 8; i++) {
            double a = r.nextDouble() * Math.PI * 2;
            bp.set((int) Math.round(Math.cos(a) * 7.5), 12 + r.nextInt(2), (int) Math.round(Math.sin(a) * 7.5), s(Blocks.COBWEB));
        }
        bp.set(3, 13, 0, hangingLantern());
        bp.set(-3, 13, 0, hangingLantern());

        // ------------------------------------------------ floor 3: telescope chamber
        bp.ring(0, 14, 0, 1.6, 2.6, Palette.of(CH));
        bp.set(0, 15, 0, s(ModBlocks.ASTRAL_ALTAR.get()));
        for (int k = 0; k < 4; k++) {
            double a = k * Math.PI / 2 + Math.PI / 4;
            bp.set((int) Math.round(Math.cos(a) * 3.5), 15, (int) Math.round(Math.sin(a) * 3.5), s(ModBlocks.STAR_JAR.get()));
            bp.set((int) Math.round(Math.cos(a + 0.4) * 6.5), 14, (int) Math.round(Math.sin(a + 0.4) * 6.5), s(ModBlocks.STARFIRE_VENT.get()));
        }
        // dome with ribs, cracked open by the old impact
        bp.dome(0, 21, 0, 9.6, 1.1, dome);
        for (int k = 0; k < 8; k++) {
            double a = k * Math.PI / 4;
            for (double phi = 0; phi <= Math.PI / 2; phi += 0.05) {
                bp.set((int) Math.round(Math.cos(phi) * Math.cos(a) * 9.1), 21 + (int) Math.round(Math.sin(phi) * 9.1), (int) Math.round(Math.cos(phi) * Math.sin(a) * 9.1), CH);
            }
        }
        bp.set(0, 31, 0, s(Blocks.GOLD_BLOCK));
        bp.set(0, 32, 0, s(Blocks.END_ROD));
        // the great telescope
        bp.fill(-3, 15, 3, -3, 16, 3, s(Blocks.GOLD_BLOCK));
        bp.line(-2.5, 17.5, 2.5, 5.0, 27.0, -5.0, 1.15, new Palette().add(SM, 5).add(s(Blocks.GOLD_BLOCK), 1));
        bp.line(5.0, 27.0, -5.0, 6.2, 28.5, -6.2, 1.5, Palette.of(GL));
        bp.set(-4, 16, 4, s(ModBlocks.TELESCOPE_EYEPIECE.get()));
        // shattering: missing dome glass and a breach on the east side
        for (var it = bp.blocks.long2ObjectEntrySet().iterator(); it.hasNext(); ) {
            var e = it.next();
            long key = e.getLongKey();
            int x = net.minecraft.core.BlockPos.getX(key), y = net.minecraft.core.BlockPos.getY(key), z = net.minecraft.core.BlockPos.getZ(key);
            BlockState st = e.getValue();
            double d = Math.sqrt(x * x + z * z);
            if (st.is(ModBlocks.ASTRAL_GLASS.get()) && y >= 21 && r.nextFloat() < (x > 3 ? 0.55f : 0.2f)) e.setValue(s(Blocks.AIR));
            else if (y >= 12 && y <= 21 && d >= 8.5 && d <= 9.7 && x > 6 && Math.abs(z) < 5 && r.nextFloat() < 0.7f && !st.isAir()) e.setValue(s(Blocks.AIR));
            else if (y >= 17 && y <= 21 && d >= 8.5 && d <= 9.7 && r.nextFloat() < 0.15f && !st.isAir()) e.setValue(s(Blocks.AIR));
        }
        // the meteorite that did it, and the rubble
        int mx = 14, mz = 5;
        for (int dx = -3; dx <= 3; dx++)
            for (int dz = -3; dz <= 3; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d > 3.3) continue;
                bp.set(mx + dx, 0, mz + dz, d < 1.6 ? s(Blocks.MAGMA_BLOCK) : s(ModBlocks.COOLED_METEORITE.get()));
            }
        bp.fill(mx - 1, 1, mz - 1, mx, 1, mz, s(ModBlocks.COOLED_METEORITE.get()));
        bp.set(mx, 1, mz, s(ModBlocks.STARMETAL_ORE.get()));
        bp.set(mx - 1, 1, mz - 1, s(ModBlocks.STARMETAL_ORE.get()));
        bp.set(mx, 2, mz, s(ModBlocks.SKYSHARD_CLUSTER.get()));
        bp.set(mx - 1, 2, mz, s(ModBlocks.SKYSHARD_CLUSTER.get()));
        for (int i = 0; i < 14; i++) {
            int x = 10 + r.nextInt(8), z = -6 + r.nextInt(12);
            if (Math.sqrt(x * x + z * z) > 19) continue;
            bp.set(x, 1, z, r.nextBoolean() ? CR : GL);
            if (r.nextInt(3) == 0) bp.set(x, 2, z, CR);
        }
    }

    private static void stairRun(Blueprint bp, BlockState stair, BlockState support, int baseY, double startAngle, int steps) {
        double stepAngle = 0.24;
        for (int i = 1; i <= steps; i++) {
            double a = startAngle + i * stepAngle;
            Direction facing = tangent(a);
            for (double rad : new double[]{7.3, 6.3}) {
                int x = (int) Math.round(Math.cos(a) * rad), z = (int) Math.round(Math.sin(a) * rad);
                int y = baseY + i;
                if (i == steps) {
                    bp.set(x, y, z, support);
                } else {
                    bp.set(x, y, z, Blueprint.stairs(stair, facing));
                    for (int yy = baseY + 1; yy < y; yy++) bp.set(x, yy, z, support);
                    for (int h = 1; h <= 3; h++) bp.air(x, y + h, z);
                }
            }
        }
        // opening in the floor above the upper half of the run
        for (int i = steps / 2; i <= steps; i++) {
            double a = startAngle + i * stepAngle;
            for (double rad = 5.6; rad <= 8.2; rad += 0.5) {
                bp.air((int) Math.round(Math.cos(a) * rad), baseY + 7, (int) Math.round(Math.sin(a) * rad));
            }
        }
    }

    private static void bookshelfArc(Blueprint bp, int y1, int y2, double a1, double a2) {
        for (double a = a1; a <= a2; a += 0.06) {
            int x = (int) Math.round(Math.cos(a) * 8.1), z = (int) Math.round(Math.sin(a) * 8.1);
            for (int y = y1; y <= y2; y++) bp.set(x, y, z, s(Blocks.BOOKSHELF));
        }
    }

    // ================================================================== FALLEN VESSEL
    private static void vessel(Blueprint bp) {
        RandomSource r = bp.random;
        BlockState MB = s(ModBlocks.METEORITE_BRICKS.get());
        BlockState VS = s(ModBlocks.VOID_STONE.get());
        BlockState CM = s(ModBlocks.COOLED_METEORITE.get());
        BlockState GL = s(ModBlocks.ASTRAL_GLASS.get());
        BlockState SK = s(ModBlocks.SKYSHARD_BLOCK.get());
        BlockState SM = s(ModBlocks.STARMETAL_BLOCK.get());
        Palette hull = new Palette().add(MB, 6).add(VS, 3).add(CM, 2);
        double pitch = -0.26;
        // trench where it slid in
        for (int x = -34; x <= -12; x++)
            for (int z = -3; z <= 3; z++) {
                int depth = Math.abs(z) <= 1 ? 2 : 1;
                for (int y = 3 - depth; y <= 6; y++) bp.air(x, y, z);
                bp.set(x, 2 - depth, z, r.nextInt(4) == 0 ? CM : s(Blocks.COARSE_DIRT));
                if (r.nextInt(12) == 0) bp.set(x, 3 - depth, z, s(Blocks.FIRE));
            }
        for (int u = -14; u <= 14; u++)
            for (int v = -5; v <= 5; v++)
                for (int w = -6; w <= 6; w++) {
                    double outer = sq(u / 13.5) + sq(v / 3.8) + sq(w / 4.8);
                    if (outer > 1.0) continue;
                    double inner = sq(u / 12.2) + sq(v / 2.7) + sq(w / 3.6);
                    int x = u, y = (int) Math.round(v + u * pitch) + 2, z = w;
                    if (inner <= 1.0) {
                        bp.set(x, y, z, v == -2 ? VS : s(Blocks.AIR));
                        if (v < -2) bp.set(x, y, z, VS);
                    } else {
                        BlockState st = hull.pick(r);
                        if (Math.abs(w) >= 3 && v == 0 && Math.floorMod(u, 4) == 0) st = GL;
                        if (v >= 3 && Math.floorMod(u, 6) == 3 && Math.abs(w) <= 1) st = SK;
                        bp.set(x, y, z, st);
                    }
                }
        // breach in the starboard side
        for (int u = -4; u <= 1; u++)
            for (int v = -1; v <= 2; v++)
                for (int w = 2; w <= 6; w++) bp.air(u, (int) Math.round(v + u * pitch) + 2, w);
        for (int i = 0; i < 16; i++) {
            int x = -8 + r.nextInt(14), z = 6 + r.nextInt(6);
            bp.set(x, 1 + r.nextInt(2), z, r.nextInt(4) == 0 ? GL : hull.pick(r));
        }
        // fins
        for (int u = -9; u <= -2; u++) {
            int span = (u + 10) / 2;
            for (int w = 5; w <= 5 + span; w++) {
                int y = (int) Math.round(u * pitch) + 2;
                bp.set(u, y, w, MB);
                bp.set(u, y, -w, MB);
            }
        }
        // thrusters, still glowing
        for (int side : new int[]{-2, 2}) {
            bp.line(-15.5, 2 + -15.5 * pitch + 0.5, side, -12.5, 2 + -12.5 * pitch + 0.5, side, 1.2, Palette.of(SM));
            bp.set(-16, (int) Math.round(2 + -16 * pitch + 0.5), side, s(Blocks.MAGMA_BLOCK));
        }
        // interior: reactor at the nose, bridge at the stern
        int fy = (int) Math.round(-2 + 7 * pitch) + 2;
        bp.fill(7, fy + 1, -1, 8, fy + 2, 0, SK);
        bp.set(6, fy + 1, 1, GL);
        bp.set(9, fy + 1, -2, GL);
        bp.chest(5, fy + 1, 2, Direction.WEST, FALLEN_VESSEL);
        int by = (int) Math.round(-2 + -8 * pitch) + 2;
        bp.chest(-8, by + 1, -2, Direction.EAST, FALLEN_VESSEL);
        bp.set(-9, by + 1, 1, s(ModBlocks.STAR_JAR.get()));
        bp.set(-10, by + 1, 0, Blueprint.stairs(s(ModBlocks.ASTRAL_BRICK_STAIRS.get()), Direction.WEST));
        int my = (int) Math.round(-2 + 2 * pitch) + 2;
        bp.spawner(2, my + 1, -2, ModEntities.METEORITE_CRAWLER);
        bp.set(-4, (int) Math.round(-2 + -4 * pitch) + 2, 0, s(ModBlocks.GRAVITY_RUNE.get()));
        bp.set(3, (int) Math.round(-2 + 3 * pitch) + 2, 0, s(ModBlocks.STARFIRE_VENT.get()));
        bp.mob(0, my + 1, 1, ModEntities.METEORITE_CRAWLER);
    }

    private static double sq(double v) {
        return v * v;
    }

    // ================================================================== SKY SHRINE
    private static void shrine(Blueprint bp) {
        RandomSource r = bp.random;
        BlockState BR = s(ModBlocks.ASTRAL_BRICKS.get());
        BlockState CH = s(ModBlocks.CHISELED_ASTRAL_BRICKS.get());
        BlockState GL = s(ModBlocks.ASTRAL_GLASS.get());
        Palette rock = new Palette().add(s(Blocks.STONE), 6).add(s(ModBlocks.COOLED_METEORITE.get()), 3).add(s(ModBlocks.STARMETAL_ORE.get()), 1);
        double[] wobble = new double[16];
        for (int i = 0; i < 16; i++) wobble[i] = r.nextDouble() * 1.4 - 0.5;
        for (int y = 0; y >= -10; y--) {
            double base = 8.5 * (1 - Math.pow(-y / 10.5, 1.4));
            for (int x = -10; x <= 10; x++)
                for (int z = -10; z <= 10; z++) {
                    double ang = Math.atan2(z, x);
                    int wi = (int) Math.floor((ang + Math.PI) / (Math.PI * 2) * 16) % 16;
                    double rad = base + wobble[wi];
                    if (x * x + z * z > rad * rad) continue;
                    BlockState st = y == 0 ? s(Blocks.GRASS_BLOCK) : y >= -2 ? s(Blocks.DIRT) : rock.pick(r);
                    bp.set(x, y, z, st);
                }
        }
        // hanging crystals beneath
        for (int i = 0; i < 10; i++) {
            int x = r.nextInt(9) - 4, z = r.nextInt(9) - 4;
            int y = -1;
            while (bp.has(x, y - 1, z) && y > -12) y--;
            bp.set(x, y - 1, z, s(ModBlocks.SKYSHARD_BLOCK.get()));
            if (r.nextBoolean()) bp.set(x, y - 2, z, s(ModBlocks.SKYSHARD_BLOCK.get()));
        }
        // flowers and grass
        BlockState[] plants = {s(Blocks.SHORT_GRASS), s(Blocks.CORNFLOWER), s(Blocks.ALLIUM), s(Blocks.OXEYE_DAISY), s(Blocks.SHORT_GRASS)};
        for (int i = 0; i < 26; i++) {
            int x = r.nextInt(15) - 7, z = r.nextInt(15) - 7;
            if (x * x + z * z < 20 || !bp.has(x, 0, z)) continue;
            bp.set(x, 1, z, plants[r.nextInt(plants.length)]);
        }
        // shrine
        bp.disk(0, 0, 0, 3.6, Palette.of(BR));
        bp.set(0, 0, 0, CH);
        for (int k = 0; k < 6; k++) {
            double a = k * Math.PI / 3;
            int px = (int) Math.round(Math.cos(a) * 4.6), pz = (int) Math.round(Math.sin(a) * 4.6);
            bp.fill(px, 0, pz, px, 5, pz, CH);
            if (k % 2 == 0) bp.set(px, 6, pz, s(ModBlocks.STAR_JAR.get()));
            double a2 = (k + 1) * Math.PI / 3;
            bp.line(Math.cos(a) * 4.6, 5, Math.sin(a) * 4.6, Math.cos(a2) * 4.6, 5, Math.sin(a2) * 4.6, 0, Palette.of(BR));
        }
        bp.set(0, 1, 0, CH);
        bp.chest(0, 2, 0, Direction.SOUTH, SKY_SHRINE);
        // floating stepping stones spiralling down
        for (int i = 0; i < 14; i++) {
            double a = i * 0.55;
            double rad = 10 + i * 0.25;
            bp.set((int) Math.round(Math.cos(a) * rad), -3 - i * 2, (int) Math.round(Math.sin(a) * rad), GL);
        }
        for (int i = 0; i < 3; i++) bp.mob(r.nextInt(5) - 2, 3, r.nextInt(5) - 2, ModEntities.ASTRAL_WISP);
    }

    // ================================================================== CRATER (command showcase)
    private static void crater(Blueprint bp) {
        RandomSource r = bp.random;
        int rad = 6;
        for (int x = -rad; x <= rad; x++)
            for (int z = -rad; z <= rad; z++) {
                double d = Math.sqrt(x * x + z * z);
                if (d > rad + 0.3) continue;
                int depth = (int) Math.round(Math.sqrt(Math.max(0, rad * rad - d * d)) * 0.55);
                for (int y = -depth + 1; y <= 4; y++) bp.air(x, y, z);
                double hot = 1 - d / rad;
                BlockState lining = hot > 0.5 && r.nextBoolean() ? s(ModBlocks.METEORITE_ROCK.get()) : hot > 0.4 && r.nextBoolean() ? s(Blocks.MAGMA_BLOCK) : s(ModBlocks.COOLED_METEORITE.get());
                bp.set(x, -depth, z, lining);
            }
        int floor = -(int) Math.round(rad * 0.55) + 1;
        bp.fill(-1, floor, -1, 1, floor, 1, s(ModBlocks.METEORITE_ROCK.get()));
        bp.set(0, floor, 0, s(ModBlocks.STARMETAL_ORE.get()));
        bp.set(1, floor, 0, s(ModBlocks.STARMETAL_ORE.get()));
        bp.set(0, floor + 1, 0, s(ModBlocks.FALLEN_STAR.get()));
        bp.set(-1, floor + 1, 1, s(ModBlocks.SKYSHARD_CLUSTER.get()));
    }
}
