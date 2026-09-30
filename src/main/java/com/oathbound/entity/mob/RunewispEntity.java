package com.oathbound.entity.mob;

import com.oathbound.entity.projectile.GlyphBoltEntity;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;

/**
 * A mote of written light that drifts through birch woods at night. It minds its own business; strike it and it
 * answers with glyphs until you leave.
 */
public class RunewispEntity extends PathfinderMob implements FaunaEntity {
    private Vec3 drift;
    private int zap = 40;

    public RunewispEntity(EntityType<? extends RunewispEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 10.0).add(Attributes.MOVEMENT_SPEED, 0.2).add(Attributes.FOLLOW_RANGE, 20.0);
    }

    @Override
    protected void registerGoals() {
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
    }

    @Override
    public boolean fauna$action() {
        return getTarget() != null;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        LivingEntity t = getTarget();
        if (t != null && (!t.isAlive() || distanceToSqr(t) > 24 * 24)) {
            setTarget(null);
            t = null;
        }
        if (drift == null || tickCount % 60 == 0 || position().distanceToSqr(drift) < 1) {
            BlockPos ground = level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, blockPosition());
            Vec3 base = t != null ? t.position() : position();
            drift = new Vec3(base.x + (random.nextDouble() - 0.5) * 10, ground.getY() + 2 + random.nextDouble() * 3, base.z + (random.nextDouble() - 0.5) * 10);
        }
        Vec3 to = drift.subtract(position());
        setDeltaMovement(getDeltaMovement().scale(0.85).add(to.normalize().scale(0.02)));
        if (t != null) {
            getLookControl().setLookAt(t, 30, 30);
            if (--zap <= 0 && hasLineOfSight(t)) {
                zap = 35 + random.nextInt(20);
                Vec3 from = position().add(0, 0.3, 0);
                Vec3 aim = t.getEyePosition().subtract(from).normalize();
                GlyphBoltEntity.shoot(level, this, from, aim.scale(0.8));
                level.playSound(null, getX(), getY(), getZ(), ModSounds.WISP_CHIME.get(), SoundSource.NEUTRAL, 1.0f, 1.4f);
            }
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(3) == 0) {
            level().addParticle(ModParticles.ARCANE_GLYPH.get(), getRandomX(0.6), getY() + random.nextDouble() * 0.6, getRandomZ(0.6), 0, 0.01, 0);
        }
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.WISP_CHIME.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.WISP_CHIME.get();
    }

    /** At night, in the open, over the forest floor. */
    public static boolean checkWispSpawn(EntityType<RunewispEntity> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        if (reason == EntitySpawnReason.SPAWNER) return true;
        return level.getLevel().isDarkOutside() && level.canSeeSky(pos) && random.nextInt(4) == 0;
    }
}
