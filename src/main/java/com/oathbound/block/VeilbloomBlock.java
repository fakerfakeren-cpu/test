package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.FlowerBlock;
import net.minecraft.world.level.block.state.BlockState;

/** A pale violet flower that grows only where the Gloam has touched. It glows faintly and sheds motes of dusk. */
public class VeilbloomBlock extends FlowerBlock {
    public static final MapCodec<VeilbloomBlock> CODEC = simpleCodec(VeilbloomBlock::new);

    public VeilbloomBlock(Properties props) {
        super(MobEffects.NIGHT_VISION, 8.0f, props);
    }

    @Override
    public MapCodec<? extends FlowerBlock> codec() {
        return CODEC;
    }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(ModBlocks.GLOAM_MOSS.get()) || state.is(ModBlocks.GLOAMSTONE.get()) || super.mayPlaceOn(state, level, pos);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(4) == 0) {
            level.addParticle(ModParticles.GLOAM_WISP.get(), pos.getX() + 0.3 + random.nextDouble() * 0.4, pos.getY() + 0.6, pos.getZ() + 0.3 + random.nextDouble() * 0.4, 0, 0.015, 0);
        }
    }
}
