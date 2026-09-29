package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModParticles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/** A shimmering wall of Veyl's warding. Unbreakable; dissolves when the Cipher is solved. */
public class ArcaneWardBlock extends Block {
    public static final MapCodec<ArcaneWardBlock> CODEC = simpleCodec(ArcaneWardBlock::new);

    public ArcaneWardBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected boolean skipRendering(BlockState state, BlockState neighbor, Direction dir) {
        return neighbor.is(this) || super.skipRendering(state, neighbor, dir);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.ward.hint").withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) != 0) return;
        level.addParticle(ModParticles.ARCANE_GLYPH.get(), pos.getX() + random.nextDouble(), pos.getY() + random.nextDouble(), pos.getZ() + random.nextDouble(), 0, 0.01, 0);
    }
}
