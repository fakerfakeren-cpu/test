package com.oathbound.entity.mob;

import com.oathbound.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** A great slow tortoise with a garden on its back. Struck, it draws into its shell and shrugs off most blows. */
public class MossbackTortoiseEntity extends WildAnimal {
    public MossbackTortoiseEntity(EntityType<? extends MossbackTortoiseEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 30.0).add(Attributes.MOVEMENT_SPEED, 0.12).add(Attributes.ARMOR, 10.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.8);
    }

    @Override
    protected double wanderSpeed() {
        return 0.8;
    }

    @Override
    protected float actionChance() {
        return 0.0015f;
    }

    @Override
    protected int actionLength() {
        return 120;
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (fauna$action()) amount *= 0.2f;
        boolean hurt = super.hurtServer(level, source, amount);
        if (hurt && isAlive()) setActing(100);
        return hurt;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.TORTOISE_HISS.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.TORTOISE_HISS.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 400;
    }

    @Override
    public float getVoicePitch() {
        return 0.7f;
    }
}
