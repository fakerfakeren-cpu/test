package com.oathbound.item;

import com.oathbound.entity.projectile.LumenFlaskEntity;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
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

/** A flask of bottled daylight. Thrown, it bursts into a flare that burns Gloam creatures and leaves glowing wisps. */
public class LumenFlaskItem extends Item {
    public LumenFlaskItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.SPLASH_POTION_THROW, SoundSource.PLAYERS, 0.6f, 0.7f);
        if (level instanceof ServerLevel server) {
            LumenFlaskEntity flask = new LumenFlaskEntity(server, player, stack.copyWithCount(1));
            flask.shootFromRotation(player, player.getXRot(), player.getYRot(), -10.0f, 0.9f, 1.0f);
            server.addFreshEntity(flask);
        }
        if (!player.hasInfiniteMaterials()) stack.shrink(1);
        player.getCooldowns().addCooldown(stack, 10);
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 2);
    }
}
