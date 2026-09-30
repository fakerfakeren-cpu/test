package com.oathbound.entity.mob;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.entity.projectile.GloamBoltEntity;
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
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * A swamp witch bent under her lantern. She keeps her distance, flings curses of green fire and, when a blade gets
 * close, is simply somewhere else in a puff of marsh-gas.
 */
public class MireHagEntity extends Monster implements FaunaEntity {
    private static final EntityDataAccessor<Boolean> CASTING = SynchedEntityData.defineId(MireHagEntity.class, EntityDataSerializers.BOOLEAN);
    private int curse = 40;
    private int blink;
    private int castTicks;

    public MireHagEntity(EntityType<? extends MireHagEntity> type, Level level) {
        super(type, level);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 30.0).add(Attributes.MOVEMENT_SPEED, 0.24).add(Attributes.FOLLOW_RANGE, 28.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CASTING, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(CASTING);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (castTicks > 0 && --castTicks == 0) entityData.set(CASTING, false);
        if (blink > 0) blink--;
        LivingEntity t = getTarget();
        if (t == null) return;
        getLookControl().setLookAt(t, 30, 30);
        double d = distanceToSqr(t);
        // keep at arm's length: close in from afar, back off when pressed
        if (d > 12 * 12) getNavigation().moveTo(t, 1.0);
        else if (d < 6 * 6) {
            Vec3 away = position().subtract(t.position()).normalize().scale(6);
            getNavigation().moveTo(getX() + away.x, getY(), getZ() + away.z, 1.1);
        } else getNavigation().stop();
        if (d < 3.5 * 3.5 && blink == 0) {
            blinkAway(level, t);
            return;
        }
        if (--curse <= 0 && hasLineOfSight(t) && d < 20 * 20) {
            curse = 50 + random.nextInt(30);
            castTicks = 14;
            entityData.set(CASTING, true);
            GloamBoltEntity.shoot(level, this, position().add(0, 1.8, 0), t, 5f);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CURSE.get(), SoundSource.HOSTILE, 1.3f, 1.0f);
            if (random.nextInt(3) == 0) t.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 120, 0));
        }
    }

    private void blinkAway(ServerLevel level, LivingEntity from) {
        blink = 120;
        for (int tries = 0; tries < 12; tries++) {
            double a = random.nextDouble() * Math.PI * 2;
            Vec3 to = from.position().add(Math.cos(a) * 9, 0, Math.sin(a) * 9);
            var pos = net.minecraft.core.BlockPos.containing(to);
            var top = level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, pos);
            if (Math.abs(top.getY() - getY()) > 6) continue;
            Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1, 0), 30, 0.5, 0.05);
            SpellMarkEntity.ring(level, position(), 3f, SpellMarkEntity.Hue.GLOAM, 10);
            teleportTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5);
            Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1, 0), 30, 0.5, 0.05);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CACKLE.get(), SoundSource.HOSTILE, 1.4f, 1.0f);
            return;
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(6) == 0) {
            level().addParticle(ModParticles.SPIRIT.get(), getRandomX(0.8), getY() + 2.0, getRandomZ(0.8), 0, 0.015, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.HAG_CACKLE.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HAG_CURSE.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 240;
    }
}
