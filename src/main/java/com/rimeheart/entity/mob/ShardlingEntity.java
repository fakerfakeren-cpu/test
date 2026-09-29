package com.rimeheart.entity.mob;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/** A skittering crystal crawler that nests inside rime crystal clusters. Its bite chills. */
public class ShardlingEntity extends Monster {
    public ShardlingEntity(EntityType<? extends ShardlingEntity> type, Level level) {
        super(type, level);
        this.xpReward = 4;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 10.0)
            .add(Attributes.MOVEMENT_SPEED, 0.32)
            .add(Attributes.ATTACK_DAMAGE, 3.0)
            .add(Attributes.ARMOR, 4.0)
            .add(Attributes.FOLLOW_RANGE, 20.0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(1, new FloatGoal(this));
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.2, false));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.9));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public boolean doHurtTarget(ServerLevel level, Entity target) {
        boolean hit = super.doHurtTarget(level, target);
        if (hit && target instanceof LivingEntity l) Frost.chill(l, 50);
        return hit;
    }

    @Override
    public boolean canFreeze() {
        return false;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(6) == 0) {
            level().addParticle(ModParticles.FROST_GLINT.get(), getRandomX(0.5), getY() + 0.5, getRandomZ(0.5), 0, 0.01, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.SHARDLING_CHITTER.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.AMETHYST_BLOCK_HIT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.AMETHYST_CLUSTER_BREAK;
    }

    @Override
    public float getVoicePitch() {
        return 1.3f + random.nextFloat() * 0.2f;
    }
}
