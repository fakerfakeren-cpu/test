package com.oathbound.event;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModTags;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;

/** The three Oathbound status effects. */
public final class OathEffects {
    private OathEffects() {}

    /** You shine with dawnlight: immune to Gloamrot, and nearby Gloam creatures burn. */
    public static class Radiance extends MobEffect {
        public Radiance() {
            super(MobEffectCategory.BENEFICIAL, 0xFFE7A0);
        }

        @Override
        public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {
            return duration % 20 == 0;
        }

        @Override
        public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
            level.sendParticles(ModParticles.SUNBURST.get(), true, false, entity.getX(), entity.getY() + 1.0, entity.getZ(), 3, 0.4, 0.5, 0.4, 0.01);
            for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, entity.getBoundingBox().inflate(5), e -> e != entity && e.typeHolder().is(ModTags.GLOAM_CREATURES))) {
                e.hurtServer(level, level.damageSources().magic(), 2.0f + amplifier);
                e.igniteForSeconds(2);
            }
            return true;
        }
    }

    /** The grey sickness of the Gloaming: a slow withering that only light can hold back. */
    public static class Gloamrot extends MobEffect {
        public Gloamrot() {
            super(MobEffectCategory.HARMFUL, 0x3A2450);
        }

        @Override
        public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {
            return duration % Math.max(10, 50 >> amplifier) == 0;
        }

        @Override
        public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
            if (entity.typeHolder().is(ModTags.GLOAM_CREATURES)) return true;
            level.sendParticles(ModParticles.GLOAM_WISP.get(), true, false, entity.getX(), entity.getY() + 1.0, entity.getZ(), 6, 0.3, 0.5, 0.3, 0.01);
            entity.hurtServer(level, level.damageSources().wither(), 1.0f);
            if (entity instanceof Player p) p.causeFoodExhaustion(0.6f);
            return true;
        }
    }

    /** Branded by the Dawnstring: glowing, and 30% more vulnerable. */
    public static class Sunmark extends MobEffect {
        public Sunmark() {
            super(MobEffectCategory.HARMFUL, 0xFFD34F);
        }

        @Override
        public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {
            return duration % 10 == 0;
        }

        @Override
        public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
            level.sendParticles(ModParticles.SUNBURST.get(), true, false, entity.getX(), entity.getY() + entity.getBbHeight() + 0.3, entity.getZ(), 2, 0.15, 0.1, 0.15, 0.0);
            return true;
        }
    }
}
