package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The shimmering violet curtain inside an opened Sundered Gate (and the return veil in the Gloaming).
 * Standing inside it for two seconds carries a player across; see {@code GameEvents.tickVeil}.
 */
public class GloamVeilBlock extends Block {
    public static final MapCodec<GloamVeilBlock> CODEC = simpleCodec(GloamVeilBlock::new);

    public GloamVeilBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return Block.box(0, 0, 6, 16, 16, 10);
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return Shapes.empty();
    }

    @Override
    protected boolean skipRendering(BlockState state, BlockState neighbor, Direction dir) {
        return neighbor.is(this) || super.skipRendering(state, neighbor, dir);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        for (int i = 0; i < 2; i++) {
            level.addParticle(ModParticles.GLOAM_WISP.get(), pos.getX() + random.nextDouble(), pos.getY() + random.nextDouble(), pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.8,
                (random.nextDouble() - 0.5) * 0.02, 0.02, (random.nextDouble() - 0.5) * 0.08);
        }
        if (random.nextInt(60) == 0) {
            level.playLocalSound(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, com.oathbound.registry.ModSounds.GATE_HUM.get(), SoundSource.BLOCKS, 0.5f, 0.8f + random.nextFloat() * 0.4f, false);
        }
    }
}
