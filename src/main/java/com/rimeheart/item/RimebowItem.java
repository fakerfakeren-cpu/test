package com.rimeheart.item;

import com.rimeheart.entity.projectile.IceShardEntity;
import com.rimeheart.registry.ModSounds;
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

/** Needs no arrows: draws an icicle out of the cold air. Full draws hit harder and chill more. */
public class RimebowItem extends Item {
    public RimebowItem(Properties props) {
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
            Vec3 look = player.getLookAngle();
            IceShardEntity shard = IceShardEntity.shoot(server, player, player.getEyePosition().add(0, -0.1, 0).add(look.scale(0.8)), look.scale(1.6 + power * 1.6),
                3.0f + power * 5.0f, (int) (50 + power * 70));
            shard.setGravity(0.012f);
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.ICICLE_SHOOT.get(), SoundSource.PLAYERS, 1.0f, 0.9f + power * 0.3f);
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
        ItemUtil.tooltip(out, getDescriptionId() + ".desc", 2);
    }
}
