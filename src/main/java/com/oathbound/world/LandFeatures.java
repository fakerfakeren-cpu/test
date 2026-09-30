package com.oathbound.world;

import com.mojang.serialization.Codec;
import com.oathbound.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * The land remembers the Order: waystones along forgotten roads, the broken halls of Lanternguard outposts, glades
 * where glimmer moss lights the forest floor, moss-grown boulders, and lumenite crystals glowing in the dark below.
 */
public final class LandFeatures {
    private LandFeatures() {}

    private static boolean soil(BlockState s) {
        return s.is(BlockTags.DIRT) || s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.MOSS_BLOCK) || s.is(Blocks.SNOW_BLOCK)
            || s.is(Blocks.STONE) || s.is(Blocks.GRAVEL) || s.is(Blocks.COARSE_DIRT) || s.is(Blocks.SAND);
    }

    private static boolean open(BlockState s) {
        return s.isAir() || s.canBeReplaced();
    }

    /** The ground block under a column (x, z), or null over water or where the surface is not soil. */
    private static BlockPos ground(WorldGenLevel level, int x, int z) {
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z) - 1;
        BlockPos p = new BlockPos(x, y, z);
        BlockState s = level.getBlockState(p);
        while (y > level.getMinY() && (s.canBeReplaced() || s.is(BlockTags.LEAVES) || s.is(BlockTags.LOGS)) && !s.getFluidState().isSource()) {
            p = p.below();
            s = level.getBlockState(p);
            y--;
        }
        return soil(s) ? p : null;
    }

    private static void set(WorldGenLevel level, BlockPos p, BlockState s) {
        level.setBlock(p, s, 2);
    }

    // ------------------------------------------------------------------ waystone
    /** A carved runestone marker: a plinth, a shaft and a glyphed cap, with wildflowers at its foot. */
    public static class Waystone extends Feature<NoneFeatureConfiguration> {
        public Waystone(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            BlockPos g = ground(level, ctx.origin().getX(), ctx.origin().getZ());
            if (g == null || !open(level.getBlockState(g.above()))) return false;
            set(level, g, ModBlocks.RUNESTONE_BRICKS.get().defaultBlockState());
            int h = 1 + r.nextInt(2);
            for (int i = 1; i <= h; i++) set(level, g.above(i), ModBlocks.RUNESTONE.get().defaultBlockState());
            set(level, g.above(h + 1), ModBlocks.GLYPHED_RUNESTONE.get().defaultBlockState());
            if (r.nextBoolean()) set(level, g.above(h + 2), Blocks.MOSS_CARPET.defaultBlockState());
            BlockState[] foot = {ModBlocks.GLIMMER_MOSS.get().defaultBlockState(), ModBlocks.MOONPETAL.get().defaultBlockState(),
                ModBlocks.DUSK_LILY.get().defaultBlockState(), Blocks.SHORT_GRASS.defaultBlockState()};
            for (Direction d : Direction.Plane.HORIZONTAL) {
                if (r.nextFloat() > 0.55f) continue;
                BlockPos f = ground(level, g.getX() + d.getStepX(), g.getZ() + d.getStepZ());
                if (f != null && f.getY() == g.getY() && level.getBlockState(f).is(Blocks.GRASS_BLOCK) && open(level.getBlockState(f.above())))
                    set(level, f.above(), foot[r.nextInt(foot.length)]);
            }
            return true;
        }
    }

    // ------------------------------------------------------------------ Lanternguard ruin
    /**
     * What is left of a Lanternguard outpost: a cracked wardstone floor, a ring of broken pillars, one fallen across
     * the grass, and sometimes an old lantern still hanging on.
     */
    public static class OrderRuin extends Feature<NoneFeatureConfiguration> {
        public OrderRuin(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            BlockPos c = ground(level, ctx.origin().getX(), ctx.origin().getZ());
            if (c == null) return false;
            BlockState[] floor = {ModBlocks.WARDSTONE_BRICKS.get().defaultBlockState(), ModBlocks.MOSSY_WARDSTONE_BRICKS.get().defaultBlockState(),
                ModBlocks.CRACKED_WARDSTONE_BRICKS.get().defaultBlockState(), ModBlocks.WARDSTONE_TILES.get().defaultBlockState()};
            // the floor follows the ground, but only where the ground is near the centre's height
            for (int dx = -3; dx <= 3; dx++)
                for (int dz = -3; dz <= 3; dz++) {
                    if (r.nextFloat() > 0.6f) continue;
                    BlockPos g = ground(level, c.getX() + dx, c.getZ() + dz);
                    if (g != null && Math.abs(g.getY() - c.getY()) <= 1) set(level, g, floor[r.nextInt(floor.length)]);
                }
            // four broken pillars
            BlockState pillar = ModBlocks.WARDSTONE_PILLAR.get().defaultBlockState();
            boolean lantern = r.nextInt(3) == 0;
            for (int[] k : new int[][]{{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) {
                if (r.nextFloat() < 0.2f) continue;
                BlockPos g = ground(level, c.getX() + k[0], c.getZ() + k[1]);
                if (g == null || Math.abs(g.getY() - c.getY()) > 2) continue;
                int h = 1 + r.nextInt(4);
                for (int i = 1; i <= h; i++) set(level, g.above(i), pillar);
                BlockPos top = g.above(h + 1);
                if (lantern && h >= 3) {
                    set(level, top, ModBlocks.OATHSTEEL_LANTERN.get().defaultBlockState());
                    lantern = false;
                } else if (r.nextBoolean()) set(level, top, Blocks.MOSS_CARPET.defaultBlockState());
            }
            // one fallen across the grass
            Direction.Axis axis = r.nextBoolean() ? Direction.Axis.X : Direction.Axis.Z;
            int len = 3 + r.nextInt(2), off = r.nextInt(3) - 1;
            for (int i = 0; i < len; i++) {
                int x = c.getX() + (axis == Direction.Axis.X ? i - 1 : off + 5), z = c.getZ() + (axis == Direction.Axis.Z ? i - 1 : off + 5);
                BlockPos g = ground(level, x, z);
                if (g != null && open(level.getBlockState(g.above()))) set(level, g.above(), pillar.setValue(RotatedPillarBlock.AXIS, axis));
            }
            // a chiselled threshold stone
            if (open(level.getBlockState(c.above()))) set(level, c, ModBlocks.CHISELED_WARDSTONE.get().defaultBlockState());
            return true;
        }
    }

    // ------------------------------------------------------------------ glimmer glade
    /** A patch of forest floor lit with glimmer moss, moonpetals and ferns. */
    public static class GlimmerGlade extends Feature<NoneFeatureConfiguration> {
        public GlimmerGlade(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            int placed = 0;
            for (int i = 0; i < 40; i++) {
                int x = ctx.origin().getX() + r.nextInt(13) - 6, z = ctx.origin().getZ() + r.nextInt(13) - 6;
                BlockPos g = ground(level, x, z);
                if (g == null) continue;
                BlockState s = level.getBlockState(g);
                if (!(s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.PODZOL) || s.is(Blocks.MOSS_BLOCK))) continue;
                if (!level.getBlockState(g.above()).isAir()) continue;
                float k = r.nextFloat();
                BlockState put = k < 0.6f ? ModBlocks.GLIMMER_MOSS.get().defaultBlockState()
                    : k < 0.8f ? ModBlocks.MOONPETAL.get().defaultBlockState() : Blocks.FERN.defaultBlockState();
                set(level, g.above(), put);
                if (k < 0.3f) set(level, g, Blocks.MOSS_BLOCK.defaultBlockState());
                placed++;
            }
            return placed > 0;
        }
    }

    // ------------------------------------------------------------------ mossy boulder
    /** A half-buried boulder of mossy cobble, streaked with runestone, furred with moss. */
    public static class MossyBoulder extends Feature<NoneFeatureConfiguration> {
        public MossyBoulder(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            BlockPos c = ground(level, ctx.origin().getX(), ctx.origin().getZ());
            if (c == null) return false;
            double rx = 1.4 + r.nextDouble() * 1.4, ry = 1.1 + r.nextDouble() * 1.2, rz = 1.4 + r.nextDouble() * 1.4;
            int R = (int) Math.ceil(Math.max(rx, rz));
            for (int dx = -R; dx <= R; dx++)
                for (int dy = -1; dy <= (int) Math.ceil(ry); dy++)
                    for (int dz = -R; dz <= R; dz++) {
                        double d = dx * dx / (rx * rx) + dy * dy / (ry * ry) + dz * dz / (rz * rz);
                        if (d > 1.0) continue;
                        float k = r.nextFloat();
                        BlockState s = k < 0.5f ? Blocks.MOSSY_COBBLESTONE.defaultBlockState() : k < 0.75f ? Blocks.COBBLESTONE.defaultBlockState()
                            : k < 0.9f ? Blocks.MOSS_BLOCK.defaultBlockState() : ModBlocks.RUNESTONE.get().defaultBlockState();
                        set(level, c.offset(dx, dy, dz), s);
                    }
            for (int dx = -R; dx <= R; dx++)
                for (int dz = -R; dz <= R; dz++) {
                    if (r.nextFloat() > 0.45f) continue;
                    BlockPos top = c.offset(dx, (int) Math.ceil(ry), dz);
                    for (int i = 0; i < 4 && !level.getBlockState(top).isAir(); i++) top = top.above();
                    if (level.getBlockState(top).isAir() && !level.getBlockState(top.below()).isAir() && level.getBlockState(top.below()).isSolid())
                        set(level, top, Blocks.MOSS_CARPET.defaultBlockState());
                }
            return true;
        }
    }

    // ------------------------------------------------------------------ lumenite clusters
    /** Clusters of lumenite crystal growing from cave walls, each rooted in a seam of ore. */
    public static class LumenClusters extends Feature<NoneFeatureConfiguration> {
        public LumenClusters(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            BlockState cluster = ModBlocks.LUMENITE_CLUSTER.get().defaultBlockState();
            int placed = 0;
            for (int i = 0; i < 48 && placed < 5; i++) {
                BlockPos p = ctx.origin().offset(r.nextInt(13) - 6, r.nextInt(9) - 4, r.nextInt(13) - 6);
                if (!level.getBlockState(p).isAir()) continue;
                for (Direction d : Direction.values()) {
                    BlockPos wall = p.relative(d);
                    BlockState w = level.getBlockState(wall);
                    if (!w.is(BlockTags.BASE_STONE_OVERWORLD)) continue;
                    set(level, p, cluster.setValue(AmethystClusterBlock.FACING, d.getOpposite()));
                    if (r.nextFloat() < 0.35f)
                        set(level, wall, (w.is(Blocks.DEEPSLATE) ? ModBlocks.DEEPSLATE_LUMENITE_ORE : ModBlocks.LUMENITE_ORE).get().defaultBlockState());
                    placed++;
                    break;
                }
            }
            return placed > 0;
        }
    }
}
