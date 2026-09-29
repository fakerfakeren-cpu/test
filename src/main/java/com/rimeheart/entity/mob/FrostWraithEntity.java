package com.rimeheart.entity.mob;

import com.rimeheart.entity.projectile.IceShardEntity;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
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
 * A hooded spirit of the Long Winter. It circles its prey and casts volleys of ice shards; it fades in
 * direct sunlight. Immune to chill.
 */
public class FrostWraithEntity extends Monster {
    private static final EntityDataAccessor<Integer> CASTING = SynchedEntityData.defineId(FrostWraithEntity.class, EntityDataSerializers.INT);

    public FrostWraithEntity(EntityType<? extends FrostWraithEntity> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 10, true);
        this.setNoGravity(true);
        this.xpReward = 8;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 22.0)
            .add(Attributes.FLYING_SPEED, 0.5)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FOLLOW_RANGE, 32.0)
            .add(Attributes.ATTACK_DAMAGE, 4.0)
            .add(Attributes.ARMOR, 2.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CASTING, 0);
    }

    public int getCasting() {
        return entityData.get(CASTING);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
        nav.setCanFloat(true);
        return nav;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(2, new CastGoal(this));
        goalSelector.addGoal(5, new WaterAvoidingRandomFlyingGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0f));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public boolean canFreeze() {
        return false;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide()) {
            if (random.nextInt(2) == 0) level().addParticle(ModParticles.WRAITH_WISP.get(), getRandomX(0.6), getY() + random.nextDouble() * 0.8, getRandomZ(0.6), 0, -0.02, 0);
            if (random.nextInt(4) == 0) level().addParticle(ParticleTypes.SNOWFLAKE, getRandomX(0.8), getY() + random.nextDouble() * 1.6, getRandomZ(0.8), 0, -0.03, 0);
            if (getCasting() > 0) {
                Vec3 hands = position().add(0, 1.3, 0).add(getLookAngle().scale(0.6));
                level().addParticle(ModParticles.FROST_GLINT.get(), hands.x + (random.nextDouble() - 0.5) * 0.6, hands.y + (random.nextDouble() - 0.5) * 0.4, hands.z + (random.nextDouble() - 0.5) * 0.6, 0, 0, 0);
            }
        } else if (level() instanceof ServerLevel server && tickCount % 20 == 0 && !server.isDarkOutside() && server.canSeeSky(blockPosition())) {
            // Wraiths fade in direct sunlight.
            hurtServer(server, damageSources().magic(), 2.0f);
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
        return ModSounds.WRAITH_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WRAITH_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.WRAITH_DEATH.get();
    }

    static final class CastGoal extends Goal {
        private final FrostWraithEntity wraith;
        private int cooldown = 30;
        private int cast;

        CastGoal(FrostWraithEntity wraith) {
            this.wraith = wraith;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = wraith.getTarget();
            return t != null && t.isAlive() && wraith.distanceToSqr(t) < 30 * 30;
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void stop() {
            cast = 0;
            wraith.entityData.set(CASTING, 0);
        }

        @Override
        public void tick() {
            LivingEntity t = wraith.getTarget();
            if (t == null) return;
            ServerLevel level = (ServerLevel) wraith.level();
            wraith.getLookControl().setLookAt(t, 30f, 30f);
            double orbit = wraith.tickCount * 0.035 + wraith.getId();
            Vec3 want = t.position().add(Math.cos(orbit) * 6.5, 3.0 + Math.sin(wraith.tickCount * 0.05) * 0.8, Math.sin(orbit) * 6.5);
            wraith.getMoveControl().setWantedPosition(want.x, want.y, want.z, 1.0);
            boolean sees = wraith.hasLineOfSight(t);
            if (cast > 0) {
                cast++;
                wraith.entityData.set(CASTING, cast);
                if (cast >= 20) {
                    if (sees) fire(level, t);
                    stop();
                    cooldown = 50 + wraith.getRandom().nextInt(30);
                }
            } else if (--cooldown <= 0 && sees) {
                cast = 1;
                level.playSound(null, wraith.getX(), wraith.getY(), wraith.getZ(), ModSounds.WRAITH_AMBIENT.get(), SoundSource.HOSTILE, 1.0f, 1.6f);
            }
        }

        private void fire(ServerLevel level, LivingEntity t) {
            Vec3 from = wraith.position().add(0, 1.3, 0);
            int n = 1 + wraith.getRandom().nextInt(3);
            for (int i = 0; i < n; i++) {
                Vec3 aim = t.getEyePosition().subtract(from).normalize()
                    .add((wraith.getRandom().nextDouble() - 0.5) * 0.12, (wraith.getRandom().nextDouble() - 0.5) * 0.08, (wraith.getRandom().nextDouble() - 0.5) * 0.12);
                IceShardEntity.shoot(level, wraith, from, aim.normalize().scale(0.9), 4.0f, 70);
            }
            level.playSound(null, wraith.getX(), wraith.getY(), wraith.getZ(), ModSounds.ICICLE_SHOOT.get(), SoundSource.HOSTILE, 1.0f, 1.2f);
        }
    }
}
