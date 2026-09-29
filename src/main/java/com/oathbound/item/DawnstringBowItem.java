package com.oathbound.item;

import com.oathbound.entity.projectile.SunArrowEntity;
import com.oathbound.registry.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/**
 * The Dawnstring Longbow, strung with spellsilk. It turns ordinary arrows into shafts of dawnlight that fly
 * straight and true. Fully drawn shots pierce and brand their target with Sunmark.
 */
public class DawnstringBowItem extends Item {
    public DawnstringBowItem(Properties props) {
        super(props);
    }

    private static ItemStack findArrow(Player player) {
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(Items.ARROW) || s.is(Items.SPECTRAL_ARROW) || s.is(Items.TIPPED_ARROW)) return s;
        }
        return ItemStack.EMPTY;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (!player.hasInfiniteMaterials() && findArrow(player).isEmpty()) return InteractionResult.FAIL;
        player.startUsingItem(hand);
        return InteractionResult.CONSUME;
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level level, LivingEntity entity, int remaining) {
        if (!(entity instanceof Player player)) return false;
        int charge = getUseDuration(stack, entity) - remaining;
        float power = BowItem.getPowerForTime(charge);
        if (power < 0.15f) return false;
        if (level instanceof ServerLevel server) {
            boolean full = power >= 1.0f;
            SunArrowEntity arrow = new SunArrowEntity(server, player, full);
            arrow.snapTo(player.getX(), player.getEyeY() - 0.1, player.getZ(), player.getYRot(), player.getXRot());
            arrow.setDeltaMovement(player.getLookAngle().scale(3.4 * power));
            arrow.setDamage(4.0f + 6.0f * power);
            server.addFreshEntity(arrow);
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.SUN_ARROW.get(), SoundSource.PLAYERS, 1.0f, 0.9f + power * 0.3f);
            stack.hurtAndBreak(1, player, player.getUsedItemHand());
            if (!player.hasInfiniteMaterials()) {
                ItemStack ammo = findArrow(player);
                if (!ammo.isEmpty()) ammo.shrink(1);
            }
        }
        return true;
    }

    @Override
    public int getUseDuration(ItemStack stack, LivingEntity entity) {
        return 72000;
    }

    @Override
    public ItemUseAnimation getUseAnimation(ItemStack stack) {
        return ItemUseAnimation.BOW;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 3);
    }
}
