package com.astralfall.entity.mob;

import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * A floating eye trailing tentacles. It locks on, charges its gaze for two seconds and fires a
 * gravity beam that hurls its victim into the air. Break line of sight to dodge.
 */
public class VoidGazerEntity extends Monster {
    public static final int CHARGE_TIME = 36;
    private static final EntityDataAccessor<Integer> CHARGE = SynchedEntityData.defineId(VoidGazerEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> BEAM_TARGET = SynchedEntityData.defineId(VoidGazerEntity.class, EntityDataSerializers.INT);

    public VoidGazerEntity(EntityType<? extends VoidGazerEntity> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 10, true);
        this.setNoGravity(true);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 26.0)
            .add(Attributes.FLYING_SPEED, 0.45)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.ARMOR, 2.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CHARGE, 0);
        builder.define(BEAM_TARGET, -1);
    }

    public int getCharge() {
        return entityData.get(CHARGE);
    }

    public Entity getBeamTarget() {
        int id = entityData.get(BEAM_TARGET);
        return id < 0 ? null : level().getEntity(id);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
        nav.setCanFloat(true);
        return nav;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(2, new GazeAttackGoal(this));
        goalSelector.addGoal(5, new WaterAvoidingRandomFlyingGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0f));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide()) {
            if (random.nextInt(3) == 0) level().addParticle(ModParticles.VOID_MOTE.get(), getRandomX(0.8), getY() + random.nextDouble() * 0.6, getRandomZ(0.8), 0, -0.04, 0);
            Entity t = getBeamTarget();
            int charge = getCharge();
            if (t != null && charge > 0) {
                Vec3 eye = getEyePosition();
                Vec3 to = t.getBoundingBox().getCenter();
                Vec3 d = to.subtract(eye);
                double len = d.length();
                int n = (int) (len * 1.5);
                for (int i = 0; i < n; i += 2) {
                    if (random.nextFloat() > charge / (float) CHARGE_TIME) continue;
                    Vec3 p = eye.add(d.scale(i / (double) n));
                    level().addParticle(ModParticles.VOID_MOTE.get(), p.x, p.y, p.z, 0, 0, 0);
                }
                level().addParticle(ParticleTypes.PORTAL, eye.x, eye.y, eye.z, (random.nextDouble() - 0.5), (random.nextDouble() - 0.5), (random.nextDouble() - 0.5));
            }
        }
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {}

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.PHANTOM_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.PHANTOM_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.PHANTOM_DEATH;
    }

    @Override
    public float getVoicePitch() {
        return 0.5f;
    }

    static final class GazeAttackGoal extends Goal {
        private final VoidGazerEntity gazer;
        private int cooldown = 40;
        private int charge;

        GazeAttackGoal(VoidGazerEntity gazer) {
            this.gazer = gazer;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = gazer.getTarget();
            return t != null && t.isAlive() && gazer.distanceToSqr(t) < 28 * 28;
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void stop() {
            charge = 0;
            gazer.entityData.set(CHARGE, 0);
            gazer.entityData.set(BEAM_TARGET, -1);
        }

        @Override
        public void tick() {
            LivingEntity t = gazer.getTarget();
            if (t == null) return;
            ServerLevel level = (ServerLevel) gazer.level();
            gazer.getLookControl().setLookAt(t, 40f, 40f);
            double d = gazer.distanceToSqr(t);
            if (charge == 0) {
                double orbit = gazer.tickCount * 0.03 + gazer.getId();
                Vec3 want = t.position().add(Math.cos(orbit) * 8, 3.5, Math.sin(orbit) * 8);
                gazer.getMoveControl().setWantedPosition(want.x, want.y, want.z, 1.0);
            }
            boolean sees = gazer.hasLineOfSight(t);
            if (charge > 0) {
                charge++;
                gazer.entityData.set(CHARGE, charge);
                if (!sees) {
                    stop();
                    cooldown = 30;
                    return;
                }
                if (charge >= CHARGE_TIME) {
                    fire(level, t);
                    stop();
                    cooldown = 70 + gazer.getRandom().nextInt(40);
                }
            } else if (--cooldown <= 0 && sees && d < 22 * 22) {
                charge = 1;
                gazer.entityData.set(BEAM_TARGET, t.getId());
                level.playSound(null, gazer.getX(), gazer.getY(), gazer.getZ(), ModSounds.GAZER_CHARGE.get(), SoundSource.HOSTILE, 1.6f, 1.0f);
            }
        }

        private void fire(ServerLevel level, LivingEntity t) {
            Vec3 eye = gazer.getEyePosition();
            FX.line(level, ModParticles.VOID_MOTE.get(), eye, t.getBoundingBox().getCenter(), 0.3);
            FX.line(level, ParticleTypes.END_ROD, eye, t.getBoundingBox().getCenter(), 0.8);
            FX.burst(level, ParticleTypes.REVERSE_PORTAL, t.getBoundingBox().getCenter(), 40, 0.4, 0.3);
            t.hurtServer(level, level.damageSources().indirectMagic(gazer, gazer), 6.0f);
            t.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 50, 1), gazer);
            level.playSound(null, gazer.getX(), gazer.getY(), gazer.getZ(), ModSounds.GAZER_BEAM.get(), SoundSource.HOSTILE, 2.0f, 1.0f);
        }
    }
}
