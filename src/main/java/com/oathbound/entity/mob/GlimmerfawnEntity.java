package com.oathbound.entity.mob;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** A slender deer of the old woods. Its dapples and antler-tips shine at night; it bolts from anyone who does not creep. */
public class GlimmerfawnEntity extends WildAnimal {
    public GlimmerfawnEntity(EntityType<? extends GlimmerfawnEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 14.0).add(Attributes.MOVEMENT_SPEED, 0.28).add(Attributes.STEP_HEIGHT, 1.1);
    }

    @Override
    protected boolean shy() {
        return true;
    }

    @Override
    protected double wanderSpeed() {
        return 1.1;
    }

    @Override
    protected int actionLength() {
        return 80;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && level().isDarkOutside() && random.nextInt(6) == 0) {
            level().addParticle(ModParticles.LUMEN_MOTE.get(), getRandomX(0.6), getY() + 1.6 + random.nextDouble() * 0.5, getRandomZ(0.6), 0, 0.01, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.FAWN_CALL.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.FAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.FAWN_HURT.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 240;
    }
}
