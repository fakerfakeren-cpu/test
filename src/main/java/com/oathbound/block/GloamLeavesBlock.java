package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;

/** Gloamwood foliage: violet leaves strung with pale lights that shed motes of dusk instead of falling leaves. */
public class GloamLeavesBlock extends LeavesBlock {
    public static final MapCodec<GloamLeavesBlock> CODEC = simpleCodec(GloamLeavesBlock::new);

    public GloamLeavesBlock(Properties props) {
        super(0.03f, props);
    }

    @Override
    public MapCodec<? extends LeavesBlock> codec() {
        return CODEC;
    }

    @Override
    protected void spawnFallingLeavesParticle(Level level, BlockPos pos, RandomSource random) {
        level.addParticle(ModParticles.GLOAM_WISP.get(), pos.getX() + random.nextDouble(), pos.getY() - 0.05, pos.getZ() + random.nextDouble(), 0, -0.015, 0);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        super.animateTick(state, level, pos, random);
        if (random.nextInt(24) == 0) {
            level.addParticle(ModParticles.LUMEN_MOTE.get(), pos.getX() + random.nextDouble(), pos.getY() + random.nextDouble(), pos.getZ() + random.nextDouble(), 0, 0.005, 0);
        }
    }
}
