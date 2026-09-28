package com.astralfall.block;

import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The heart of a rare golden meteor. It shoots a pillar of light into the sky so it can be
 * spotted from far away, and chimes softly.
 */
public class FallenStarBlock extends Block {
    public static final MapCodec<FallenStarBlock> CODEC = simpleCodec(FallenStarBlock::new);
    private static final VoxelShape SHAPE = Block.box(3, 0, 3, 13, 10, 13);

    public FallenStarBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        double cx = pos.getX() + 0.5, cy = pos.getY() + 0.5, cz = pos.getZ() + 0.5;
        // pillar of light (always visible so it reads from a distance)
        for (int i = 0; i < 3; i++) {
            level.addAlwaysVisibleParticle(ParticleTypes.END_ROD, cx + (random.nextDouble() - 0.5) * 0.3, cy + random.nextDouble() * 2, cz + (random.nextDouble() - 0.5) * 0.3, 0, 0.6 + random.nextDouble() * 0.6, 0);
        }
        level.addParticle(ModParticles.GOLD_SPARKLE.get(), cx + (random.nextDouble() - 0.5) * 1.5, cy + random.nextDouble(), cz + (random.nextDouble() - 0.5) * 1.5, 0, 0.03, 0);
        if (random.nextInt(60) == 0) {
            level.playLocalSound(cx, cy, cz, ModSounds.STAR_CHIME.get(), SoundSource.BLOCKS, 0.8f, 0.9f + random.nextFloat() * 0.3f, false);
        }
    }
}
