package com.astralfall.item;

import com.astralfall.entity.projectile.SingularityGrenadeEntity;
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

public class SingularityGrenadeItem extends Item {
    public SingularityGrenadeItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.SNOWBALL_THROW, SoundSource.PLAYERS, 0.6f, 0.5f);
        if (level instanceof ServerLevel server) {
            SingularityGrenadeEntity grenade = new SingularityGrenadeEntity(server, player, stack.copyWithCount(1));
            grenade.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0f, 1.3f, 1.0f);
            server.addFreshEntity(grenade);
            player.getCooldowns().addCooldown(stack, 30);
        }
        if (!player.hasInfiniteMaterials()) stack.shrink(1);
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.singularity_grenade.desc", 2);
    }
}
