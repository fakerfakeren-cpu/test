package com.rimeheart.item;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Hold use to breathe a cone of blizzard for up to five seconds: light damage, heavy chill. */
public class BlizzardStaffItem extends Item {
    private static final int MAX_CHANNEL = 100;
    private static final double RANGE = 7.0;

    public BlizzardStaffItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(player.getItemInHand(hand))) return InteractionResult.PASS;
        player.startUsingItem(hand);
        return InteractionResult.CONSUME;
    }

    @Override
    public void onUseTick(Level level, LivingEntity entity, ItemStack stack, int remaining) {
        if (!(level instanceof ServerLevel server) || !(entity instanceof Player player)) return;
        int used = getUseDuration(stack, entity) - remaining;
        Vec3 eye = player.getEyePosition().add(0, -0.25, 0);
        Vec3 look = player.getLookAngle();
        var rand = player.getRandom();
        for (int i = 0; i < 6; i++) {
            Vec3 dir = look.add((rand.nextDouble() - 0.5) * 0.35, (rand.nextDouble() - 0.5) * 0.25, (rand.nextDouble() - 0.5) * 0.35).normalize();
            double speed = 0.45 + rand.nextDouble() * 0.35;
            Vec3 from = eye.add(look.scale(0.9));
            server.sendParticles(i % 3 == 0 ? ModParticles.SNOW_PUFF.get() : ParticleTypes.SNOWFLAKE, true, true, from.x, from.y, from.z, 0, dir.x, dir.y, dir.z, speed);
        }
        if (used % 20 == 0) server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.BLIZZARD.get(), SoundSource.PLAYERS, 0.9f, 1.0f);
        if (used % 5 == 0) {
            for (LivingEntity e : server.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(RANGE), e -> e != player && e.isAlive() && !e.isAlliedTo(player))) {
                Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
                double d = to.length();
                if (d > RANGE || to.normalize().dot(look) < 0.82) continue;
                if (e instanceof Player && !ItemUtil.isHostileTo(e, player)) continue;
                if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(player)) continue;
                e.hurtServer(server, server.damageSources().indirectMagic(player, player), 1.5f);
                Frost.chill(e, 40);
                e.setDeltaMovement(e.getDeltaMovement().add(look.scale(0.08)));
            }
        }
        if (used % 10 == 0) stack.hurtAndBreak(1, player, player.getUsedItemHand());
        if (used >= MAX_CHANNEL) player.releaseUsingItem();
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level level, LivingEntity entity, int remaining) {
        if (entity instanceof Player player) player.getCooldowns().addCooldown(stack, 50);
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
