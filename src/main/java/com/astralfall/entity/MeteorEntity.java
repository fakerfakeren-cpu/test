package com.astralfall.entity;

import com.astralfall.event.Starfall;
import com.astralfall.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** A falling meteor. Streaks across the sky with a blazing trail and craters on impact. */
public class MeteorEntity extends Entity {
    public static final byte IMPACT_EVENT = 60;
    private static final EntityDataAccessor<Integer> VARIANT = SynchedEntityData.defineId(MeteorEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> SIZE = SynchedEntityData.defineId(MeteorEntity.class, EntityDataSerializers.FLOAT);

    private int burnoutAt = -1;
    public float spin;
    public float spinO;

    public MeteorEntity(EntityType<? extends MeteorEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public void setup(Starfall.Variant variant, float size, Vec3 velocity) {
        entityData.set(VARIANT, variant.ordinal());
        entityData.set(SIZE, size);
        setDeltaMovement(velocity);
        if (variant == Starfall.Variant.SHOOTING_STAR) burnoutAt = 30 + random.nextInt(30);
    }

    public Starfall.Variant getVariant() {
        int i = entityData.get(VARIANT);
        Starfall.Variant[] all = Starfall.Variant.values();
        return all[Mth.clamp(i, 0, all.length - 1)];
    }

    public float getSize() {
        return entityData.get(SIZE);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(VARIANT, 0);
        builder.define(SIZE, 1.5f);
    }

    @Override
    public void tick() {
        super.tick();
        spinO = spin;
        spin += 12f;
        Vec3 from = position();
        Vec3 v = getDeltaMovement();
        Vec3 to = from.add(v);
        if (level() instanceof ServerLevel server) {
            if (burnoutAt > 0 && tickCount >= burnoutAt) {
                discard();
                return;
            }
            if (getY() < level().getMinY() - 16 || tickCount > 600) {
                discard();
                return;
            }
            if (getVariant() != Starfall.Variant.SHOOTING_STAR) {
                BlockHitResult hit = server.clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.ANY, this));
                if (hit.getType() != HitResult.Type.MISS) {
                    setPos(hit.getLocation().x, hit.getLocation().y, hit.getLocation().z);
                    server.broadcastEntityEvent(this, IMPACT_EVENT);
                    Starfall.impact(server, this, BlockPos.containing(hit.getLocation().subtract(v.normalize().scale(0.1))));
                    discard();
                    return;
                }
            }
            setPos(to.x, to.y, to.z);
        } else {
            setPos(to.x, to.y, to.z);
            trail(from, to);
        }
    }

    private void trail(Vec3 from, Vec3 to) {
        Starfall.Variant variant = getVariant();
        float size = getSize();
        int steps = 4;
        for (int i = 0; i < steps; i++) {
            Vec3 p = from.lerp(to, i / (double) steps);
            double s = size * 0.4;
            double ox = (random.nextDouble() - 0.5) * s, oy = (random.nextDouble() - 0.5) * s, oz = (random.nextDouble() - 0.5) * s;
            switch (variant) {
                case FALLEN_STAR -> {
                    level().addAlwaysVisibleParticle(ModParticles.GOLD_SPARKLE.get(), p.x + ox, p.y + oy, p.z + oz, 0, 0, 0);
                    level().addAlwaysVisibleParticle(ParticleTypes.END_ROD, p.x + ox, p.y + oy, p.z + oz, 0, 0.02, 0);
                }
                case SHOOTING_STAR -> level().addAlwaysVisibleParticle(ParticleTypes.END_ROD, p.x, p.y, p.z, 0, 0, 0);
                default -> {
                    level().addAlwaysVisibleParticle(ModParticles.COMET_TRAIL.get(), p.x + ox, p.y + oy, p.z + oz, 0, 0, 0);
                    level().addAlwaysVisibleParticle(ParticleTypes.FLAME, p.x + ox, p.y + oy, p.z + oz, 0, 0, 0);
                }
            }
        }
        if (variant != Starfall.Variant.SHOOTING_STAR) {
            level().addAlwaysVisibleParticle(ParticleTypes.LARGE_SMOKE, from.x, from.y, from.z, 0, 0.02, 0);
            if (random.nextInt(3) == 0) level().addAlwaysVisibleParticle(ParticleTypes.LAVA, to.x, to.y, to.z, 0, 0, 0);
            if (variant == Starfall.Variant.CRAWLER || variant == Starfall.Variant.BOSS) {
                level().addAlwaysVisibleParticle(ModParticles.VOID_MOTE.get(), to.x, to.y, to.z, 0, 0, 0);
            }
        }
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == IMPACT_EVENT) {
            Vec3 p = position();
            for (int i = 0; i < 40; i++) {
                level().addAlwaysVisibleParticle(ParticleTypes.LAVA, p.x, p.y + 0.5, p.z, 0, 0, 0);
                level().addAlwaysVisibleParticle(ModParticles.COMET_TRAIL.get(), p.x, p.y + 0.5, p.z, (random.nextDouble() - 0.5) * 1.2, random.nextDouble() * 1.2, (random.nextDouble() - 0.5) * 1.2);
            }
            com.astralfall.client.ClientFX.shakeFrom(p, 6.0f + getSize() * 3.0f, 48.0 + getSize() * 20.0);
        } else {
            super.handleEntityEvent(id);
        }
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double dist) {
        return true;
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {}

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {}
}
