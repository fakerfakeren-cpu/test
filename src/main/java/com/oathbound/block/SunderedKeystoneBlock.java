package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.event.GateRite;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;

/** The keystone of the Sundered Gate. Turn the Oathkey in it to begin the rite that opens the way to the Gloaming. */
public class SunderedKeystoneBlock extends Block {
    public static final MapCodec<SunderedKeystoneBlock> CODEC = simpleCodec(SunderedKeystoneBlock::new);
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");

    public SunderedKeystoneBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(ACTIVE, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(ACTIVE);
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!stack.is(ModItems.OATHKEY.get())) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (level instanceof ServerLevel server) {
            if (state.getValue(ACTIVE) || GateRite.isRunning(server, pos)) {
                player.sendOverlayMessage(Component.translatable("message.oathbound.gate.already").withStyle(ChatFormatting.LIGHT_PURPLE));
                return InteractionResult.SUCCESS;
            }
            GateRite.begin(server, pos, player);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable(state.getValue(ACTIVE) ? "message.oathbound.gate.open_hint" : "message.oathbound.gate.hint")
                .withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        int n = state.getValue(ACTIVE) ? 3 : 1;
        for (int i = 0; i < n; i++) {
            level.addParticle(ModParticles.GLOAM_WISP.get(), pos.getX() + random.nextDouble(), pos.getY() + 1.0, pos.getZ() + random.nextDouble(), 0, 0.04, 0);
        }
    }
}
