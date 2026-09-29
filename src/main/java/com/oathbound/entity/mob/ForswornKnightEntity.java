package com.oathbound.entity.mob;

import com.oathbound.entity.projectile.SunArrowEntity;
import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

/**
 * A knight who broke faith with the Order and followed Morvane into the dusk. Cut one down with ordinary
 * steel and it collapses into a heap of armour, only to rise again. Oath-forged weapons, fire, light or
 * magic lay it to rest for good (it can rise at most twice).
 */
public class ForswornKnightEntity extends Monster {
    private static final EntityDataAccessor<Boolean> FALLEN = SynchedEntityData.defineId(ForswornKnightEntity.class, EntityDataSerializers.BOOLEAN);
    public static final int FALL_TIME = 110;
    private int fallenTicks;
    private int rises;

    public ForswornKnightEntity(EntityType<? extends ForswornKnightEntity> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 34.0)
            .add(Attributes.ATTACK_DAMAGE, 7.0)
            .add(Attributes.ARMOR, 8.0)
            .add(Attributes.MOVEMENT_SPEED, 0.27)
            .add(Attributes.FOLLOW_RANGE, 32.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.4);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(FALLEN, false);
    }

    public boolean isFallen() {
        return entityData.get(FALLEN);
    }

    public int fallenTicks() {
        return fallenTicks;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15, false));
        goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.7));
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 10f));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, (t, l) -> !GameEvents.wearsCrown(t)));
    }

    /** Whether this blow can lay a forsworn knight to rest for good. */
    public static boolean laysToRest(DamageSource source) {
        if (source.is(DamageTypeTags.IS_FIRE) || source.is(DamageTypeTags.WITCH_RESISTANT_TO)) return true;
        if (source.getDirectEntity() instanceof SunArrowEntity) return true;
        if (source.getEntity() instanceof Player p && source.getDirectEntity() == p && p.getMainHandItem().is(ModTags.OATH_FORGED)) return true;
        return false;
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (isFallen()) {
            if (laysToRest(source)) {
                entityData.set(FALLEN, false);
                setNoAi(false);
                rises = 99;
                // the collapse left it inside its hurt cooldown; the rite must land regardless
                invulnerableTime = 0;
                return super.hurtServer(level, source, Math.max(amount, getHealth() + 50));
            }
            if (source.getEntity() instanceof Player p) {
                p.sendOverlayMessage(Component.translatable("message.oathbound.forsworn.rest").withStyle(ChatFormatting.GRAY));
            }
            return false;
        }
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void die(DamageSource source) {
        if (!level().isClientSide() && !laysToRest(source) && rises < 2 && !isFallen()) {
            setHealth(1.0f);
            entityData.set(FALLEN, true);
            fallenTicks = 0;
            getNavigation().stop();
            setTarget(null);
            setNoAi(true);
            playSound(ModSounds.FORSWORN_COLLAPSE.get(), 1.2f, 1.0f);
            if (level() instanceof ServerLevel s) Vfx.burst(s, ModParticles.GLOAM_WISP.get(), position().add(0, 0.5, 0), 25, 0.5, 0.05);
            return;
        }
        super.die(source);
    }

    @Override
    public void aiStep() {
        if (isFallen()) {
            setDeltaMovement(0, getDeltaMovement().y, 0);
            if (!level().isClientSide()) {
                fallenTicks++;
                if (fallenTicks % 10 == 0 && level() instanceof ServerLevel s) Vfx.burst(s, ModParticles.GLOAM_WISP.get(), position().add(0, 0.3, 0), 6, 0.4, 0.02);
                if (fallenTicks >= FALL_TIME) {
                    entityData.set(FALLEN, false);
                    setNoAi(false);
                    rises++;
                    setHealth(getMaxHealth() * 0.5f);
                    playSound(ModSounds.FORSWORN_RISE.get(), 1.3f, 1.0f);
                    if (level() instanceof ServerLevel s) {
                        Vfx.column(s, ModParticles.GLOAM_WISP.get(), position(), 2.5, 30);
                        Vfx.burst(s, ParticleTypes.SOUL, position().add(0, 1, 0), 10, 0.4, 0.05);
                    }
                }
            } else {
                fallenTicks++;
            }
            super.aiStep();
            return;
        }
        fallenTicks = 0;
        super.aiStep();
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        if (isFallen()) return;
        super.customServerAiStep(level);
    }

    @Override
    public boolean isPushable() {
        return !isFallen() && super.isPushable();
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isFallen() ? null : ModSounds.FORSWORN_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return net.minecraft.sounds.SoundEvents.SKELETON_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.FORSWORN_COLLAPSE.get();
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putInt("Rises", rises);
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        rises = in.getIntOr("Rises", 0);
        setNoAi(false);
    }
}
