package com.astralfall.block;

import com.astralfall.registry.ModParticles;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A captured star in a jar: the brightest lamp in the game, and it twinkles. */
public class StarJarBlock extends Block {
    public static final MapCodec<StarJarBlock> CODEC = simpleCodec(StarJarBlock::new);
    private static final VoxelShape SHAPE = Block.box(5, 0, 5, 11, 10, 11);

    public StarJarBlock(Properties props) {
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
        if (random.nextInt(3) == 0) {
            level.addParticle(ModParticles.GOLD_SPARKLE.get(), pos.getX() + 0.5 + (random.nextDouble() - 0.5) * 0.5, pos.getY() + 0.4 + random.nextDouble() * 0.5, pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.5, 0, 0.015, 0);
        }
    }
}
