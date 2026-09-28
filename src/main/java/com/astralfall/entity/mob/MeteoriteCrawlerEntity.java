package com.astralfall.entity.mob;

import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Six-legged rock beast that hatches from some meteors. It curls into a burning boulder and rolls at
 * you. If it slams into a wall instead it is stunned and takes double damage: dodge, then punish.
 */
public class MeteoriteCrawlerEntity extends Monster {
    public static final int WALK = 0, CURL = 1, ROLL = 2, STUNNED = 3;
    private static final EntityDataAccessor<Integer> STATE = SynchedEntityData.defineId(MeteoriteCrawlerEntity.class, EntityDataSerializers.INT);
    public float rollAngle;
    public float rollAngleO;

    public MeteoriteCrawlerEntity(EntityType<? extends MeteoriteCrawlerEntity> type, Level level) {
        super(type, level);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 34.0)
            .add(Attributes.ARMOR, 10.0)
            .add(Attributes.ATTACK_DAMAGE, 6.0)
            .add(Attributes.MOVEMENT_SPEED, 0.26)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.7)
            .add(Attributes.FOLLOW_RANGE, 32.0)
            .add(Attributes.STEP_HEIGHT, 1.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(STATE, WALK);
    }

    public int getState() {
        return entityData.get(STATE);
    }

    void setState(int s) {
        entityData.set(STATE, s);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new RollChargeGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.1, false) {
            @Override
            public boolean canUse() {
                return getState() == WALK && super.canUse();
            }
        });
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 10.0f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public void tick() {
        super.tick();
        rollAngleO = rollAngle;
        if (getState() == ROLL) rollAngle += 0.55f;
        else if (getState() == CURL) rollAngle += 0.08f;
        else rollAngle *= 0.6f;
        if (level().isClientSide()) {
            if (getState() == ROLL) {
                level().addParticle(ParticleTypes.FLAME, getRandomX(0.7), getY() + 0.2, getRandomZ(0.7), 0, 0.05, 0);
                level().addParticle(ModParticles.COMET_TRAIL.get(), getRandomX(0.7), getY() + 0.4, getRandomZ(0.7), 0, 0.02, 0);
                BlockState below = level().getBlockState(blockPosition().below());
                if (!below.isAir()) level().addParticle(new BlockParticleOption(ParticleTypes.BLOCK, below), getRandomX(0.8), getY() + 0.1, getRandomZ(0.8), 0, 0.2, 0);
            } else if (getState() == STUNNED) {
                level().addParticle(ParticleTypes.CRIT, getRandomX(0.6), getY() + 1.1, getRandomZ(0.6), 0, 0.1, 0);
            } else if (random.nextInt(6) == 0) {
                level().addParticle(ParticleTypes.SMALL_FLAME, getRandomX(0.6), getY() + 0.8, getRandomZ(0.6), 0, 0.02, 0);
            }
        }
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (getState() == STUNNED) amount *= 2.0f;
        else if (getState() == ROLL) amount *= 0.5f;
        return super.hurtServer(level, source, amount);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.BASALT_STEP;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.CRAWLER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.BASALT_BREAK;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        playSound(SoundEvents.SPIDER_STEP, 0.4f, 0.6f);
    }

    /** Curl up, then roll at the target in a straight line. */
    static final class RollChargeGoal extends Goal {
        private final MeteoriteCrawlerEntity mob;
        private int timer;
        private int cooldown = 60;
        private Vec3 dir = Vec3.ZERO;
        private boolean hit;

        RollChargeGoal(MeteoriteCrawlerEntity mob) {
            this.mob = mob;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
        }

        @Override
        public boolean canUse() {
            if (cooldown > 0) {
                cooldown--;
                return false;
            }
            LivingEntity t = mob.getTarget();
            if (t == null || !t.isAlive() || !mob.onGround()) return false;
            double d = mob.distanceToSqr(t);
            return d > 4 * 4 && d < 20 * 20 && mob.hasLineOfSight(t);
        }

        @Override
        public boolean canContinueToUse() {
            return mob.getState() != WALK;
        }

        @Override
        public void start() {
            mob.setState(CURL);
            timer = 18;
            hit = false;
            mob.getNavigation().stop();
            mob.playSound(ModSounds.CRAWLER_ROLL.get(), 1.2f, 0.8f);
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            ServerLevel level = (ServerLevel) mob.level();
            LivingEntity t = mob.getTarget();
            switch (mob.getState()) {
                case CURL -> {
                    if (t != null) mob.getLookControl().setLookAt(t, 30f, 30f);
                    if (--timer <= 0) {
                        Vec3 to = t != null ? t.position().subtract(mob.position()) : mob.getLookAngle();
                        dir = new Vec3(to.x, 0, to.z).normalize();
                        mob.setState(ROLL);
                        timer = 40;
                        mob.playSound(ModSounds.CRAWLER_ROLL.get(), 1.5f, 1.2f);
                    }
                }
                case ROLL -> {
                    mob.setDeltaMovement(dir.x * 0.85, mob.getDeltaMovement().y, dir.z * 0.85);
                    mob.setYRot((float) (Math.atan2(dir.z, dir.x) * 180 / Math.PI) - 90f);
                    mob.yBodyRot = mob.getYRot();
                    for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, mob.getBoundingBox().inflate(0.4), e -> e != mob && !(e instanceof MeteoriteCrawlerEntity))) {
                        if (e.hurtServer(level, level.damageSources().mobAttack(mob), 10.0f)) {
                            e.igniteForSeconds(3);
                            e.setDeltaMovement(e.getDeltaMovement().add(dir.x * 1.4, 0.5, dir.z * 1.4));
                            e.hurtMarked = true;
                            hit = true;
                        }
                    }
                    if (mob.horizontalCollision && timer < 38) {
                        mob.setState(STUNNED);
                        timer = 50;
                        mob.setDeltaMovement(dir.scale(-0.4).add(0, 0.3, 0));
                        FX.burst(level, ParticleTypes.EXPLOSION, mob.position().add(dir), 3, 0.4, 0);
                        level.playSound(null, mob.getX(), mob.getY(), mob.getZ(), SoundEvents.ANVIL_LAND, SoundSource.HOSTILE, 1.0f, 0.6f);
                    } else if (--timer <= 0 || hit) {
                        mob.setState(WALK);
                        cooldown = 90 + mob.getRandom().nextInt(60);
                    }
                }
                case STUNNED -> {
                    mob.getNavigation().stop();
                    if (--timer <= 0) {
                        mob.setState(WALK);
                        cooldown = 80;
                    }
                }
                default -> {}
            }
        }

        @Override
        public void stop() {
            if (mob.getState() != WALK) mob.setState(WALK);
        }
    }
}
