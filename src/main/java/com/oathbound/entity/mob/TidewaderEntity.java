package com.oathbound.entity.mob;

import com.oathbound.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;

/** A tall grey heron of the chapel shallows. It stands so still that fish forget it, then strikes. */
public class TidewaderEntity extends WildAnimal {
    public TidewaderEntity(EntityType<? extends TidewaderEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 8.0).add(Attributes.MOVEMENT_SPEED, 0.25);
    }

    @Override
    protected boolean shy() {
        return true;
    }

    @Override
    protected float actionChance() {
        return isInWater() || level().getFluidState(blockPosition().below()).isSource() ? 0.02f : 0.002f;
    }

    @Override
    protected int actionLength() {
        return 24;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (fauna$action() && tickCount % 24 == 0 && isInWater() && random.nextInt(6) == 0) {
            spawnAtLocation(level, new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.COD));
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HERON_CROAK.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HERON_CROAK.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 300;
    }
}
