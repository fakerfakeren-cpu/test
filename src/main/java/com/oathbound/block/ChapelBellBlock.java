package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import com.oathbound.util.Puzzles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.List;

/**
 * One of the four tuned bells of a Drowned Chapel. Each is cast with a coloured band (sea-blue, verdigris,
 * gold, crimson) and rings its own note, low to high. Ringing them in the order of the Hymn Stone's hymn
 * opens the crypt.
 */
public class ChapelBellBlock extends Block {
    public static final MapCodec<ChapelBellBlock> CODEC = simpleCodec(ChapelBellBlock::new);
    public static final IntegerProperty TONE = IntegerProperty.create("tone", 0, 3);
    public static final ChatFormatting[] COLORS = {ChatFormatting.DARK_AQUA, ChatFormatting.GREEN, ChatFormatting.GOLD, ChatFormatting.RED};
    private static final VoxelShape SHAPE = Shapes.or(Block.box(3, 0, 3, 13, 2, 13), Block.box(4, 2, 4, 12, 11, 12), Block.box(7, 11, 7, 9, 16, 9));

    public ChapelBellBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(TONE, 0));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(TONE);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    public static Component toneName(int tone) {
        return Component.translatable("bell.oathbound.tone." + tone).withStyle(COLORS[tone & 3], ChatFormatting.BOLD);
    }

    /** Plays a bell note at a position with its coloured shimmer. */
    public static void chime(ServerLevel level, BlockPos pos, int tone) {
        level.playSound(null, pos, ModSounds.bell(tone), SoundSource.BLOCKS, 2.2f, 1.0f);
        Vec3 c = Vec3.atCenterOf(pos);
        Vfx.burst(level, ModParticles.TIDE.get(), c, 10, 0.35, 0.04);
        level.sendParticles(ParticleTypes.NOTE, true, true, c.x, c.y + 0.8, c.z, 0, tone / 4.0 + 0.1, 0, 0, 1);
        Vfx.ring(level, ModParticles.LUMEN_MOTE.get(), c, 1.2 + tone * 0.2, 16, 0.02);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level instanceof ServerLevel server) {
            int tone = state.getValue(TONE);
            chime(server, pos, tone);
            player.sendOverlayMessage(Component.translatable("message.oathbound.bell.rung", toneName(tone)).withStyle(ChatFormatting.GRAY));
            List<BlockPos> stones = Puzzles.find(server, pos, 16, ModBlocks.HYMN_STONE.get());
            if (!stones.isEmpty()) HymnStoneBlock.onBellRung(server, stones.get(0), tone, player);
        }
        return InteractionResult.SUCCESS;
    }
}
