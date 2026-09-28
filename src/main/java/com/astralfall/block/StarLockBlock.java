package com.astralfall.block;

import com.astralfall.registry.ModBlocks;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
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
import net.minecraft.world.phys.Vec3;

/**
 * Secret mechanism in the Shattered Observatory. Socket a Skyshard and every Sealed Astral Brick
 * nearby crumbles away, revealing the Star Vault.
 */
public class StarLockBlock extends Block {
    public static final MapCodec<StarLockBlock> CODEC = simpleCodec(StarLockBlock::new);
    public static final BooleanProperty OPEN = BooleanProperty.create("open");

    public StarLockBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(OPEN, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(OPEN);
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (state.getValue(OPEN)) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (!stack.is(ModItems.SKYSHARD.get())) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (level instanceof ServerLevel server) {
            if (!player.hasInfiniteMaterials()) stack.shrink(1);
            level.setBlock(pos, state.setValue(OPEN, true), 3);
            int removed = unseal(server, pos);
            player.sendOverlayMessage(Component.translatable("message.astralfall.star_lock.open", removed).withStyle(ChatFormatting.AQUA));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable(state.getValue(OPEN) ? "message.astralfall.star_lock.already_open" : "message.astralfall.star_lock.hint").withStyle(ChatFormatting.GRAY));
        }
        return InteractionResult.SUCCESS;
    }

    public static int unseal(ServerLevel level, BlockPos center) {
        int removed = 0;
        BlockState sealed = ModBlocks.SEALED_ASTRAL_BRICKS.get().defaultBlockState();
        for (BlockPos p : BlockPos.betweenClosed(center.offset(-12, -10, -12), center.offset(12, 10, 12))) {
            if (level.getBlockState(p).is(sealed.getBlock())) {
                BlockPos imm = p.immutable();
                level.setBlock(imm, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
                FX.burst(level, new BlockParticleOption(ParticleTypes.BLOCK, sealed), Vec3.atCenterOf(imm), 12, 0.3, 0.1);
                FX.burst(level, ModParticles.STAR_SPARKLE.get(), Vec3.atCenterOf(imm), 3, 0.3, 0.02);
                removed++;
            }
        }
        level.playSound(null, center, ModSounds.VAULT_OPEN.get(), SoundSource.BLOCKS, 2.0f, 1.0f);
        level.playSound(null, center, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 2.0f, 0.6f);
        return removed;
    }
}
