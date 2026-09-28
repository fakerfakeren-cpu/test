package com.astralfall.block;

import com.astralfall.entity.boss.BossSummoner;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModParticles;
import com.mojang.serialization.MapCodec;
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

/** Place an Eclipse Sigil on the altar to summon Astraeus. */
public class AstralAltarBlock extends Block {
    public static final MapCodec<AstralAltarBlock> CODEC = simpleCodec(AstralAltarBlock::new);

    public AstralAltarBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!stack.is(ModItems.ECLIPSE_SIGIL.get())) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (level instanceof ServerLevel server) {
            if (BossSummoner.isRitualActive(server)) {
                player.sendOverlayMessage(Component.translatable("message.astralfall.altar.busy").withStyle(ChatFormatting.RED));
                return InteractionResult.FAIL;
            }
            if (!player.hasInfiniteMaterials()) stack.shrink(1);
            BossSummoner.begin(server, pos.above());
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable("message.astralfall.altar.hint").withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        for (int i = 0; i < 2; i++) {
            double a = random.nextDouble() * Math.PI * 2;
            double r = 0.6 + random.nextDouble() * 0.6;
            level.addParticle(ParticleTypes.ENCHANT, pos.getX() + 0.5 + Math.cos(a) * r, pos.getY() + 1.6, pos.getZ() + 0.5 + Math.sin(a) * r, -Math.cos(a) * 0.4, -0.5, -Math.sin(a) * 0.4);
        }
        if (random.nextInt(3) == 0) {
            level.addParticle(ModParticles.STAR_SPARKLE.get(), pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5, (random.nextDouble() - 0.5) * 0.05, 0.05, (random.nextDouble() - 0.5) * 0.05);
        }
    }
}
