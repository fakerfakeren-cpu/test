package com.oathbound.entity.mob;

import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * A hound of the Gloaming. Veilhounds hunt in packs: they circle their prey at a distance, howling to bring
 * the rest of the pack, then lunge in one at a time from every side.
 */
public class VeilhoundEntity extends Monster {
    private static final EntityDataAccessor<Boolean> LUNGING = SynchedEntityData.defineId(VeilhoundEntity.class, EntityDataSerializers.BOOLEAN);
    private int circle = 60;
    private int lungeTicks;
    private boolean howled;

    public VeilhoundEntity(EntityType<? extends VeilhoundEntity> type, Level level) {
        super(type, level);
        this.xpReward = 9;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 28.0)
            .add(Attributes.ATTACK_DAMAGE, 6.0)
            .add(Attributes.MOVEMENT_SPEED, 0.38)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.STEP_HEIGHT, 1.1);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(LUNGING, false);
    }

    public boolean isLunging() {
        return entityData.get(LUNGING);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8) {
            @Override
            public boolean canUse() {
                return getTarget() == null && super.canUse();
            }
        });
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        if (t == null) {
            howled = false;
            return;
        }
        if (!howled) {
            howled = true;
            level.playSound(null, getX(), getY(), getZ(), ModSounds.VEILHOUND_HOWL.get(), SoundSource.HOSTILE, 2.5f, 0.9f + random.nextFloat() * 0.2f);
            for (VeilhoundEntity v : level.getEntitiesOfClass(VeilhoundEntity.class, getBoundingBox().inflate(24), v -> v != this && v.getTarget() == null)) {
                v.setTarget(t);
                v.howled = true;
                v.circle = 40 + random.nextInt(60);
            }
        }
        getLookControl().setLookAt(t, 30, 30);
        if (lungeTicks > 0) {
            lungeTicks--;
            if (distanceToSqr(t) < 2.2 * 2.2 && isLunging()) {
                doHurtTarget(level, t);
                entityData.set(LUNGING, false);
            }
            if (lungeTicks == 0) {
                entityData.set(LUNGING, false);
                circle = 50 + random.nextInt(50);
            }
            return;
        }
        if (--circle > 0) {
            double a = tickCount * 0.04 + getId() * 2.1;
            Vec3 want = t.position().add(Math.cos(a) * 6, 0, Math.sin(a) * 6);
            getNavigation().moveTo(want.x, want.y, want.z, 1.1);
            if (tickCount % 30 == 0 && random.nextInt(3) == 0) level.playSound(null, getX(), getY(), getZ(), ModSounds.VEILHOUND_GROWL.get(), SoundSource.HOSTILE, 1.0f, 1.0f);
        } else if (onGround()) {
            getNavigation().stop();
            Vec3 leap = t.position().subtract(position()).normalize();
            double dist = Math.sqrt(distanceToSqr(t));
            setDeltaMovement(leap.x * Math.min(1.4, 0.3 + dist * 0.14), 0.45, leap.z * Math.min(1.4, 0.3 + dist * 0.14));
            hurtMarked = true;
            entityData.set(LUNGING, true);
            lungeTicks = 16;
            level.playSound(null, getX(), getY(), getZ(), ModSounds.VEILHOUND_GROWL.get(), SoundSource.HOSTILE, 1.5f, 1.4f);
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(2) == 0) {
            level().addParticle(ModParticles.GLOAM_WISP.get(), getRandomX(0.6), getY() + 0.4 + random.nextDouble() * 0.6, getRandomZ(0.6), 0, 0.01, 0);
        }
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.VEILHOUND_GROWL.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.VEILHOUND_GROWL.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.VEILHOUND_HOWL.get();
    }

    @Override
    public float getVoicePitch() {
        return 0.7f;
    }
}
