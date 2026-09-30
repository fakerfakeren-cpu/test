package com.oathbound.entity.mob;

import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * A hooded shade that drifts over the Gloaming's islands. It circles above its prey, then swoops through it and
 * leaves the cold of the grave behind.
 */
public class ShadeWraithEntity extends Monster implements FaunaEntity {
    private static final EntityDataAccessor<Boolean> SWOOPING = SynchedEntityData.defineId(ShadeWraithEntity.class, EntityDataSerializers.BOOLEAN);
    private int swoop = 60;
    private int swoopTicks;
    private Vec3 wander;

    public ShadeWraithEntity(EntityType<? extends ShadeWraithEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 26.0).add(Attributes.MOVEMENT_SPEED, 0.25).add(Attributes.ATTACK_DAMAGE, 6.0)
            .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(SWOOPING, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(SWOOPING);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        Vec3 want;
        if (t == null) {
            if (wander == null || tickCount % 80 == 0) wander = position().add((random.nextDouble() - 0.5) * 16, (random.nextDouble() - 0.4) * 4, (random.nextDouble() - 0.5) * 16);
            want = wander;
        } else if (swoopTicks > 0) {
            swoopTicks--;
            want = t.position().add(0, 1, 0);
            if (distanceToSqr(t) < 2 * 2) {
                doHurtTarget(level, t);
                t.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 1));
                swoopTicks = 0;
            }
            if (swoopTicks == 0) entityData.set(SWOOPING, false);
        } else {
            double a = tickCount * 0.05 + getId();
            want = t.position().add(Math.cos(a) * 6, 4.5, Math.sin(a) * 6);
            if (--swoop <= 0 && hasLineOfSight(t)) {
                swoop = 70 + random.nextInt(40);
                swoopTicks = 30;
                entityData.set(SWOOPING, true);
                level.playSound(null, getX(), getY(), getZ(), ModSounds.WRAITH_WAIL.get(), SoundSource.HOSTILE, 1.6f, 1.2f);
            }
            getLookControl().setLookAt(t, 30, 30);
        }
        Vec3 to = want.subtract(position());
        double speed = swoopTicks > 0 ? 0.09 : 0.035;
        setDeltaMovement(getDeltaMovement().scale(0.88).add(to.normalize().scale(speed)));
        if (getDeltaMovement().horizontalDistanceSqr() > 1e-4) {
            setYRot((float) (Math.atan2(getDeltaMovement().z, getDeltaMovement().x) * 180 / Math.PI) - 90f);
            yBodyRot = getYRot();
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(2) == 0) {
            level().addParticle(ModParticles.GLOAM_WISP.get(), getRandomX(0.6), getY() + random.nextDouble() * 1.2, getRandomZ(0.6), 0, -0.01, 0);
        }
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.WRAITH_WAIL.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WRAITH_WAIL.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }
}
