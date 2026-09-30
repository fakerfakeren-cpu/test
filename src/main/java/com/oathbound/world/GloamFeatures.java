package com.oathbound.world;

import com.mojang.serialization.Codec;
import com.oathbound.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Decoration for the Gloaming's floating islands. */
public final class GloamFeatures {
    private GloamFeatures() {}

    private static boolean ground(WorldGenLevel level, BlockPos pos) {
        BlockState below = level.getBlockState(pos.below());
        return (below.is(ModBlocks.GLOAM_MOSS.get()) || below.is(ModBlocks.GLOAMSTONE.get())) && level.getBlockState(pos).isAir();
    }

    private static void set(WorldGenLevel level, BlockPos p, BlockState s) {
        BlockState cur = level.getBlockState(p);
        if (cur.isAir() || cur.canBeReplaced() || cur.is(ModBlocks.VEILBLOOM.get())) level.setBlock(p, s, 2);
    }

    /**
     * A gloamwood: a trunk that leans and splits into crooked boughs crowned with glowing violet leaves
     * and hung with gloam lanterns. Every tree is different.
     */
    public static class Tree extends Feature<NoneFeatureConfiguration> {
        public Tree(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            BlockPos base = ctx.origin();
            if (!ground(level, base)) return false;
            BlockState log = ModBlocks.GLOAMWOOD_LOG.get().defaultBlockState();
            int height = 5 + r.nextInt(5);
            double lx = (r.nextDouble() - 0.5) * 0.5, lz = (r.nextDouble() - 0.5) * 0.5;
            double x = 0, z = 0;
            BlockPos top = base;
            for (int y = 0; y < height; y++) {
                x += lx;
                z += lz;
                top = base.offset((int) Math.round(x), y, (int) Math.round(z));
                set(level, top, log);
            }
            // two to four crooked boughs
            int boughs = 2 + r.nextInt(3);
            for (int b = 0; b < boughs; b++) {
                double a = r.nextDouble() * Math.PI * 2;
                Direction.Axis axis = Math.abs(Math.cos(a)) > Math.abs(Math.sin(a)) ? Direction.Axis.X : Direction.Axis.Z;
                BlockPos p = top.below(r.nextInt(2));
                int len = 2 + r.nextInt(3);
                for (int i = 1; i <= len; i++) {
                    p = p.offset((int) Math.round(Math.cos(a)), r.nextInt(3) == 0 ? 1 : 0, (int) Math.round(Math.sin(a)));
                    set(level, p, log.setValue(RotatedPillarBlock.AXIS, i == len ? Direction.Axis.Y : axis));
                }
                canopy(level, r, p);
                if (r.nextInt(3) == 0) set(level, p.below(), ModBlocks.GLOAM_LANTERN.get().defaultBlockState()
                    .setValue(net.minecraft.world.level.block.LanternBlock.HANGING, true));
            }
            canopy(level, r, top);
            // roots
            for (Direction d : Direction.Plane.HORIZONTAL) {
                if (r.nextInt(2) == 0) set(level, base.relative(d), log.setValue(RotatedPillarBlock.AXIS, d.getAxis()));
            }
            return true;
        }
    }

    /** A loose, glowing crown of gloamwood leaves over a bough's end, never below it (lanterns hang there). */
    private static void canopy(WorldGenLevel level, RandomSource r, BlockPos end) {
        BlockState leaves = ModBlocks.GLOAMWOOD_LEAVES.get().defaultBlockState();
        int rad = 1 + r.nextInt(2);
        for (int dx = -rad; dx <= rad; dx++)
            for (int dy = 0; dy <= rad; dy++)
                for (int dz = -rad; dz <= rad; dz++) {
                    int d = Math.abs(dx) + Math.abs(dy) + Math.abs(dz);
                    if (d == 0 || d > rad + 1 || (d == rad + 1 && r.nextInt(3) != 0)) continue;
                    BlockPos q = end.offset(dx, dy, dz);
                    if (level.getBlockState(q).isAir()) {
                        level.setBlock(q, leaves.setValue(net.minecraft.world.level.block.LeavesBlock.DISTANCE, Math.min(6, Math.max(1, d))), 2);
                    }
                }
    }

    /**
     * A fragment of the Lanternguard's lost chapterhouses: a broken pillar or a crumbling wall corner in pale
     * wardstone, half swallowed by gloamstone, sometimes with a guttered lantern.
     */
    public static class Ruin extends Feature<NoneFeatureConfiguration> {
        public Ruin(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            BlockPos base = ctx.origin();
            if (!ground(level, base)) return false;
            BlockState[] mix = {ModBlocks.WARDSTONE_BRICKS.get().defaultBlockState(), ModBlocks.CRACKED_WARDSTONE_BRICKS.get().defaultBlockState(),
                ModBlocks.GLOAMSTONE_BRICKS.get().defaultBlockState(), ModBlocks.MOSSY_WARDSTONE_BRICKS.get().defaultBlockState()};
            if (r.nextBoolean()) {
                // broken pillar
                int h = 2 + r.nextInt(5);
                for (int y = 0; y < h; y++) {
                    set(level, base.above(y), ModBlocks.WARDSTONE_PILLAR.get().defaultBlockState());
                }
                if (r.nextInt(3) == 0) set(level, base.above(h), ModBlocks.CHISELED_WARDSTONE.get().defaultBlockState());
                // a fallen drum beside it
                Direction d = Direction.Plane.HORIZONTAL.getRandomDirection(r);
                BlockPos f = base.relative(d, 2);
                if (ground(level, f)) set(level, f, ModBlocks.WARDSTONE_PILLAR.get().defaultBlockState().setValue(RotatedPillarBlock.AXIS, d.getAxis()));
            } else {
                // wall corner
                int len = 3 + r.nextInt(3), h = 2 + r.nextInt(3);
                for (int i = 0; i < len; i++) {
                    for (int y = 0; y < h - (i > len - 2 ? 1 : 0); y++) {
                        set(level, base.offset(i, y, 0), mix[r.nextInt(mix.length)]);
                        if (i < len - 1) set(level, base.offset(0, y, i), mix[r.nextInt(mix.length)]);
                    }
                }
                if (r.nextInt(2) == 0) set(level, base.offset(1, 0, 1), Blocks.SOUL_LANTERN.defaultBlockState());
            }
            return true;
        }
    }

    /** A drift of veilbloom across gloam moss. */
    public static class Flowers extends Feature<NoneFeatureConfiguration> {
        public Flowers(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource r = ctx.random();
            int placed = 0;
            for (int i = 0; i < 24; i++) {
                BlockPos p = ctx.origin().offset(r.nextInt(7) - 3, r.nextInt(3) - 1, r.nextInt(7) - 3);
                if (level.getBlockState(p.below()).is(ModBlocks.GLOAM_MOSS.get()) && level.getBlockState(p).isAir()) {
                    level.setBlock(p, ModBlocks.VEILBLOOM.get().defaultBlockState(), 2);
                    placed++;
                }
            }
            return placed > 0;
        }
    }
}
