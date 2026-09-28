package com.astralfall.entity.projectile;

import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import com.astralfall.util.FX;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** Homing star. Colour 0 = starlight (players), 1 = void (enemies), 2 = gold (wisps & crown). */
public class StarBoltEntity extends AstralProjectile {
    private static final EntityDataAccessor<Integer> COLOR = SynchedEntityData.defineId(StarBoltEntity.class, EntityDataSerializers.INT);
    private LivingEntity target;
    private float homing = 0.14f;
    private double speed = 0.9;

    public StarBoltEntity(EntityType<? extends StarBoltEntity> type, Level level) {
        super(type, level);
        this.maxLife = 80;
    }

    public static StarBoltEntity shoot(Level level, LivingEntity owner, Vec3 from, Vec3 dir, int color, float damage, LivingEntity target) {
        StarBoltEntity e = new StarBoltEntity(ModEntities.STAR_BOLT.get(), level);
        e.setOwner(owner);
        e.setPos(from.x, from.y, from.z);
        e.speed = color == 1 ? 0.7 : 0.95;
        e.setDeltaMovement(dir.normalize().scale(e.speed));
        e.entityData.set(COLOR, color);
        e.damage = damage;
        e.target = target;
        level.addFreshEntity(e);
        return e;
    }

    public void setHoming(float homing) {
        this.homing = homing;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(COLOR, 0);
    }

    public int getColor() {
        return entityData.get(COLOR);
    }

    @Override
    protected boolean voidBane() {
        return getColor() != 1;
    }

    @Override
    protected void steer() {
        if (life < 4) return;
        if (target == null || !target.isAlive() || target.distanceToSqr(this) > 40 * 40) {
            target = findTarget();
        }
        if (target != null) {
            Vec3 want = target.getBoundingBox().getCenter().subtract(position()).normalize().scale(speed);
            setDeltaMovement(getDeltaMovement().lerp(want, homing).normalize().scale(speed));
        }
    }

    private LivingEntity findTarget() {
        Entity owner = getOwner();
        boolean hostileOwner = owner instanceof Enemy;
        LivingEntity best = null;
        double bestD = Double.MAX_VALUE;
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(20), this::canHitEntity)) {
            boolean valid = hostileOwner ? e instanceof Player p && !p.isCreative() && !p.isSpectator() : e instanceof Enemy;
            if (!valid) continue;
            double d = e.distanceToSqr(this);
            if (d < bestD) {
                bestD = d;
                best = e;
            }
        }
        return best;
    }

    @Override
    protected void onHitTarget(ServerLevel level, Entity hit) {
        super.onHitTarget(level, hit);
        FX.burst(level, particle(), hit.getBoundingBox().getCenter(), 12, 0.3, 0.12);
    }

    @Override
    protected void onHitWall(ServerLevel level, BlockHitResult hit) {
        FX.burst(level, particle(), hit.getLocation(), 8, 0.2, 0.08);
    }

    private ParticleOptions particle() {
        return switch (getColor()) {
            case 1 -> ModParticles.VOID_MOTE.get();
            case 2 -> ModParticles.GOLD_SPARKLE.get();
            default -> ModParticles.STAR_SPARKLE.get();
        };
    }

    @Override
    protected void clientTrail(Vec3 from, Vec3 to) {
        ParticleOptions p = particle();
        for (int i = 0; i < 3; i++) {
            Vec3 at = from.lerp(to, i / 3.0);
            level().addAlwaysVisibleParticle(p, at.x, at.y, at.z, 0, 0, 0);
        }
        if (getColor() == 1) level().addParticle(ParticleTypes.PORTAL, to.x, to.y, to.z, 0, 0, 0);
        else level().addParticle(ParticleTypes.END_ROD, to.x, to.y, to.z, 0, 0, 0);
    }
}
