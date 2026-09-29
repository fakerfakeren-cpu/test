package com.oathbound.item;

import com.oathbound.entity.projectile.AnchorHookEntity;
import com.oathbound.registry.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/**
 * Sir Caldris' anchor, still trailing its drowned chain. Swing it as a heavy weapon, or hurl it: it drags a
 * creature back to your feet, or bites into stone and hauls you after it.
 */
public class DrownedAnchorItem extends Item {
    public DrownedAnchorItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            AnchorHookEntity hook = new AnchorHookEntity(server, player);
            hook.snapTo(player.getX(), player.getEyeY() - 0.2, player.getZ(), player.getYRot(), player.getXRot());
            hook.setDeltaMovement(player.getLookAngle().scale(1.9));
            server.addFreshEntity(hook);
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.ANCHOR_THROW.get(), SoundSource.PLAYERS, 1.0f, 0.9f + player.getRandom().nextFloat() * 0.2f);
            stack.hurtAndBreak(1, player, hand);
        }
        player.getCooldowns().addCooldown(stack, com.oathbound.event.GameEvents.cooldown(player, 50));
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 3);
    }
}
