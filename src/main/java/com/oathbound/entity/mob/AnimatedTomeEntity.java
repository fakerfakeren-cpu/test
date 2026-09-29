package com.oathbound.entity.mob;

import com.oathbound.entity.projectile.GlyphBoltEntity;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.core.BlockPos;
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
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * A spellbook from Veyl's library that learned to fly. It flaps erratically around intruders, snapping its
 * pages and loosing glyph bolts that sting and weaken.
 */
public class AnimatedTomeEntity extends Monster {
    private static final EntityDataAccessor<Integer> CASTING = SynchedEntityData.defineId(AnimatedTomeEntity.class, EntityDataSerializers.INT);
    private int reload = 40;
    private Vec3 wander = Vec3.ZERO;

    public AnimatedTomeEntity(EntityType<? extends AnimatedTomeEntity> type, Level level) {
        super(type, level);
        setNoGravity(true);
        this.xpReward = 6;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 14.0)
            .add(Attributes.ATTACK_DAMAGE, 2.0)
            .add(Attributes.FLYING_SPEED, 0.5)
            .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CASTING, 0);
    }

    public int casting() {
        return entityData.get(CASTING);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        Vec3 want;
        if (t != null) {
            double a = tickCount * 0.09 + getId() * 1.3;
            want = t.position().add(Math.cos(a) * 4.5, 2 + Math.sin(tickCount * 0.21) * 1.2, Math.sin(a) * 4.5);
            getLookControl().setLookAt(t, 40, 40);
            int c = casting();
            if (c > 0) {
                entityData.set(CASTING, c + 1);
                if (c == 12) {
                    Vec3 from = position().add(0, 0.3, 0);
                    Vec3 aim = t.getEyePosition().subtract(from).normalize();
                    GlyphBoltEntity.shoot(level, this, from, aim.scale(0.9));
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.TOME_CAST.get(), SoundSource.HOSTILE, 1.0f, 1.0f + random.nextFloat() * 0.3f);
                    entityData.set(CASTING, 0);
                    reload = 35 + random.nextInt(20);
                }
            } else if (--reload <= 0 && hasLineOfSight(t)) {
                entityData.set(CASTING, 1);
            }
        } else {
            if (wander.equals(Vec3.ZERO) || random.nextInt(40) == 0) wander = position().add(random.nextInt(9) - 4, random.nextInt(3) - 1, random.nextInt(9) - 4);
            want = wander;
        }
        Vec3 d = want.subtract(position());
        Vec3 jitter = new Vec3(random.nextGaussian() * 0.02, random.nextGaussian() * 0.03, random.nextGaussian() * 0.02);
        setDeltaMovement(getDeltaMovement().scale(0.85).add(d.normalize().scale(0.05 * Math.min(1, d.length()))).add(jitter));
        if (t == null) {
            Vec3 v = getDeltaMovement();
            float yaw = (float) (Math.atan2(v.z, v.x) * 180 / Math.PI) - 90f;
            setYRot(yaw);
            yBodyRot = yaw;
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(3) == 0) {
            level().addParticle(net.minecraft.core.particles.ParticleTypes.ENCHANT, getRandomX(0.6), getY() + 0.3, getRandomZ(0.6), 0, 0.1, 0);
            if (casting() > 0) level().addParticle(ModParticles.ARCANE_GLYPH.get(), getX(), getY() + 0.5, getZ(), 0, 0.03, 0);
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
        return ModSounds.TOME_FLUTTER.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.TOME_CAST.get();
    }
}
