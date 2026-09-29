package com.rimeheart.item;

import com.rimeheart.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Summons the Frost Sovereign when sounded at a Glacial Altar (see GlacialAltarBlock). Elsewhere it only echoes. */
public class WinterHornItem extends LoreItem {
    public WinterHornItem(Properties props) {
        super(props, 2, true);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.WINTER_HORN.get(), SoundSource.PLAYERS, 1.2f, 1.3f);
        if (!level.isClientSide()) {
            player.sendOverlayMessage(Component.translatable("message.rimeheart.horn.echo").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
            player.getCooldowns().addCooldown(stack, 60);
        }
        return InteractionResult.SUCCESS;
    }
}
