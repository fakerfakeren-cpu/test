package com.astralfall.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/** Freshly fallen meteorite: still glowing, it smoulders when exposed to air. */
public class GlowingMeteoriteBlock extends Block {
    public static final MapCodec<GlowingMeteoriteBlock> CODEC = simpleCodec(GlowingMeteoriteBlock::new);

    public GlowingMeteoriteBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(6) == 0 && level.getBlockState(pos.above()).isAir()) {
            double x = pos.getX() + random.nextDouble();
            double z = pos.getZ() + random.nextDouble();
            level.addParticle(random.nextBoolean() ? ParticleTypes.SMOKE : ParticleTypes.SMALL_FLAME, x, pos.getY() + 1.02, z, 0, 0.02, 0);
        }
    }
}
