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
import net.minecraft.world.phys.Vec3;

/**
 * A long, low cat of the Gloaming. Until it is close it is only a shimmer at the edge of sight; then it is all at
 * once, mid-leap. A lit lantern shows it plainly.
 */
public class GloamStalkerEntity extends Monster implements FaunaEntity {
    private static final EntityDataAccessor<Boolean> REVEALED = SynchedEntityData.defineId(GloamStalkerEntity.class, EntityDataSerializers.BOOLEAN);
    private int pounce = 30;

    public GloamStalkerEntity(EntityType<? extends GloamStalkerEntity> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 32.0).add(Attributes.MOVEMENT_SPEED, 0.34).add(Attributes.ATTACK_DAMAGE, 7.0)
            .add(Attributes.FOLLOW_RANGE, 32.0).add(Attributes.STEP_HEIGHT, 1.1);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(REVEALED, false);
    }

    @Override
    public boolean fauna$ghost() {
        return !entityData.get(REVEALED);
    }

    @Override
    public boolean fauna$action() {
        return !onGround();
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15, true));
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        boolean lantern = false;
        for (Player p : level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(8))) {
            if (!GameEvents.heldLitLantern(p).isEmpty()) lantern = true;
        }
        boolean close = t != null && distanceToSqr(t) < 6 * 6;
        entityData.set(REVEALED, lantern || close || getLastHurtByMob() != null && tickCount - getLastHurtByMobTimestamp() < 60);
        if (t != null && --pounce <= 0 && onGround() && distanceToSqr(t) < 9 * 9 && distanceToSqr(t) > 3 * 3) {
            pounce = 60 + random.nextInt(40);
            Vec3 leap = t.position().subtract(position()).normalize();
            setDeltaMovement(leap.x * 1.2, 0.5, leap.z * 1.2);
            hurtMarked = true;
            Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 0.6, 0), 16, 0.4, 0.05);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.STALKER_SNARL.get(), SoundSource.HOSTILE, 1.4f, 1.1f);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return entityData.get(REVEALED) ? ModSounds.STALKER_SNARL.get() : null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.STALKER_SNARL.get();
    }
}
