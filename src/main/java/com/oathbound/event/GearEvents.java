package com.oathbound.event;

import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModTags;
import com.oathbound.registry.ModWorldgen;
import com.oathbound.util.Vfx;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.RegistryObject;

import java.util.List;

/**
 * The five gear tiers: full-set bonuses (ticked once a second) and the signature weapons' strikes.
 * Tidebronze thrives in water, Runesilver turns spells, Gravegold wards off the dead, Duskiron grows
 * strong in the dark and Dawnsteel drinks the sun.
 */
public final class GearEvents {
    public enum Tier {
        TIDEBRONZE(ModItems.TIDEBRONZE_HELMET, ModItems.TIDEBRONZE_CHESTPLATE, ModItems.TIDEBRONZE_LEGGINGS, ModItems.TIDEBRONZE_BOOTS),
        RUNESILVER(ModItems.RUNESILVER_HELMET, ModItems.RUNESILVER_CHESTPLATE, ModItems.RUNESILVER_LEGGINGS, ModItems.RUNESILVER_BOOTS),
        GRAVEGOLD(ModItems.GRAVEGOLD_HELMET, ModItems.GRAVEGOLD_CHESTPLATE, ModItems.GRAVEGOLD_LEGGINGS, ModItems.GRAVEGOLD_BOOTS),
        DUSKIRON(ModItems.DUSKIRON_HELMET, ModItems.DUSKIRON_CHESTPLATE, ModItems.DUSKIRON_LEGGINGS, ModItems.DUSKIRON_BOOTS),
        DAWNSTEEL(ModItems.DAWNSTEEL_HELMET, ModItems.DAWNSTEEL_CHESTPLATE, ModItems.DAWNSTEEL_LEGGINGS, ModItems.DAWNSTEEL_BOOTS);

        private final List<RegistryObject<Item>> pieces;

        @SafeVarargs
        Tier(RegistryObject<Item>... pieces) {
            this.pieces = List.of(pieces);
        }
    }

    private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

    private GearEvents() {}

    public static boolean fullSet(LivingEntity e, Tier tier) {
        for (int i = 0; i < 4; i++) if (!e.getItemBySlot(SLOTS[i]).is(tier.pieces.get(i).get())) return false;
        return true;
    }

    private static void keep(Player p, net.minecraft.core.Holder<net.minecraft.world.effect.MobEffect> effect, int amplifier) {
        p.addEffect(new MobEffectInstance(effect, 60, amplifier, true, false, true));
    }

    /** Once a second. */
    public static void tick(ServerPlayer p, ServerLevel level) {
        if (fullSet(p, Tier.TIDEBRONZE) && p.isInWater()) {
            keep(p, MobEffects.CONDUIT_POWER, 0);
            keep(p, MobEffects.DOLPHINS_GRACE, 0);
        }
        if (fullSet(p, Tier.DUSKIRON)) {
            if (level.getMaxLocalRawBrightness(p.blockPosition()) <= 7) {
                keep(p, MobEffects.SPEED, 0);
                keep(p, MobEffects.STRENGTH, 0);
            }
            if (level.dimension() == ModWorldgen.GLOAMING) p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 320, 0, true, false, true));
        }
        if (fullSet(p, Tier.DAWNSTEEL) && level.isBrightOutside() && level.canSeeSky(p.blockPosition())) {
            keep(p, MobEffects.REGENERATION, 0);
            keep(p, MobEffects.FIRE_RESISTANCE, 0);
            if (p.tickCount % 60 == 0) Vfx.burst(level, ModParticles.SUNBURST.get(), p.position().add(0, 1.2, 0), 4, 0.4, 0.02);
        }
    }

    /** A player's melee blow with their main-hand weapon. */
    public static float outgoing(ServerLevel level, Player attacker, LivingEntity victim, float amount) {
        ItemStack weapon = attacker.getMainHandItem();
        var centre = victim.getBoundingBox().getCenter();
        boolean undead = victim.typeHolder().is(EntityTypeTags.UNDEAD);
        if (weapon.is(ModItems.TIDEBRONZE_GLADIUS.get()) && attacker.isInWaterOrRain()) {
            amount *= 1.5f;
            Vfx.burst(level, ModParticles.TIDE.get(), centre, 14, 0.3, 0.12);
            level.playSound(null, victim.getX(), victim.getY(), victim.getZ(), SoundEvents.PLAYER_SPLASH, SoundSource.PLAYERS, 0.6f, 1.4f);
        } else if (weapon.is(ModItems.RUNESILVER_RAPIER.get())) {
            amount += 4f;
            Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), centre, 6, 0.25, 0.05);
        } else if (weapon.is(ModItems.GRAVEGOLD_KHOPESH.get()) && undead) {
            amount *= 1.6f;
            Vfx.burst(level, ModParticles.SPIRIT.get(), centre, 12, 0.3, 0.08);
        } else if (weapon.is(ModItems.DUSKIRON_GLAIVE.get()) && level.getMaxLocalRawBrightness(victim.blockPosition()) <= 7) {
            amount *= 1.3f;
            Vfx.line(level, ModParticles.GLOAM_WISP.get(), attacker.position().add(0, 1.2, 0), centre, 0.35);
        } else if (weapon.is(ModItems.DAWNSTEEL_GREATSWORD.get()) && (undead || victim.typeHolder().is(ModTags.GLOAM_CREATURES))) {
            amount *= 1.5f;
            victim.igniteForSeconds(5);
            Vfx.burst(level, ModParticles.SUNBURST.get(), centre, 16, 0.35, 0.12);
        }
        if (undead && fullSet(attacker, Tier.GRAVEGOLD)) amount *= 1.15f;
        return amount;
    }

    /** Damage coming at a player. */
    public static float incoming(Player victim, DamageSource source, float amount) {
        if (fullSet(victim, Tier.RUNESILVER) && source.is(DamageTypeTags.WITCH_RESISTANT_TO)) amount *= 0.6f;
        Entity from = source.getEntity();
        if (from != null && from.typeHolder().is(EntityTypeTags.UNDEAD) && fullSet(victim, Tier.GRAVEGOLD)) amount *= 0.7f;
        return amount;
    }
}
