package com.astralfall.entity.mob;

import com.astralfall.entity.projectile.StarBoltEntity;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.FollowOwnerGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * A little spirit of starlight. Wild wisps gather around fallen stars. Offer one Stardust to tame
 * it: tamed wisps follow you, heal you, and shoot golden stars at your enemies. One in thirty is a
 * rare Prismatic Wisp that shimmers through every colour and hits twice as hard.
 */
public class AstralWispEntity extends TamableAnimal {
    private static final EntityDataAccessor<Boolean> PRISMATIC = SynchedEntityData.defineId(AstralWispEntity.class, EntityDataSerializers.BOOLEAN);
    private int healCooldown = 100;

    public AstralWispEntity(EntityType<? extends AstralWispEntity> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        this.setNoGravity(true);
        if (!level.isClientSide() && level.getRandom().nextInt(30) == 0) {
            this.entityData.set(PRISMATIC, true);
        }
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
            .add(Attributes.MAX_HEALTH, 16.0)
            .add(Attributes.FLYING_SPEED, 0.7)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FOLLOW_RANGE, 32.0)
            .add(Attributes.ATTACK_DAMAGE, 3.0);
    }

    public static boolean checkWispSpawnRules(EntityType<AstralWispEntity> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        return pos.getY() > level.getSeaLevel() && level.getLevel().isDarkOutside() && random.nextInt(3) == 0;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(PRISMATIC, false);
    }

    public boolean isPrismatic() {
        return entityData.get(PRISMATIC);
    }

    public void setPrismatic(boolean prismatic) {
        entityData.set(PRISMATIC, prismatic);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
        nav.setCanOpenDoors(false);
        nav.setCanFloat(true);
        return nav;
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        goalSelector.addGoal(2, new WispAttackGoal(this));
        goalSelector.addGoal(3, new FollowOwnerGoal(this, 1.2, 6.0f, 2.0f));
        goalSelector.addGoal(5, new WaterAvoidingRandomFlyingGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0f));
        targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean treat = stack.is(ModItems.STARDUST.get()) || stack.is(ModItems.SKYSHARD.get());
        if (!isTame() && treat) {
            if (level() instanceof ServerLevel server) {
                if (!player.hasInfiniteMaterials()) stack.shrink(1);
                if (random.nextInt(3) == 0) {
                    tame(player);
                    setOrderedToSit(false);
                    navigation.stop();
                    setTarget(null);
                    server.broadcastEntityEvent(this, (byte) 7);
                    FX.burst(server, isPrismatic() ? ModParticles.STAR_SPARKLE.get() : ModParticles.GOLD_SPARKLE.get(), position().add(0, 0.3, 0), 30, 0.5, 0.1);
                } else {
                    server.broadcastEntityEvent(this, (byte) 6);
                }
            }
            return InteractionResult.SUCCESS;
        }
        if (isTame() && isOwnedBy(player)) {
            if (treat && getHealth() < getMaxHealth()) {
                if (!player.hasInfiniteMaterials()) stack.shrink(1);
                heal(8.0f);
                return InteractionResult.SUCCESS;
            }
            if (stack.isEmpty()) {
                if (!level().isClientSide()) {
                    setOrderedToSit(!isOrderedToSit());
                    navigation.stop();
                }
                return InteractionResult.SUCCESS;
            }
        }
        return super.mobInteract(player, hand);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide()) {
            if (random.nextInt(2) == 0) {
                double x = getX() + (random.nextDouble() - 0.5) * 0.6, y = getY() + 0.3 + (random.nextDouble() - 0.5) * 0.6, z = getZ() + (random.nextDouble() - 0.5) * 0.6;
                if (isPrismatic()) {
                    int rgb = Mth.hsvToRgb((tickCount % 60) / 60f, 0.7f, 1.0f);
                    level().addParticle(new DustParticleOptions(rgb, 0.8f), x, y, z, 0, 0, 0);
                } else {
                    level().addParticle(ModParticles.STAR_SPARKLE.get(), x, y, z, 0, -0.02, 0);
                }
            }
        } else if (level() instanceof ServerLevel server && isTame() && getOwner() instanceof Player owner) {
            if (--healCooldown <= 0 && owner.getHealth() < owner.getMaxHealth() && owner.distanceToSqr(this) < 12 * 12) {
                owner.heal(isPrismatic() ? 4.0f : 2.0f);
                FX.line(server, ModParticles.GOLD_SPARKLE.get(), position().add(0, 0.3, 0), owner.position().add(0, 1, 0), 0.4);
                FX.burst(server, ParticleTypes.HEART, owner.position().add(0, 2, 0), 2, 0.3, 0);
                healCooldown = 200;
            }
        }
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {}

    @Override
    protected boolean canFlyToOwner() {
        return true;
    }

    @Override
    public boolean removeWhenFarAway(double distanceSqr) {
        return !isTame() && !hasCustomName() && tickCount > 2400;
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(ModItems.STARDUST.get());
    }

    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        return null;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.WISP_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WISP_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.AMETHYST_CLUSTER_BREAK;
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putBoolean("Prismatic", isPrismatic());
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        setPrismatic(in.getBooleanOr("Prismatic", false));
    }

    /** Hovers near its target and shoots golden stars. */
    static final class WispAttackGoal extends Goal {
        private final AstralWispEntity wisp;
        private int cooldown;

        WispAttackGoal(AstralWispEntity wisp) {
            this.wisp = wisp;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = wisp.getTarget();
            return wisp.isTame() && !wisp.isOrderedToSit() && t != null && t.isAlive();
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity t = wisp.getTarget();
            if (t == null) return;
            wisp.getLookControl().setLookAt(t, 30f, 30f);
            double d = wisp.distanceToSqr(t);
            if (d > 7 * 7) wisp.getNavigation().moveTo(t.getX(), t.getY() + 2.5, t.getZ(), 1.2);
            else wisp.getNavigation().stop();
            if (--cooldown <= 0 && d < 16 * 16 && wisp.hasLineOfSight(t)) {
                Vec3 from = wisp.position().add(0, 0.3, 0);
                StarBoltEntity.shoot(wisp.level(), wisp, from, t.getBoundingBox().getCenter().subtract(from), 2, wisp.isPrismatic() ? 8.0f : 4.0f, t);
                wisp.playSound(ModSounds.STAR_BOLT.get(), 0.8f, 1.4f);
                cooldown = wisp.isPrismatic() ? 20 : 30;
            }
        }
    }
}
