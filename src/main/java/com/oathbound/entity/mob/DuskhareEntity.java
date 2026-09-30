package com.oathbound.entity.mob;

import com.oathbound.registry.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** A long-eared hare the colour of dusk, quick to bolt and quicker to vanish into tall grass. */
public class DuskhareEntity extends WildAnimal {
    public DuskhareEntity(EntityType<? extends DuskhareEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 5.0).add(Attributes.MOVEMENT_SPEED, 0.34);
    }

    @Override
    protected boolean shy() {
        return true;
    }

    @Override
    protected double wanderSpeed() {
        return 1.2;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HARE_SQUEAK.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HARE_SQUEAK.get();
    }

    @Override
    public float getVoicePitch() {
        return 1.3f + random.nextFloat() * 0.2f;
    }
}
