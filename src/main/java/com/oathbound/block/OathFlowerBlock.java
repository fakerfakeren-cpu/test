package com.oathbound.block;

import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.FlowerBlock;
import net.minecraft.world.level.block.state.BlockState;

/**
 * A wildflower of the old kingdom. Each kind gives off its own faint light: emberroot smoulders, the moonpetal
 * glimmers after dark, the dusk lily breathes violet motes, and the gloam fern grows only on Gloam-touched ground.
 */
public class OathFlowerBlock extends FlowerBlock {
    public enum Glint { EMBER, MOON, DUSK, GLOAM }

    private final Glint glint;

    public OathFlowerBlock(Holder<MobEffect> effect, float seconds, Glint glint, Properties props) {
        super(effect, seconds, props);
        this.glint = glint;
    }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        if (glint == Glint.GLOAM) return state.is(ModBlocks.GLOAM_MOSS.get()) || state.is(ModBlocks.GLOAMSTONE.get());
        return state.is(ModBlocks.GLOAM_MOSS.get()) || super.mayPlaceOn(state, level, pos);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        double x = pos.getX() + 0.3 + random.nextDouble() * 0.4, y = pos.getY() + 0.5 + random.nextDouble() * 0.3, z = pos.getZ() + 0.3 + random.nextDouble() * 0.4;
        switch (glint) {
            case EMBER -> {
                if (random.nextInt(6) == 0) level.addParticle(ModParticles.EMBER.get(), x, y + 0.2, z, 0, 0.02, 0);
            }
            case MOON -> {
                long time = level.getDayTime() % 24000L;
                if (time > 12500 && time < 23500 && random.nextInt(5) == 0) level.addParticle(ModParticles.LUMEN_MOTE.get(), x, y, z, 0, 0.008, 0);
            }
            case DUSK -> {
                if (random.nextInt(8) == 0) level.addParticle(ModParticles.GLOAM_WISP.get(), x, y, z, 0, 0.012, 0);
            }
            case GLOAM -> {
                if (random.nextInt(10) == 0) level.addParticle(ModParticles.SPIRIT.get(), x, y + 0.3, z, 0, 0.01, 0);
            }
        }
    }
}
