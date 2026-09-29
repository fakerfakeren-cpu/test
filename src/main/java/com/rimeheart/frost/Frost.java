package com.rimeheart.frost;

import com.rimeheart.registry.ModItems;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.registry.ModTags;
import com.rimeheart.util.FX;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Rimeheart's core mechanic: <b>chill</b>. It builds on vanilla freezing (the same meter powder snow fills),
 * so chilled mobs slow down, shiver and take freeze damage once fully frozen, and players see the frost
 * overlay. Frost weapons add chill; fully frozen targets take bonus "shatter" damage from them.
 * Anything wearing a Frostiron or Wraithweave piece is immune (they are freeze-immune wearables, like leather).
 */
public final class Frost {
    /** Chill is capped so a target thaws within a few seconds of the last hit. */
    public static final int MAX_CHILL = 320;
    private static final Map<UUID, Long> FADE_READY = new HashMap<>();

    private Frost() {}

    public static boolean immune(LivingEntity e) {
        return e.typeHolder().is(ModTags.WINTER_CREATURES) || !e.canFreeze();
    }

    /** Adds chill (freeze ticks). Returns true if the target is now fully frozen. */
    public static boolean chill(LivingEntity e, int ticks) {
        if (immune(e)) return false;
        boolean was = e.isFullyFrozen();
        e.setTicksFrozen(Math.min(MAX_CHILL, Math.max(e.getTicksFrozen(), 0) + ticks));
        boolean now = e.getTicksFrozen() >= e.getTicksRequiredToFreeze();
        if (now) e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 30, 1, false, false, true));
        if (now && !was && e.level() instanceof ServerLevel level) {
            FX.burst(level, ModParticles.FROST_GLINT.get(), e.getBoundingBox().getCenter(), 14, 0.35, 0.05);
            level.playSound(null, e.getX(), e.getY(), e.getZ(), ModSounds.FREEZE.get(), SoundSource.PLAYERS, 0.9f, 0.9f + e.getRandom().nextFloat() * 0.3f);
        }
        return now;
    }

    public static boolean isFrozen(LivingEntity e) {
        return e.getTicksFrozen() >= e.getTicksRequiredToFreeze();
    }

    // ------------------------------------------------------------------ armour set bonuses

    private static boolean wearing(LivingEntity e, Item head, Item chest, Item legs, Item feet) {
        return e.getItemBySlot(EquipmentSlot.HEAD).is(head) && e.getItemBySlot(EquipmentSlot.CHEST).is(chest)
            && e.getItemBySlot(EquipmentSlot.LEGS).is(legs) && e.getItemBySlot(EquipmentSlot.FEET).is(feet);
    }

    public static boolean hasFrostironSet(LivingEntity e) {
        return wearing(e, ModItems.FROSTIRON_HELMET.get(), ModItems.FROSTIRON_CHESTPLATE.get(), ModItems.FROSTIRON_LEGGINGS.get(), ModItems.FROSTIRON_BOOTS.get());
    }

    public static boolean hasWraithweaveSet(LivingEntity e) {
        return wearing(e, ModItems.WRAITHWEAVE_HOOD.get(), ModItems.WRAITHWEAVE_ROBE.get(), ModItems.WRAITHWEAVE_LEGGINGS.get(), ModItems.WRAITHWEAVE_BOOTS.get());
    }

    public static void onPlayerTick(Player player) {
        if (!(player.level() instanceof ServerLevel level) || player.isSpectator()) return;
        if (hasFrostironSet(player)) {
            // Glacial Stride: water freezes into frosted ice underfoot (like Frost Walker I).
            if (player.onGround() && !player.isPassenger()) {
                BlockPos feet = player.blockPosition();
                for (BlockPos p : BlockPos.betweenClosed(feet.offset(-2, -1, -2), feet.offset(2, -1, 2))) {
                    if (p.distToCenterSqr(player.getX(), p.getY() + 0.5, player.getZ()) > 6.25) continue;
                    BlockState s = level.getBlockState(p);
                    if (s.is(Blocks.WATER) && s.getFluidState().is(Fluids.WATER) && s.getFluidState().isSource() && level.getBlockState(p.above()).isAir()) {
                        level.setBlockAndUpdate(p, Blocks.FROSTED_ICE.defaultBlockState());
                        level.scheduleTick(p.immutable(), Blocks.FROSTED_ICE, Mth.nextInt(player.getRandom(), 60, 120));
                    }
                }
            }
            // Frostward: melee attackers are chilled.
            if (player.hurtTime == 9 && player.getLastHurtByMob() != null && player.getLastHurtByMob().distanceToSqr(player) < 16) {
                LivingEntity attacker = player.getLastHurtByMob();
                if (chill(attacker, 90)) FX.burst(level, ParticleTypes.SNOWFLAKE, attacker.getBoundingBox().getCenter(), 12, 0.3, 0.05);
            }
        }
        if (hasWraithweaveSet(player)) {
            // Spectral Step: swift on snow and ice.
            BlockState below = level.getBlockState(player.getOnPos());
            if (player.tickCount % 10 == 0 && (below.is(BlockTags.SNOW) || below.is(BlockTags.ICE))) {
                player.addEffect(new MobEffectInstance(MobEffects.SPEED, 30, 0, false, false, true));
            }
            // Fade: at low health, vanish into the snow (90 s cooldown).
            if (player.getHealth() < player.getMaxHealth() * 0.3f) {
                long now = level.getGameTime();
                if (FADE_READY.getOrDefault(player.getUUID(), 0L) <= now) {
                    FADE_READY.put(player.getUUID(), now + 1800);
                    player.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 100, 0, false, false, true));
                    player.addEffect(new MobEffectInstance(MobEffects.SPEED, 100, 1, false, false, true));
                    FX.burst(level, ModParticles.WRAITH_WISP.get(), player.getBoundingBox().getCenter(), 40, 0.5, 0.05);
                    FX.burst(level, ParticleTypes.SNOWFLAKE, player.getBoundingBox().getCenter(), 30, 0.6, 0.05);
                    level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.WRAITH_AMBIENT.get(), SoundSource.PLAYERS, 1.0f, 1.4f);
                    for (var mob : level.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, player.getBoundingBox().inflate(16), m -> m.getTarget() == player)) {
                        mob.setTarget(null);
                    }
                }
            }
        }
    }
}
