package com.oathbound.entity.mob;

import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
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
import net.minecraft.world.phys.Vec3;

/**
 * A spiteful little shard of living dusk. In darkness it is all but invisible, unless someone nearby carries a
 * lit lantern. It darts in, bites, and flees back into the shadows before striking again. Sunlight burns it.
 */
public class GloamlingEntity extends Monster {
    private static final EntityDataAccessor<Boolean> VEILED = SynchedEntityData.defineId(GloamlingEntity.class, EntityDataSerializers.BOOLEAN);
    private int fleeing;

    public GloamlingEntity(EntityType<? extends GloamlingEntity> type, Level level) {
        super(type, level);
        this.xpReward = 5;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 14.0)
            .add(Attributes.ATTACK_DAMAGE, 4.0)
            .add(Attributes.MOVEMENT_SPEED, 0.36)
            .add(Attributes.FOLLOW_RANGE, 28.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(VEILED, true);
    }

    public boolean isVeiled() {
        return entityData.get(VEILED);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.35, false) {
            @Override
            public boolean canUse() {
                return fleeing <= 0 && super.canUse();
            }

            @Override
            public boolean canContinueToUse() {
                return fleeing <= 0 && super.canContinueToUse();
            }
        });
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.9));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    @Override
    public boolean doHurtTarget(ServerLevel level, Entity target) {
        boolean hit = super.doHurtTarget(level, target);
        if (hit) fleeing = 35 + random.nextInt(25);
        return hit;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (fleeing > 0) {
            fleeing--;
            LivingEntity t = getTarget();
            if (t != null && tickCount % 10 == 0) {
                Vec3 away = position().subtract(t.position()).normalize().scale(8);
                getNavigation().moveTo(getX() + away.x, getY(), getZ() + away.z, 1.5);
            }
        }
        if (tickCount % 10 == 0) {
            boolean dark = level.getMaxLocalRawBrightness(blockPosition()) < 9;
            boolean revealed = false;
            for (Player p : level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(12))) {
                if (!GameEvents.heldLitLantern(p).isEmpty()) revealed = true;
            }
            entityData.set(VEILED, dark && !revealed);
        }
        if (tickCount % 20 == 0 && level.isBrightOutside() && level.canSeeSky(blockPosition()) && !level.isRainingAt(blockPosition())) {
            igniteForSeconds(4);
        }
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (!isVeiled()) amount *= 1.25f;
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(isVeiled() ? 4 : 2) == 0) {
            level().addParticle(ModParticles.GLOAM_WISP.get(), getRandomX(0.5), getY() + random.nextDouble() * 0.8, getRandomZ(0.5), 0, 0.01, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.GLOAMLING_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.GLOAMLING_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.GLOAMLING_DEATH.get();
    }
}
