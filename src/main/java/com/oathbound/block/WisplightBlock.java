package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Invisible, intangible light. A Warden's Lantern keeps one burning at its bearer's head (refreshing it as they
 * move); Lumen Flasks scatter long-lived ones. Each one counts down and removes itself.
 */
public class WisplightBlock extends Block {
    public static final MapCodec<WisplightBlock> CODEC = simpleCodec(WisplightBlock::new);
    public static final IntegerProperty LIFE = IntegerProperty.create("life", 0, 3);
    public static final BooleanProperty LINGERING = BooleanProperty.create("lingering");

    public WisplightBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(LIFE, 3).setValue(LINGERING, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(LIFE, LINGERING);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return Shapes.empty();
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return Shapes.empty();
    }

    private static int interval(BlockState state) {
        return state.getValue(LINGERING) ? 100 : 6;
    }

    /** Places (or refreshes) a wisplight if the spot is empty air. */
    public static boolean place(ServerLevel level, BlockPos pos, boolean lingering) {
        BlockState cur = level.getBlockState(pos);
        Block self = com.oathbound.registry.ModBlocks.WISPLIGHT.get();
        if (cur.is(self)) {
            if (cur.getValue(LIFE) < 3) level.setBlock(pos, cur.setValue(LIFE, 3), 2);
            return true;
        }
        if (!cur.is(Blocks.AIR) && !cur.is(Blocks.CAVE_AIR)) return false;
        BlockState s = self.defaultBlockState().setValue(LINGERING, lingering);
        level.setBlock(pos, s, 3);
        level.scheduleTick(pos, self, interval(s));
        return true;
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        int life = state.getValue(LIFE);
        if (life <= 0) {
            level.setBlock(pos, Blocks.AIR.defaultBlockState(), 3);
        } else {
            level.setBlock(pos, state.setValue(LIFE, life - 1), 2);
            level.scheduleTick(pos, this, interval(state));
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(LINGERING) && random.nextInt(3) == 0) {
            level.addParticle(ModParticles.LUMEN_MOTE.get(), pos.getX() + random.nextDouble(), pos.getY() + random.nextDouble(), pos.getZ() + random.nextDouble(), 0, 0.005, 0);
        }
    }
}
