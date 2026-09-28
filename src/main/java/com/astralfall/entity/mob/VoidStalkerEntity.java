package com.astralfall.entity.mob;

import com.astralfall.event.ArmorEffects;
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
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Tall, thin and wrong. A Void Stalker cannot move while anyone is looking at it, but the moment you
 * turn away it sprints at you, and if you ignore it long enough it simply appears behind you.
 * Starlight weapons burn it; Voidwalker armour makes you invisible to it.
 */
public class VoidStalkerEntity extends Monster {
    private static final EntityDataAccessor<Boolean> FROZEN = SynchedEntityData.defineId(VoidStalkerEntity.class, EntityDataSerializers.BOOLEAN);
    private int unseenTicks;
    private int blinkCooldown = 100;
    private int creepCooldown;

    public VoidStalkerEntity(EntityType<? extends VoidStalkerEntity> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 40.0)
            .add(Attributes.ATTACK_DAMAGE, 8.0)
            .add(Attributes.MOVEMENT_SPEED, 0.34)
            .add(Attributes.FOLLOW_RANGE, 48.0)
            .add(Attributes.ARMOR, 4.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.5)
            .add(Attributes.STEP_HEIGHT, 1.1);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(FROZEN, false);
    }

    public boolean isFrozen() {
        return entityData.get(FROZEN);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.5, false) {
            @Override
            public boolean canUse() {
                return !isFrozen() && super.canUse();
            }

            @Override
            public boolean canContinueToUse() {
                return !isFrozen() && super.canContinueToUse();
            }
        });
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8) {
            @Override
            public boolean canUse() {
                return !isFrozen() && super.canUse();
            }
        });
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false,
            (target, level) -> !ArmorEffects.hasVoidwalkerSet(target)));
    }

    /** True if any survival player within 64 blocks is looking roughly at us with line of sight. */
    private boolean isWatched(ServerLevel level) {
        for (Player p : level.players()) {
            if (p.isSpectator() || p.isCreative() || p.distanceToSqr(this) > 64 * 64) continue;
            Vec3 look = p.getViewVector(1.0f).normalize();
            Vec3 to = new Vec3(getX() - p.getX(), getEyeY() - 0.6 - p.getEyeY(), getZ() - p.getZ());
            double dist = to.length();
            if (dist < 0.1) return true;
            double dot = look.dot(to.scale(1.0 / dist));
            if (dot > 0.8 && p.hasLineOfSight(this)) return true;
        }
        return false;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        boolean watched = isWatched(level);
        entityData.set(FROZEN, watched);
        if (watched) {
            navigation.stop();
            setDeltaMovement(0, Math.min(0, getDeltaMovement().y), 0);
            unseenTicks = 0;
            LivingEntity target = getTarget();
            if (target != null && --creepCooldown <= 0 && distanceToSqr(target) < 14 * 14) {
                level.playSound(null, getX(), getY(), getZ(), ModSounds.STALKER_AMBIENT.get(), SoundSource.HOSTILE, 1.2f, 0.8f + random.nextFloat() * 0.3f);
                creepCooldown = 80 + random.nextInt(80);
            }
        } else {
            unseenTicks++;
            LivingEntity target = getTarget();
            if (--blinkCooldown <= 0 && target != null && unseenTicks > 50 && distanceToSqr(target) > 10 * 10 && distanceToSqr(target) < 48 * 48) {
                blinkBehind(level, target);
            }
        }
        if (!isPersistenceRequired() && !level.isDarkOutside() && level.canSeeSky(blockPosition()) && random.nextInt(80) == 0) {
            FX.burst(level, ModParticles.VOID_MOTE.get(), getBoundingBox().getCenter(), 40, 0.4, 0.1);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.STALKER_BLINK.get(), SoundSource.HOSTILE, 1.0f, 0.6f);
            discard();
        }
    }

    private void blinkBehind(ServerLevel level, LivingEntity target) {
        Vec3 back = target.getViewVector(1.0f).multiply(1, 0, 1).normalize().scale(-3.0);
        int x = (int) Math.floor(target.getX() + back.x), z = (int) Math.floor(target.getZ() + back.z);
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        if (Math.abs(y - target.getY()) > 4) y = (int) Math.floor(target.getY());
        BlockPos dest = new BlockPos(x, y, z);
        if (!level.getBlockState(dest).isAir() || !level.getBlockState(dest.above()).isAir() || !level.getBlockState(dest.above(2)).isAir()) return;
        FX.burst(level, ModParticles.VOID_MOTE.get(), getBoundingBox().getCenter(), 30, 0.4, 0.1);
        FX.burst(level, ParticleTypes.REVERSE_PORTAL, getBoundingBox().getCenter(), 30, 0.3, 0.2);
        teleportTo(dest.getX() + 0.5, dest.getY(), dest.getZ() + 0.5);
        lookAt(target, 180f, 180f);
        FX.burst(level, ModParticles.VOID_MOTE.get(), getBoundingBox().getCenter(), 30, 0.4, 0.1);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.STALKER_BLINK.get(), SoundSource.HOSTILE, 1.5f, 1.0f);
        blinkCooldown = 200 + random.nextInt(120);
        unseenTicks = 0;
    }

    @Override
    public boolean doHurtTarget(ServerLevel level, Entity target) {
        boolean hit = super.doHurtTarget(level, target);
        if (hit && target instanceof LivingEntity living) {
            living.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 80, 0), this);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.STALKER_SCREAM.get(), SoundSource.HOSTILE, 1.4f, 0.9f + random.nextFloat() * 0.2f);
        }
        return hit;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(3) == 0) {
            level().addParticle(ModParticles.VOID_MOTE.get(), getRandomX(0.6), getRandomY(), getRandomZ(0.6), 0, -0.02, 0);
        }
    }

    @Override
    public void push(Entity entity) {
        if (!isFrozen()) super.push(entity);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.ENDERMAN_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.STALKER_SCREAM.get();
    }

    @Override
    protected float getSoundVolume() {
        return 1.2f;
    }

    @Override
    public float getVoicePitch() {
        return 0.6f;
    }
}
