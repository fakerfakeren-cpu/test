package com.astralfall.world;

import com.astralfall.registry.ModBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Ancient impact site: an old, overgrown crater with a cooled meteorite core full of Starmetal. */
public class ImpactSiteFeature extends Feature<NoneFeatureConfiguration> {
    public ImpactSiteFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource r = ctx.random();
        BlockPos origin = ctx.origin();
        BlockState below = level.getBlockState(origin.below());
        if (!below.isSolid() || !level.getFluidState(origin.below()).isEmpty()) return false;
        int rad = 3 + r.nextInt(3);
        for (int dx = -rad; dx <= rad; dx++)
            for (int dz = -rad; dz <= rad; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d > rad + 0.3) continue;
                int depth = (int) Math.round(Math.sqrt(Math.max(0, rad * rad - d * d)) * 0.5);
                BlockPos col = origin.offset(dx, 0, dz);
                for (int y = 3; y >= -depth + 1; y--) {
                    BlockPos p = col.above(y);
                    BlockState st = level.getBlockState(p);
                    if (!st.hasBlockEntity() && st.getDestroySpeed(level, p) >= 0) level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
                }
                BlockPos lining = col.below(depth);
                if (!level.getBlockState(lining).hasBlockEntity()) {
                    BlockState put = r.nextInt(3) == 0 ? ModBlocks.COOLED_METEORITE.get().defaultBlockState()
                        : d > rad - 1.5 ? Blocks.MOSS_BLOCK.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState();
                    level.setBlock(lining, put, 2);
                }
            }
        BlockPos core = origin.below((int) Math.round(rad * 0.5) - 1);
        for (int dx = -1; dx <= 1; dx++)
            for (int dz = -1; dz <= 1; dz++) {
                if (Math.abs(dx) + Math.abs(dz) == 2 && r.nextBoolean()) continue;
                level.setBlock(core.offset(dx, 0, dz), r.nextInt(3) == 0 ? ModBlocks.STARMETAL_ORE.get().defaultBlockState() : ModBlocks.COOLED_METEORITE.get().defaultBlockState(), 2);
            }
        level.setBlock(core, ModBlocks.STARMETAL_ORE.get().defaultBlockState(), 2);
        level.setBlock(core.above(), ModBlocks.SKYSHARD_CLUSTER.get().defaultBlockState(), 2);
        return true;
    }
}
