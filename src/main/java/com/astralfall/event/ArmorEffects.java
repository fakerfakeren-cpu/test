package com.astralfall.event;

import com.astralfall.entity.projectile.StarBoltEntity;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingFallEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Armour set bonuses:
 * <ul>
 *   <li>Starmetal: immune to fall damage, and hard landings release a Meteor Landing shockwave.</li>
 *   <li>Voidwalker: night vision, Void Stalkers ignore you, and sneaking in mid-air blinks you forward.</li>
 *   <li>Crown of Astraeus: rains golden stars on nearby monsters.</li>
 *   <li>Nebula Wings: leave a nebula trail while gliding; sneak mid-glide for a Nebula Boost.</li>
 * </ul>
 */
public final class ArmorEffects {
    private static final Map<UUID, Boolean> WAS_SNEAKING = new HashMap<>();
    private static final Map<UUID, Long> BLINK_READY = new HashMap<>();

    private ArmorEffects() {}

    private static boolean full(LivingEntity e, Item head, Item chest, Item legs, Item feet) {
        return e.getItemBySlot(EquipmentSlot.HEAD).is(head) && e.getItemBySlot(EquipmentSlot.CHEST).is(chest)
            && e.getItemBySlot(EquipmentSlot.LEGS).is(legs) && e.getItemBySlot(EquipmentSlot.FEET).is(feet);
    }

    public static boolean hasStarmetalSet(LivingEntity e) {
        return full(e, ModItems.STARMETAL_HELMET.get(), ModItems.STARMETAL_CHESTPLATE.get(), ModItems.STARMETAL_LEGGINGS.get(), ModItems.STARMETAL_BOOTS.get());
    }

    public static boolean hasVoidwalkerSet(LivingEntity e) {
        return full(e, ModItems.VOIDWALKER_HELMET.get(), ModItems.VOIDWALKER_CHESTPLATE.get(), ModItems.VOIDWALKER_LEGGINGS.get(), ModItems.VOIDWALKER_BOOTS.get());
    }

    public static void onPlayerTick(Player player) {
        if (!(player.level() instanceof ServerLevel level)) return;
        GravityGauntletHandler.onPlayerTick(player);

        boolean voidSet = hasVoidwalkerSet(player);
        boolean sneaking = player.isShiftKeyDown();
        boolean was = WAS_SNEAKING.getOrDefault(player.getUUID(), false);
        WAS_SNEAKING.put(player.getUUID(), sneaking);
        if (voidSet) {
            if (player.tickCount % 80 == 0) player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 320, 0, true, false, true));
            if (sneaking && !was && !player.onGround() && !player.getAbilities().flying && !player.isFallFlying()) {
                long now = level.getGameTime();
                if (now >= BLINK_READY.getOrDefault(player.getUUID(), 0L)) {
                    blink(level, player);
                    BLINK_READY.put(player.getUUID(), now + 40);
                }
            }
        }

        if (player.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.CROWN_OF_ASTRAEUS.get())) {
            if (player.tickCount % 80 == 0) player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 320, 0, true, false, true));
            if (player.tickCount % 50 == 0) {
                LivingEntity target = null;
                double best = 14 * 14;
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(14), e -> e instanceof Enemy && e.isAlive())) {
                    double d = e.distanceToSqr(player);
                    if (d < best && player.hasLineOfSight(e)) {
                        best = d;
                        target = e;
                    }
                }
                if (target != null) {
                    Vec3 from = player.position().add(0, player.getBbHeight() + 0.6, 0);
                    StarBoltEntity.shoot(level, player, from, target.getBoundingBox().getCenter().subtract(from), 2, 6.0f, target);
                    level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.STAR_BOLT.get(), SoundSource.PLAYERS, 0.7f, 1.6f);
                }
            }
        }

        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (player.isFallFlying() && chest.is(ModItems.NEBULA_WINGS.get())) {
            if (player.tickCount % 2 == 0) {
                Vec3 back = player.position().add(player.getLookAngle().scale(-1.0)).add(0, 0.6, 0);
                FX.burst(level, ModParticles.VOID_MOTE.get(), back, 2, 0.3, 0.0);
                FX.burst(level, ModParticles.STAR_SPARKLE.get(), back, 1, 0.4, 0.0);
            }
            // Nebula Boost: sneak mid-glide for a firework-free burst of speed.
            if (sneaking && !was && !player.getCooldowns().isOnCooldown(chest)) {
                Vec3 look = player.getLookAngle();
                player.setDeltaMovement(player.getDeltaMovement().scale(0.35).add(look.scale(1.9)));
                player.hurtMarked = true;
                player.getCooldowns().addCooldown(chest, 80);
                Vec3 at = player.position().add(0, 0.6, 0);
                FX.burst(level, ModParticles.STAR_SPARKLE.get(), at, 36, 0.7, 0.25);
                FX.ring(level, ModParticles.VOID_MOTE.get(), at.subtract(look.scale(1.5)), 1.6, 28, 0.08);
                level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.VOID_BLINK.get(), SoundSource.PLAYERS, 1.0f, 1.5f);
                level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.STAR_SLASH.get(), SoundSource.PLAYERS, 0.8f, 0.7f);
                chest.hurtAndBreak(2, player, EquipmentSlot.CHEST);
            }
        }
    }

    private static void blink(ServerLevel level, Player player) {
        Vec3 look = player.getLookAngle();
        Vec3 dir = new Vec3(look.x, Math.max(-0.2, Math.min(0.4, look.y)), look.z).normalize();
        Vec3 start = player.position();
        for (double d = 8; d >= 2; d -= 0.5) {
            Vec3 offset = dir.scale(d);
            if (level.noCollision(player, player.getBoundingBox().move(offset))) {
                FX.burst(level, ModParticles.VOID_MOTE.get(), start.add(0, 1, 0), 25, 0.3, 0.1);
                FX.line(level, ParticleTypes.REVERSE_PORTAL, start.add(0, 1, 0), start.add(offset).add(0, 1, 0), 0.5);
                player.teleportTo(start.x + offset.x, start.y + offset.y, start.z + offset.z);
                player.resetFallDistance();
                FX.burst(level, ModParticles.VOID_MOTE.get(), player.position().add(0, 1, 0), 25, 0.3, 0.1);
                level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.VOID_BLINK.get(), SoundSource.PLAYERS, 1.0f, 1.0f);
                return;
            }
        }
    }

    public static void onFall(LivingFallEvent event) {
        LivingEntity e = event.getEntity();
        if (!hasStarmetalSet(e)) return;
        double distance = event.getDistance();
        event.setDamageMultiplier(0f);
        if (distance > 5 && e.level() instanceof ServerLevel level) {
            Vec3 c = e.position();
            double radius = Math.min(8, 2 + distance * 0.3);
            float damage = (float) Math.min(24, 4 + distance * 0.8);
            level.playSound(null, c.x, c.y, c.z, ModSounds.SHOCKWAVE.get(), SoundSource.PLAYERS, 2.0f, 1.0f);
            FX.ring(level, ModParticles.COMET_TRAIL.get(), c.add(0, 0.2, 0), radius, 40, 0.05);
            FX.ring(level, ParticleTypes.EXPLOSION, c.add(0, 0.2, 0), radius * 0.6, 8, 0);
            FX.burst(level, ParticleTypes.LAVA, c, 10, 0.5, 0.2);
            for (LivingEntity o : level.getEntitiesOfClass(LivingEntity.class, e.getBoundingBox().inflate(radius, 2, radius), o -> o != e && o.isAlive())) {
                if (o instanceof net.minecraft.world.entity.TamableAnimal pet && e instanceof Player p && pet.isOwnedBy(p)) continue;
                if (o instanceof Player) continue;
                o.hurtServer(level, e instanceof Player p ? level.damageSources().playerAttack(p) : level.damageSources().mobAttack(e), damage);
                Vec3 away = o.position().subtract(c).multiply(1, 0, 1).normalize();
                o.setDeltaMovement(away.scale(1.0).add(0, 0.6, 0));
                o.hurtMarked = true;
            }
        }
    }
}
