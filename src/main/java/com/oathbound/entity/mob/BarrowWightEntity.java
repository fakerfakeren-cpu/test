package com.oathbound.entity.mob;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * A grave-cold spirit of the barrows. It drifts through stone as if it were mist, circles its victim, then
 * swoops through them, leaving Grave Chill (slowness and mining fatigue). It cannot bear the open sun.
 */
public class BarrowWightEntity extends Monster {
    private int swoop;
    private int attackCooldown = 40;
    private Vec3 drift = Vec3.ZERO;

    public BarrowWightEntity(EntityType<? extends BarrowWightEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
        setNoGravity(true);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 26.0)
            .add(Attributes.ATTACK_DAMAGE, 5.0)
            .add(Attributes.MOVEMENT_SPEED, 0.25)
            .add(Attributes.FLYING_SPEED, 0.4)
            .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public void tick() {
        noPhysics = true;
        super.tick();
        noPhysics = true;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        Vec3 want;
        if (t == null) {
            if (drift.equals(Vec3.ZERO) || random.nextInt(60) == 0) drift = position().add(random.nextInt(11) - 5, random.nextInt(5) - 2, random.nextInt(11) - 5);
            want = drift;
        } else if (swoop > 0) {
            swoop--;
            want = t.position().add(0, 1.0, 0);
            if (distanceToSqr(t) < 1.6 * 1.6 && attackCooldown <= 0) {
                if (t.hurtServer(level, damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE))) {
                    t.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 100, 1));
                    t.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 160, 1));
                    level.sendParticles(ModParticles.SPIRIT.get(), true, false, t.getX(), t.getY() + 1, t.getZ(), 20, 0.3, 0.5, 0.3, 0.05);
                }
                attackCooldown = 50;
                swoop = 0;
            }
        } else {
            double a = tickCount * 0.05 + getId();
            want = t.position().add(Math.cos(a) * 5, 2.5 + Math.sin(tickCount * 0.07) * 0.8, Math.sin(a) * 5);
            if (--attackCooldown <= 0 && random.nextInt(20) == 0) {
                swoop = 30;
                playSound(ModSounds.WIGHT_AMBIENT.get(), 1.2f, 1.4f);
            }
        }
        Vec3 d = want.subtract(position());
        double speed = swoop > 0 ? 0.08 : 0.04;
        setDeltaMovement(getDeltaMovement().scale(0.85).add(d.normalize().scale(speed * Math.min(1, d.length()))));
        if (t != null) getLookControl().setLookAt(t, 30, 30);
        Vec3 v = getDeltaMovement();
        if (v.horizontalDistanceSqr() > 1.0E-4) {
            float yaw = (float) (Math.atan2(v.z, v.x) * 180 / Math.PI) - 90f;
            setYRot(yaw);
            yBodyRot = yaw;
        }
        if (tickCount % 20 == 0 && level.isBrightOutside() && level.canSeeSky(blockPosition())) hurtServer(level, damageSources().magic(), 3.0f);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide()) {
            if (random.nextInt(2) == 0) level().addParticle(ModParticles.SPIRIT.get(), getRandomX(0.6), getY() + random.nextDouble() * 1.8, getRandomZ(0.6), 0, -0.02, 0);
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
        return ModSounds.WIGHT_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WIGHT_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.WIGHT_HURT.get();
    }
}
