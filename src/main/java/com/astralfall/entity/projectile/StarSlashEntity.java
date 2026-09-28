package com.astralfall.entity.projectile;

import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import com.astralfall.util.FX;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** Crescent of starlight fired by the Starblade. Pierces everything in its path. */
public class StarSlashEntity extends AstralProjectile {
    public StarSlashEntity(EntityType<? extends StarSlashEntity> type, Level level) {
        super(type, level);
        this.maxLife = 16;
        this.damage = 9.0f;
    }

    public static StarSlashEntity create(Level level, LivingEntity owner) {
        StarSlashEntity e = new StarSlashEntity(ModEntities.STAR_SLASH.get(), level);
        e.setOwner(owner);
        Vec3 look = owner.getLookAngle();
        e.setPos(owner.getX() + look.x * 0.8, owner.getEyeY() - 0.35 + look.y * 0.8, owner.getZ() + look.z * 0.8);
        e.setDeltaMovement(look.scale(1.7));
        return e;
    }

    @Override
    protected boolean piercing() {
        return true;
    }

    @Override
    protected double hitInflate() {
        return 1.1;
    }

    @Override
    protected void onHitTarget(ServerLevel level, Entity target) {
        super.onHitTarget(level, target);
        target.push(getDeltaMovement().normalize().scale(0.6).add(0, 0.2, 0));
        FX.burst(level, ModParticles.STAR_SPARKLE.get(), target.getBoundingBox().getCenter(), 14, 0.4, 0.15);
        FX.burst(level, ParticleTypes.CRIT, target.getBoundingBox().getCenter(), 10, 0.3, 0.4);
    }

    @Override
    protected void onHitWall(ServerLevel level, BlockHitResult hit) {
        FX.burst(level, ModParticles.STAR_SPARKLE.get(), hit.getLocation(), 20, 0.5, 0.1);
    }

    @Override
    protected void onExpire(ServerLevel level) {
        FX.burst(level, ModParticles.STAR_SPARKLE.get(), position(), 12, 0.6, 0.05);
    }

    @Override
    protected void clientTrail(Vec3 from, Vec3 to) {
        Vec3 dir = getDeltaMovement().normalize();
        Vec3 right = dir.cross(new Vec3(0, 1, 0));
        if (right.lengthSqr() < 1.0E-4) right = new Vec3(1, 0, 0);
        right = right.normalize();
        Vec3 up = right.cross(dir).normalize();
        double radius = 1.6;
        float tilt = (getId() % 7 - 3) * 0.15f;
        for (int i = -8; i <= 8; i++) {
            double theta = Math.toRadians(i * 10);
            Vec3 side = right.scale(Math.cos(tilt)).add(up.scale(Math.sin(tilt)));
            Vec3 p = to.add(side.scale(Math.sin(theta) * radius)).add(dir.scale((Math.cos(theta) - 1) * radius * 0.6));
            level().addAlwaysVisibleParticle(Math.abs(i) > 6 ? ParticleTypes.END_ROD : ModParticles.STAR_SPARKLE.get(), p.x, p.y, p.z, dir.x * 0.05, dir.y * 0.05, dir.z * 0.05);
        }
        if (tickCount % 2 == 0) {
            level().addParticle(ParticleTypes.SWEEP_ATTACK, to.x, to.y, to.z, 0, 0, 0);
        }
    }
}
