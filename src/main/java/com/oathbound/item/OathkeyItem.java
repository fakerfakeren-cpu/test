package com.oathbound.item;

import com.oathbound.event.GloamingTravel;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModWorldgen;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * The Oathkey. Turned in the Sundered Keystone it opens the Gate (SunderedKeystoneBlock); once that Gate has
 * opened for its bearer, the key opens the way anywhere: used in the air it carries them to the Gloaming, and
 * home again from there to where they left.
 */
public class OathkeyItem extends InscribedItem {
    private static final int COOLDOWN = 200;

    public OathkeyItem(Properties props) {
        super(props, 3, true);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel server) || !(player instanceof ServerPlayer sp)) return InteractionResult.SUCCESS;
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (!QuestLog.isComplete(sp, "gate")) {
            sp.sendOverlayMessage(Component.translatable("message.oathbound.oathkey.unopened").withStyle(ChatFormatting.LIGHT_PURPLE));
            return InteractionResult.SUCCESS;
        }
        Vfx.burst(server, ModParticles.GLOAM_WISP.get(), sp.position().add(0, 1, 0), 50, 0.5, 0.08);
        server.playSound(null, sp.getX(), sp.getY(), sp.getZ(), ModSounds.GATE_HUM.get(), SoundSource.PLAYERS, 1.2f, 1.3f);
        if (level.dimension() == ModWorldgen.GLOAMING) {
            GloamingTravel.toOverworld(sp);
        } else if (level.dimension() == Level.OVERWORLD) {
            // come back to where you left: the return point sits three blocks "north" of the gate it records
            GloamingTravel.toGloaming(sp, sp.blockPosition().offset(0, 0, -3));
        } else {
            sp.sendOverlayMessage(Component.translatable("message.oathbound.oathkey.elsewhere").withStyle(ChatFormatting.LIGHT_PURPLE));
            return InteractionResult.SUCCESS;
        }
        player.getCooldowns().addCooldown(stack, COOLDOWN);
        return InteractionResult.SUCCESS;
    }
}
