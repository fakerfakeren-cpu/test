package com.astralfall.item;

import com.astralfall.entity.projectile.StarBoltEntity;
import com.astralfall.registry.ModSounds;
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
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Needs no arrows. Draw to charge; release a volley of homing stars (up to five at full draw). */
public class ConstellationBowItem extends Item {
    public ConstellationBowItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        player.startUsingItem(hand);
        return InteractionResult.CONSUME;
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level level, LivingEntity entity, int remaining) {
        if (!(entity instanceof Player player)) return false;
        float power = BowItem.getPowerForTime(getUseDuration(stack, entity) - remaining);
        if (power < 0.2f) return false;
        if (level instanceof ServerLevel server) {
            int count = 1 + Math.round(power * 4);
            Vec3 look = player.getLookAngle();
            Vec3 right = look.cross(new Vec3(0, 1, 0)).normalize();
            Vec3 eye = player.getEyePosition().add(0, -0.2, 0);
            for (int i = 0; i < count; i++) {
                double spread = (i - (count - 1) / 2.0) * 0.18;
                Vec3 dir = look.add(right.scale(spread)).add(0, Math.abs(spread) * 0.3, 0);
                StarBoltEntity bolt = StarBoltEntity.shoot(server, player, eye.add(look), dir, 0, 3.0f + power * 4.0f, null);
                bolt.setHoming(0.1f + power * 0.1f);
            }
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.STAR_BOLT.get(), SoundSource.PLAYERS, 1.0f, 1.0f + power * 0.3f);
            stack.hurtAndBreak(1, player, player.getUsedItemHand());
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
        ItemUtil.tooltip(out, "item.astralfall.constellation_bow.desc", 3);
    }
}
