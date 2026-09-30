package com.oathbound.entity.mob;

import com.oathbound.entity.SpellMarkEntity;
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
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
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
import net.minecraft.world.phys.AABB;

/**
 * A monk of the drowned chapel who never stopped singing the vespers. When it sees the living it raises its
 * candle and sings, and the hymn weighs on every limb that hears it.
 */
public class DrownedChoirmonkEntity extends Monster implements FaunaEntity {
    private static final EntityDataAccessor<Boolean> SINGING = SynchedEntityData.defineId(DrownedChoirmonkEntity.class, EntityDataSerializers.BOOLEAN);
    private int hymn = 60;
    private int singing;

    public DrownedChoirmonkEntity(EntityType<? extends DrownedChoirmonkEntity> type, Level level) {
        super(type, level);
        this.xpReward = 8;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 26.0).add(Attributes.MOVEMENT_SPEED, 0.23).add(Attributes.ATTACK_DAMAGE, 4.0)
            .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(SINGING, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(SINGING);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, false) {
            @Override
            public boolean canUse() {
                return !fauna$action() && super.canUse();
            }
        });
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        if (singing > 0) {
            getNavigation().stop();
            if (--singing % 20 == 0) {
                for (Player p : level.getEntitiesOfClass(Player.class, new AABB(blockPosition()).inflate(9), p -> !p.isCreative() && !p.isSpectator())) {
                    p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 100, 1));
                    p.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 100, 0));
                }
                Vfx.ring(level, ModParticles.TIDE.get(), position().add(0, 0.2, 0), 4 + (60 - singing) * 0.08, 32, 0.05);
            }
            if (singing == 0) entityData.set(SINGING, false);
            return;
        }
        if (t != null && --hymn <= 0 && distanceToSqr(t) < 10 * 10) {
            hymn = 180 + random.nextInt(80);
            singing = 60;
            entityData.set(SINGING, true);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.MONK_CHANT.get(), SoundSource.HOSTILE, 2.0f, 1.0f);
            SpellMarkEntity.ring(level, position(), 9f, SpellMarkEntity.Hue.TIDE, 30);
            SpellMarkEntity.sigil(level, position(), 2.2f, SpellMarkEntity.Hue.TIDE, 60);
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(10) == 0) {
            level().addParticle(ModParticles.TIDE.get(), getRandomX(0.5), getY() + 1.8, getRandomZ(0.5), 0, 0.02, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.MONK_CHANT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WIGHT_HURT.get();
    }

    @Override
    public float getVoicePitch() {
        return 0.8f;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 300;
    }
}
