package com.rimeheart.item;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.util.FX;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/** The Sovereign's own blade, reforged. Heavy chill and Shatter; use: <b>Absolute Zero</b>. */
public class WinterfangItem extends Item {
    public WinterfangItem(Properties props) {
        super(props);
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        super.postHurtEnemy(stack, target, attacker);
        Frost.chill(target, 120);
    }

    @Override
    public float getAttackDamageBonus(Entity target, float damage, DamageSource source) {
        return target instanceof LivingEntity l && Frost.isFrozen(l) ? damage * 0.4f : 0.0f;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            FX.sphere(server, ModParticles.FROST_GLINT.get(), player.position().add(0, 1, 0), 3.0, 90);
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.ICE_SHATTER.get(), SoundSource.PLAYERS, 1.5f, 0.6f);
            FrostbiteBladeItem.coldSnap(server, player, 8.0, Frost.MAX_CHILL, 8.0f);
            player.getCooldowns().addCooldown(stack, 400);
            stack.hurtAndBreak(4, player, hand);
        }
        player.swing(hand, true);
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, getDescriptionId() + ".desc", 3);
    }
}
