package com.astralfall.block;

import com.astralfall.event.Starfall;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

import java.util.HashMap;
import java.util.Map;

/**
 * The eyepiece of the great telescope. Look through it at night and you knock a star loose:
 * a Fallen Star crashes down right next to the observatory.
 */
public class TelescopeEyepieceBlock extends Block {
    public static final MapCodec<TelescopeEyepieceBlock> CODEC = simpleCodec(TelescopeEyepieceBlock::new);
    private static final Map<Long, Long> LAST_USE = new HashMap<>();
    private static final long COOLDOWN = 24000L / 2;

    public TelescopeEyepieceBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level instanceof ServerLevel server)) return InteractionResult.SUCCESS;
        if (!server.isDarkOutside()) {
            player.sendOverlayMessage(Component.translatable("message.astralfall.telescope.day").withStyle(ChatFormatting.GRAY));
            return InteractionResult.SUCCESS;
        }
        long now = server.getGameTime();
        Long last = LAST_USE.get(pos.asLong());
        if (last != null && now - last < COOLDOWN && !player.hasInfiniteMaterials()) {
            player.sendOverlayMessage(Component.translatable("message.astralfall.telescope.cooldown").withStyle(ChatFormatting.GRAY));
            return InteractionResult.SUCCESS;
        }
        LAST_USE.put(pos.asLong(), now);
        player.sendSystemMessage(Component.translatable("message.astralfall.telescope.star").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
        double angle = server.getRandom().nextDouble() * Math.PI * 2;
        double dist = 14 + server.getRandom().nextInt(10);
        BlockPos target = BlockPos.containing(pos.getX() + Math.cos(angle) * dist, pos.getY(), pos.getZ() + Math.sin(angle) * dist);
        Starfall.spawnMeteor(server, target, Starfall.Variant.FALLEN_STAR, 2.0f);
        return InteractionResult.SUCCESS;
    }
}
