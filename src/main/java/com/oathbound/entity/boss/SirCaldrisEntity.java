package com.oathbound.entity.boss;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Sir Caldris, the Drowned Knight: first of the seal keepers. His tower shield turns aside every blow that
 * comes from in front of him; strike from the flanks or behind, or split the guard with an axe to stagger him.
 * Moves: anchor swings, a thundering Shield Charge (he is stunned if he slams into a wall), and the Undertow,
 * which drags everyone in before a crushing slam. At half health he calls his drowned squires.
 */
public class SirCaldrisEntity extends KeeperEntity {
    public static final int SWING = 1, CHARGE = 2, UNDERTOW = 3, STUNNED = 4, SQUIRES = 5;
    private static final EntityDataAccessor<Integer> STAGGER = SynchedEntityData.defineId(SirCaldrisEntity.class, EntityDataSerializers.INT);
    private Vec3 chargeDir = Vec3.ZERO;
    private boolean calledSquires;
    private int lastMove;

    public SirCaldrisEntity(EntityType<? extends SirCaldrisEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.BLUE);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 180.0)
            .add(Attributes.ARMOR, 8.0)
            .add(Attributes.ATTACK_DAMAGE, 9.0)
            .add(Attributes.MOVEMENT_SPEED, 0.26)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.9)
            .add(Attributes.STEP_HEIGHT, 1.1);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(STAGGER, 0);
    }

    public int stagger() {
        return entityData.get(STAGGER);
    }

    @Override
    protected String questId() {
        return "caldris";
    }

    @Override
    protected float baseHealth() {
        return 180f;
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        level.playSound(null, getX(), getY(), getZ(), ModSounds.CALDRIS_ROAR.get(), SoundSource.HOSTILE, 3.0f, 1.0f);
        Vfx.burst(level, ParticleTypes.SPLASH, position().add(0, 1, 0), 80, 1.0, 0.3);
        Vfx.ring(level, ModParticles.TIDE.get(), position().add(0, 0.2, 0), 3, 40, 0.1);
    }

    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        if (stagger() > 0) {
            entityData.set(STAGGER, stagger() - 1);
            getNavigation().stop();
            if (tickCount % 4 == 0) Vfx.burst(level, ParticleTypes.CRIT, position().add(0, 2.6, 0), 3, 0.3, 0.05);
            return;
        }
        if (target == null) {
            getNavigation().stop();
            return;
        }
        getLookControl().setLookAt(target, 30f, 30f);
        if (!calledSquires && getHealth() < getMaxHealth() * 0.5f && move() == IDLE) {
            calledSquires = true;
            startMove(SQUIRES);
        }
        int t = moveTicks();
        switch (move()) {
            case IDLE -> {
                double d = distanceToSqr(target);
                if (d > 3.2 * 3.2) getNavigation().moveTo(target, 1.0);
                else getNavigation().stop();
                if (--cooldown <= 0) {
                    int pick;
                    if (d < 3.6 * 3.6) pick = SWING;
                    else pick = random.nextInt(3) == 0 && lastMove != UNDERTOW ? UNDERTOW : CHARGE;
                    if (pick == lastMove && pick != SWING) pick = pick == CHARGE ? UNDERTOW : CHARGE;
                    lastMove = pick;
                    startMove(pick);
                    getNavigation().stop();
                }
            }
            case SWING -> {
                if (t == 8) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_SLASH.get(), SoundSource.HOSTILE, 1.4f, 0.8f);
                    Vec3 fwd = Vec3.directionFromRotation(0, getYRot());
                    Vfx.burst(level, ParticleTypes.SWEEP_ATTACK, position().add(fwd.scale(2)).add(0, 1.2, 0), 3, 0.6, 0);
                    for (Player p : challengers(level, 4.0)) {
                        Vec3 to = p.position().subtract(position()).normalize();
                        if (to.dot(fwd) > 0.2 && p.distanceTo(this) < 4.2) p.hurtServer(level, damageSources().mobAttack(this), 11f);
                    }
                }
                if (t > 18) endMove(18 + random.nextInt(12));
            }
            case CHARGE -> {
                if (t == 1) {
                    chargeDir = target.position().subtract(position()).multiply(1, 0, 1).normalize();
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.SHIELD_CHARGE.get(), SoundSource.HOSTILE, 2.0f, 0.8f);
                }
                if (t < 16) {
                    setYRot((float) (Mth.atan2(chargeDir.z, chargeDir.x) * Mth.RAD_TO_DEG) - 90f);
                    Vfx.burst(level, ModParticles.TIDE.get(), position().add(0, 1, 0), 3, 0.5, 0.02);
                } else if (t < 32) {
                    Vec3 v = chargeDir.scale(0.85);
                    setDeltaMovement(v.x, getDeltaMovement().y, v.z);
                    Vfx.burst(level, ParticleTypes.SPLASH, position(), 6, 0.4, 0.1);
                    for (Player p : challengers(level, 1.6)) {
                        p.hurtServer(level, damageSources().mobAttack(this), 12f);
                        p.setDeltaMovement(chargeDir.scale(1.6).add(0, 0.5, 0));
                        p.hurtMarked = true;
                    }
                    if (horizontalCollision) {
                        level.playSound(null, getX(), getY(), getZ(), ModSounds.SHIELD_BLOCK.get(), SoundSource.HOSTILE, 2.0f, 0.5f);
                        Vfx.burst(level, ParticleTypes.EXPLOSION, position().add(chargeDir).add(0, 1, 0), 2, 0.3, 0);
                        startMove(STUNNED);
                    }
                } else {
                    endMove(30 + random.nextInt(20));
                }
            }
            case STUNNED -> {
                getNavigation().stop();
                if (t % 4 == 0) Vfx.burst(level, ParticleTypes.CRIT, position().add(0, 2.7, 0), 4, 0.3, 0.05);
                if (t > 60) endMove(10);
            }
            case UNDERTOW -> {
                getNavigation().stop();
                Vec3 c = position();
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.UNDERTOW.get(), SoundSource.HOSTILE, 2.5f, 1.0f);
                if (t < 34) {
                    Vfx.spiralIn(level, ModParticles.TIDE.get(), c.add(0, 0.4, 0), 10, 8, t);
                    Vfx.spiralIn(level, ParticleTypes.BUBBLE, c.add(0, 0.6, 0), 8, 4, t + 2);
                    for (Player p : challengers(level, 12)) {
                        Vec3 pull = c.subtract(p.position()).multiply(1, 0, 1).normalize().scale(0.11);
                        p.setDeltaMovement(p.getDeltaMovement().add(pull));
                        p.hurtMarked = true;
                    }
                } else if (t == 36) {
                    level.playSound(null, getX(), getY(), getZ(), net.minecraft.sounds.SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1.5f, 0.6f);
                    for (int r = 1; r <= 4; r++) Vfx.ring(level, ParticleTypes.SPLASH, c.add(0, 0.2, 0), r, 12 * r, 0.25);
                    Vfx.ring(level, ModParticles.TIDE.get(), c.add(0, 0.2, 0), 4.5, 48, 0.15);
                    for (Player p : challengers(level, 4.5)) {
                        p.hurtServer(level, damageSources().mobAttack(this), 13f);
                        p.setDeltaMovement(p.position().subtract(c).normalize().scale(1.0).add(0, 0.7, 0));
                        p.hurtMarked = true;
                    }
                } else if (t > 50) {
                    endMove(40);
                }
            }
            case SQUIRES -> {
                getNavigation().stop();
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.CALDRIS_ROAR.get(), SoundSource.HOSTILE, 3.0f, 0.8f);
                if (t == 20) {
                    for (int i = 0; i < 3; i++) {
                        Mob m = net.minecraft.world.entity.EntityTypes.DROWNED.create(level, EntitySpawnReason.MOB_SUMMONED);
                        if (m == null) continue;
                        double a = i * Math.PI * 2 / 3;
                        m.snapTo(getX() + Math.cos(a) * 3, getY(), getZ() + Math.sin(a) * 3, random.nextFloat() * 360, 0);
                        m.setTarget(target);
                        m.setPersistenceRequired();
                        level.addFreshEntity(m);
                        Vfx.burst(level, ParticleTypes.SPLASH, m.position().add(0, 1, 0), 40, 0.5, 0.2);
                    }
                }
                if (t > 30) endMove(30);
            }
            default -> endMove(20);
        }
    }

    /** True if the blow comes from within the shield's arc (in front of him). */
    private boolean guarded(Entity attacker) {
        if (attacker == null) return false;
        Vec3 fwd = Vec3.directionFromRotation(0, yBodyRot);
        Vec3 to = attacker.position().subtract(position()).multiply(1, 0, 1).normalize();
        return fwd.dot(to) > 0.35;
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (isSleeping() || stagger() > 0 || move() == STUNNED || source.getEntity() == null) {
            if (stagger() > 0 || move() == STUNNED) amount *= 1.5f;
            return super.hurtServer(level, source, amount);
        }
        Entity attacker = source.getEntity();
        if (guarded(source.getDirectEntity() != null ? source.getDirectEntity() : attacker)) {
            if (attacker instanceof Player p && p.getMainHandItem().is(ItemTags.AXES) && source.getDirectEntity() == p) {
                entityData.set(STAGGER, 70);
                endMove(10);
                level.playSound(null, getX(), getY(), getZ(), ModSounds.SHIELD_BLOCK.get(), SoundSource.HOSTILE, 2.5f, 0.5f);
                Vfx.burst(level, ParticleTypes.CRIT, position().add(0, 1.4, 0), 30, 0.5, 0.3);
                return super.hurtServer(level, source, amount * 0.5f);
            }
            level.playSound(null, getX(), getY(), getZ(), ModSounds.SHIELD_BLOCK.get(), SoundSource.HOSTILE, 1.5f, 0.9f + random.nextFloat() * 0.2f);
            Vec3 fwd = Vec3.directionFromRotation(0, yBodyRot);
            Vfx.burst(level, ModParticles.TIDE.get(), position().add(fwd.scale(0.9)).add(0, 1.3, 0), 10, 0.3, 0.1);
            if (attacker instanceof LivingEntity l && l.distanceTo(this) < 4) {
                Vec3 push = l.position().subtract(position()).multiply(1, 0, 1).normalize().scale(0.7);
                l.setDeltaMovement(l.getDeltaMovement().add(push.x, 0.2, push.z));
                l.hurtMarked = true;
            }
            return false;
        }
        return super.hurtServer(level, source, amount * 1.15f);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : net.minecraft.sounds.SoundEvents.DROWNED_AMBIENT_WATER;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return net.minecraft.sounds.SoundEvents.DROWNED_HURT_WATER;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.CALDRIS_ROAR.get();
    }

    @Override
    public float getVoicePitch() {
        return 0.6f;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && !isSleeping() && random.nextInt(3) == 0) {
            level().addParticle(ModParticles.TIDE.get(), getRandomX(0.8), getY() + random.nextDouble() * 2.4, getRandomZ(0.8), 0, -0.03, 0);
        }
        if (level().isClientSide() && isSleeping() && random.nextInt(8) == 0) {
            level().addParticle(ParticleTypes.BUBBLE_POP, getRandomX(0.6), getY() + 1.5, getRandomZ(0.6), 0, 0.05, 0);
        }
    }

    public BlockPos anchor() {
        return blockPosition();
    }
}
