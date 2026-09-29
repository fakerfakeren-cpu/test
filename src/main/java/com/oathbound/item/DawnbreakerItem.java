package com.oathbound.item;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/**
 * Dawnbreaker, forged from the Everflame that burned inside the Hollow Crown. Hold use to raise it; release
 * once it blazes to call the Dawn Rite, a sunburst that sears everything around you and triple-burns the Gloam
 * and the undead.
 */
public class DawnbreakerItem extends Item {
    public static final int CHARGE = 20;
    public static final double RADIUS = 7.0;

    public DawnbreakerItem(Properties props) {
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
        if (!(level instanceof ServerLevel server)) return;
        int used = getUseDuration(stack, entity) - remaining;
        Vec3 c = entity.position().add(0, 1.2, 0);
        if (used < CHARGE) {
            Vfx.spiralIn(server, ModParticles.SUNBURST.get(), c, 3.0, 3, used);
        } else {
            Vfx.burst(server, ModParticles.SUNBURST.get(), entity.position().add(0, 2.4, 0), 2, 0.15, 0.02);
        }
        if (used == 1) server.playSound(null, entity.getX(), entity.getY(), entity.getZ(), ModSounds.DAWN_CHARGE.get(), SoundSource.PLAYERS, 1.0f, 1.0f);
        if (used == CHARGE) server.playSound(null, entity.getX(), entity.getY(), entity.getZ(), net.minecraft.sounds.SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 2.0f, 1.6f);
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level level, LivingEntity entity, int remaining) {
        int used = getUseDuration(stack, entity) - remaining;
        if (used < CHARGE || !(entity instanceof Player player)) return false;
        if (level instanceof ServerLevel server) {
            dawnRite(server, player);
            stack.hurtAndBreak(3, player, player.getUsedItemHand());
            player.getCooldowns().addCooldown(stack, com.oathbound.event.GameEvents.cooldown(player, 140));
        }
        return true;
    }

    public static void dawnRite(ServerLevel level, Player player) {
        Vec3 c = player.position().add(0, 1, 0);
        level.playSound(null, c.x, c.y, c.z, ModSounds.DAWN_BURST.get(), SoundSource.PLAYERS, 2.5f, 1.0f);
        Vfx.sphere(level, ModParticles.SUNBURST.get(), c, RADIUS * 0.6, 160);
        for (int ring = 1; ring <= 3; ring++) Vfx.ring(level, ModParticles.SUNBURST.get(), c.add(0, -0.8, 0), RADIUS * ring / 3.0, 30 * ring, 0.04);
        Vfx.burst(level, ModParticles.SUNBURST.get(), c, 40, 0.3, 0.3);
        Vfx.burst(level, ModParticles.EMBER.get(), c, 60, 1.5, 0.2);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(RADIUS), e -> e != player && e.isAlive())) {
            if (e.distanceTo(player) > RADIUS) continue;
            if (e instanceof TamableAnimal pet && pet.isOwnedBy(player)) continue;
            if (e instanceof Player p && !Inscriptions.isFoeOf(p, player)) continue;
            if (e instanceof com.oathbound.entity.mob.SpectralHousecarlEntity h && h.isAlly()) continue;
            boolean gloam = e.typeHolder().is(ModTags.GLOAM_CREATURES) || e.typeHolder().is(EntityTypeTags.UNDEAD);
            float dmg = gloam ? 30.0f : 10.0f;
            e.hurtServer(level, level.damageSources().indirectMagic(player, player), dmg);
            e.igniteForSeconds(gloam ? 6 : 3);
            Vec3 away = e.position().subtract(player.position()).multiply(1, 0, 1).normalize();
            e.setDeltaMovement(away.scale(1.1).add(0, 0.45, 0));
            e.hurtMarked = true;
        }
    }

    @Override
    public int getUseDuration(ItemStack stack, LivingEntity entity) {
        return 72000;
    }

    @Override
    public ItemUseAnimation getUseAnimation(ItemStack stack) {
        return ItemUseAnimation.TRIDENT;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 3);
    }
}
