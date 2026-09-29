package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/** An unbreakable seal (crypt grate, barrow door) that only its puzzle can lift. */
public class SealedBlock extends Block {
    public static final MapCodec<SealedBlock> CODEC = simpleCodec(SealedBlock::new);

    public SealedBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable(getDescriptionId() + ".hint").withStyle(ChatFormatting.GRAY));
        }
        return InteractionResult.SUCCESS;
    }
}
