package com.rimeheart.block;

import com.mojang.serialization.MapCodec;
import com.rimeheart.entity.boss.SovereignRitual;
import com.rimeheart.registry.ModItems;
import com.rimeheart.registry.ModParticles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
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
import net.minecraft.world.phys.BlockHitResult;

/** Sound the Winter Horn at a Glacial Altar to wake the Frost Sovereign. */
public class GlacialAltarBlock extends Block {
    public static final MapCodec<GlacialAltarBlock> CODEC = simpleCodec(GlacialAltarBlock::new);

    public GlacialAltarBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!stack.is(ModItems.WINTER_HORN.get())) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (level instanceof ServerLevel server) {
            if (SovereignRitual.isActive(server)) {
                player.sendOverlayMessage(Component.translatable("message.rimeheart.altar.busy").withStyle(ChatFormatting.RED));
                return InteractionResult.FAIL;
            }
            if (!player.hasInfiniteMaterials()) stack.shrink(1);
            SovereignRitual.begin(server, pos.above());
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable("message.rimeheart.altar.hint").withStyle(ChatFormatting.AQUA));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        for (int i = 0; i < 2; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double r = 0.6 + random.nextDouble() * 0.4;
            level.addParticle(ModParticles.FROST_GLINT.get(), pos.getX() + 0.5 + Math.cos(a) * r, pos.getY() + 1.1 + random.nextDouble() * 0.6,
                pos.getZ() + 0.5 + Math.sin(a) * r, -Math.cos(a) * 0.02, 0.02, -Math.sin(a) * 0.02);
        }
        if (random.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.SNOWFLAKE, pos.getX() + random.nextDouble(), pos.getY() + 1.0, pos.getZ() + random.nextDouble(), 0, 0.03, 0);
        }
    }
}
