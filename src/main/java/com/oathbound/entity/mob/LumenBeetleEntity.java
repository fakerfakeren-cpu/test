package com.oathbound.entity.mob;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** A thumb-sized beetle that carries its own lantern through the caves; miners follow them to lumenite. */
public class LumenBeetleEntity extends WildAnimal {
    public LumenBeetleEntity(EntityType<? extends LumenBeetleEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 3.0).add(Attributes.MOVEMENT_SPEED, 0.2);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return true;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(8) == 0) {
            level().addParticle(ModParticles.LUMEN_MOTE.get(), getX(), getY() + 0.2, getZ(), 0, 0.01, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.BEETLE_CLICK.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.BEETLE_CLICK.get();
    }

    @Override
    protected float getSoundVolume() {
        return 0.4f;
    }
}
