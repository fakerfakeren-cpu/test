package com.oathbound.entity.mob;

import com.oathbound.registry.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * A heavy forest boar with a ridge of black quills. Left alone it roots and grunts; struck, it lowers its tusks,
 * paws the ground and charges, and the whole sounder charges with it.
 */
public class ThornbackBoarEntity extends PathfinderMob implements FaunaEntity {
    private static final EntityDataAccessor<Boolean> CHARGING = SynchedEntityData.defineId(ThornbackBoarEntity.class, EntityDataSerializers.BOOLEAN);
    private int chargeCooldown = 40;
    private int chargeTicks;

    public ThornbackBoarEntity(EntityType<? extends ThornbackBoarEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 24.0).add(Attributes.MOVEMENT_SPEED, 0.27).add(Attributes.ATTACK_DAMAGE, 5.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.4).add(Attributes.FOLLOW_RANGE, 20.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CHARGING, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(CHARGING);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.3, true));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.9));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 6f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        if (chargeTicks > 0) {
            chargeTicks--;
            if (t != null && distanceToSqr(t) < 2.5 * 2.5) {
                doHurtTarget(level, t);
                Vec3 push = t.position().subtract(position()).normalize().scale(1.3).add(0, 0.4, 0);
                t.push(push.x, push.y, push.z);
                t.hurtMarked = true;
                chargeTicks = 0;
            }
            if (chargeTicks == 0) entityData.set(CHARGING, false);
            return;
        }
        if (t != null && --chargeCooldown <= 0 && onGround() && distanceToSqr(t) > 4 * 4 && distanceToSqr(t) < 14 * 14 && hasLineOfSight(t)) {
            chargeCooldown = 80 + random.nextInt(40);
            chargeTicks = 20;
            entityData.set(CHARGING, true);
            Vec3 dir = t.position().subtract(position()).multiply(1, 0, 1).normalize();
            setDeltaMovement(dir.x * 1.1, 0.1, dir.z * 1.1);
            hurtMarked = true;
            level.playSound(null, getX(), getY(), getZ(), ModSounds.BOAR_SQUEAL.get(), SoundSource.NEUTRAL, 1.4f, 0.8f);
        }
    }

    @Override
    public boolean doHurtTarget(ServerLevel level, Entity target) {
        return super.doHurtTarget(level, target);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.BOAR_GRUNT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.BOAR_SQUEAL.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.BOAR_SQUEAL.get();
    }
}
