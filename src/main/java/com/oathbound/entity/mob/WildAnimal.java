package com.oathbound.entity.mob;

import net.minecraft.core.BlockPos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;

/**
 * A creature of the wilds: it wanders, panics when struck and, if shy, keeps its distance from anyone who is not
 * creeping. It has one idle action (grazing, fishing, hiding in its shell) that its model shows.
 */
public abstract class WildAnimal extends PathfinderMob implements FaunaEntity {
    private static final EntityDataAccessor<Boolean> ACTING = SynchedEntityData.defineId(WildAnimal.class, EntityDataSerializers.BOOLEAN);
    private int actionTicks;

    protected WildAnimal(EntityType<? extends WildAnimal> type, Level level) {
        super(type, level);
    }

    /** Keeps away from players who are not sneaking. */
    protected boolean shy() {
        return false;
    }

    protected double wanderSpeed() {
        return 1.0;
    }

    /** Chance per tick of starting the idle action, and how long it lasts. */
    protected float actionChance() {
        return 0.004f;
    }

    protected int actionLength() {
        return 60;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(ACTING, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(ACTING);
    }

    protected void setActing(int ticks) {
        actionTicks = ticks;
        entityData.set(ACTING, ticks > 0);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new PanicGoal(this, 1.6 * wanderSpeed()));
        if (shy()) {
            goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 10f, 1.1 * wanderSpeed(), 1.5 * wanderSpeed(),
                e -> e instanceof Player p && !p.isShiftKeyDown() && !p.isSpectator() && !p.isCreative()));
        }
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, wanderSpeed()));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 6f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (actionTicks > 0) {
            getNavigation().stop();
            if (--actionTicks == 0) entityData.set(ACTING, false);
        } else if (getNavigation().isDone() && getLastHurtByMob() == null && random.nextFloat() < actionChance()) {
            setActing(actionLength());
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    /** Surface creatures: on grass-like ground in daylight or moonlight. */
    public static boolean checkWildSpawn(EntityType<? extends Mob> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        if (reason == EntitySpawnReason.SPAWNER) return true;
        return level.getBlockState(pos.below()).is(BlockTags.ANIMALS_SPAWNABLE_ON) && level.getRawBrightness(pos, 0) > 8;
    }

    /** Waders and tortoises: sand, gravel, mud or grass near water. */
    public static boolean checkShoreSpawn(EntityType<? extends Mob> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        if (reason == EntitySpawnReason.SPAWNER) return true;
        var below = level.getBlockState(pos.below());
        boolean ground = below.is(BlockTags.ANIMALS_SPAWNABLE_ON) || below.is(BlockTags.SAND) || below.is(net.minecraft.world.level.block.Blocks.MUD)
            || below.is(net.minecraft.world.level.block.Blocks.GRAVEL);
        return ground && level.getRawBrightness(pos, 0) > 8;
    }

    /** Cave creatures: in the dark, well below the surface. */
    public static boolean checkCaveSpawn(EntityType<? extends Mob> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        if (reason == EntitySpawnReason.SPAWNER) return true;
        return pos.getY() < level.getSeaLevel() - 12 && level.getRawBrightness(pos, 0) < 6 && !level.canSeeSky(pos)
            && level.getBlockState(pos.below()).isSolid();
    }
}
