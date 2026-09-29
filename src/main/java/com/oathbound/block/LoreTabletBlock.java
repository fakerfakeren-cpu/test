package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * An engraved Lanternguard tablet. Each tablet index carries a titled passage of lore; reading all of them
 * completes the Loremaster quest.
 */
public class LoreTabletBlock extends HorizontalDirectionalBlock {
    public static final MapCodec<LoreTabletBlock> CODEC = simpleCodec(LoreTabletBlock::new);
    public static final IntegerProperty TABLET = IntegerProperty.create("tablet", 0, 15);
    /** Number of lines of text per tablet index (keys tablet.oathbound.N.1 .. N.lines). */
    public static final int[] LINES = {4, 4, 4, 5, 4, 5, 4, 5, 4, 4};

    public LoreTabletBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(FACING, net.minecraft.core.Direction.NORTH).setValue(TABLET, 0));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, TABLET);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
    }

    public static int tabletCount() {
        return LINES.length;
    }

    public static void read(Player player, int index) {
        int i = Math.max(0, Math.min(LINES.length - 1, index));
        player.sendSystemMessage(Component.literal(""));
        player.sendSystemMessage(Component.literal("✦ ").withStyle(ChatFormatting.GOLD)
            .append(Component.translatable("tablet.oathbound." + i + ".title").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD))
            .append(Component.literal(" ✦").withStyle(ChatFormatting.GOLD)));
        for (int l = 1; l <= LINES[i]; l++) {
            player.sendSystemMessage(Component.translatable("tablet.oathbound." + i + "." + l).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        }
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide() && player instanceof ServerPlayer sp) {
            int idx = state.getValue(TABLET);
            read(player, idx);
            level.playSound(null, pos, ModSounds.CHRONICLE_PAGE.get(), SoundSource.BLOCKS, 0.8f, 0.8f);
            QuestLog.readTablet(sp, idx);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(4) != 0) return;
        var f = state.getValue(FACING);
        double x = pos.getX() + 0.5 + f.getStepX() * 0.55 + (random.nextDouble() - 0.5) * 0.6;
        double z = pos.getZ() + 0.5 + f.getStepZ() * 0.55 + (random.nextDouble() - 0.5) * 0.6;
        level.addParticle(ModParticles.LUMEN_MOTE.get(), x, pos.getY() + 0.3 + random.nextDouble() * 0.6, z, 0, 0.01, 0);
    }
}
