package com.oathbound.entity.mob;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.UUID;

/**
 * A spectral axeman of Hrodgar's guard. Raised by the Barrow-King they fight for him (and shield him with their
 * oath); raised by the Housecarl's Warhorn they fight for you until the horn's echo fades.
 */
public class SpectralHousecarlEntity extends Monster {
    private static final EntityDataAccessor<Boolean> ALLY = SynchedEntityData.defineId(SpectralHousecarlEntity.class, EntityDataSerializers.BOOLEAN);
    private UUID owner;
    private int life = -1;

    public SpectralHousecarlEntity(EntityType<? extends SpectralHousecarlEntity> type, Level level) {
        super(type, level);
        this.xpReward = 3;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 24.0)
            .add(Attributes.ATTACK_DAMAGE, 6.0)
            .add(Attributes.ARMOR, 4.0)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(ALLY, false);
    }

    public boolean isAlly() {
        return entityData.get(ALLY);
    }

    public void makeAlly(Player player, int ticks) {
        entityData.set(ALLY, true);
        owner = player.getUUID();
        life = ticks;
    }

    private Player ownerPlayer() {
        return owner == null ? null : level().getPlayerByUUID(owner);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2, true));
        targetSelector.addGoal(1, new HurtByTargetGoal(this) {
            @Override
            public boolean canUse() {
                LivingEntity by = getLastHurtByMob();
                if (isAlly() && by != null && by.getUUID().equals(owner)) return false;
                return super.canUse();
            }
        });
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !isAlly()));
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Mob.class, 5, true, false,
            (t, l) -> isAlly() && t instanceof Enemy && !(t instanceof SpectralHousecarlEntity h && h.isAlly())));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (!isAlly()) return;
        Player o = ownerPlayer();
        if (getTarget() == null && o != null) {
            LivingEntity foe = o.getLastHurtByMob();
            if (foe != null && foe.isAlive() && foe != this) setTarget(foe);
            else if (distanceToSqr(o) > 36) getNavigation().moveTo(o, 1.2);
        }
        if (getTarget() instanceof Player) setTarget(null);
        if (life > 0 && --life == 0) {
            Vfx.burst(level, ModParticles.SPIRIT.get(), position().add(0, 1, 0), 30, 0.4, 0.08);
            discard();
        }
    }

    @Override
    protected boolean considersEntityAsAlly(Entity other) {
        if (isAlly() && owner != null && (other.getUUID().equals(owner) || other instanceof SpectralHousecarlEntity h && h.isAlly())) return true;
        return super.considersEntityAsAlly(other);
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (isAlly() && source.getEntity() != null && source.getEntity().getUUID().equals(owner)) return false;
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(2) == 0) {
            level().addParticle(ModParticles.SPIRIT.get(), getRandomX(0.6), getY() + random.nextDouble() * 1.9, getRandomZ(0.6), 0, 0.02, 0);
        }
    }

    @Override
    public boolean removeWhenFarAway(double d) {
        return !isAlly() && super.removeWhenFarAway(d);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HOUSECARL_RISE.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 240;
    }

    @Override
    protected float getSoundVolume() {
        return 0.5f;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return net.minecraft.sounds.SoundEvents.SKELETON_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.TETHER_SNAP.get();
    }

    public Vec3 tetherPoint() {
        return position().add(0, 1.2, 0);
    }
}
