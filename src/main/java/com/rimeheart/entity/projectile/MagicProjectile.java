package com.rimeheart.entity.projectile;

import it.unimi.dsi.fastutil.ints.IntOpenHashSet;
import it.unimi.dsi.fastutil.ints.IntSet;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Base for Rimeheart's magical projectiles. They fly in straight lines without gravity,
 * optionally pierce through several targets, and are drawn purely with particles.
 */
public abstract class MagicProjectile extends Projectile {
    protected int life;
    protected int maxLife = 60;
    protected float damage = 6.0f;
    protected float gravity = 0.0f;
    private final IntSet alreadyHit = new IntOpenHashSet();

    protected MagicProjectile(EntityType<? extends MagicProjectile> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public void setDamage(float damage) {
        this.damage = damage;
    }

    public void setGravity(float gravity) {
        this.gravity = gravity;
    }

    protected boolean piercing() {
        return false;
    }

    protected boolean stopsOnBlocks() {
        return true;
    }

    protected double hitInflate() {
        return 0.3;
    }

    /** Called client-side every tick with the previous and current position. */
    protected abstract void clientTrail(Vec3 from, Vec3 to);

    protected void onHitTarget(ServerLevel level, Entity target) {
        Entity owner = getOwner();
        float dmg = damage;
        DamageSource src = owner instanceof LivingEntity living ? level.damageSources().mobProjectile(this, living) : level.damageSources().magic();
        target.hurtServer(level, src, dmg);
    }

    protected void onHitWall(ServerLevel level, BlockHitResult hit) {}

    protected void onExpire(ServerLevel level) {}

    protected void steer() {}

    @Override
    protected boolean canHitEntity(Entity target) {
        if (!target.isAlive() || target.isSpectator() || !target.isPickable()) return false;
        Entity owner = getOwner();
        if (owner != null && (target == owner || target.isPassengerOfSameVehicle(owner) || owner.isAlliedTo(target))) return false;
        if (owner != null && target instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(owner instanceof LivingEntity l ? l : null)) return false;
        return target instanceof LivingEntity;
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 from = position();
        if (level() instanceof ServerLevel server) {
            steer();
            if (gravity != 0) setDeltaMovement(getDeltaMovement().add(0, -gravity, 0));
            Vec3 v = getDeltaMovement();
            Vec3 to = from.add(v);
            if (stopsOnBlocks()) {
                BlockHitResult bhr = server.clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
                if (bhr.getType() != HitResult.Type.MISS) {
                    onHitWall(server, bhr);
                    discard();
                    return;
                }
            }
            AABB sweep = getBoundingBox().expandTowards(v).inflate(hitInflate());
            for (Entity e : server.getEntities(this, sweep, this::canHitEntity)) {
                if (alreadyHit.add(e.getId())) {
                    onHitTarget(server, e);
                    if (!piercing()) {
                        discard();
                        return;
                    }
                }
            }
            setPos(to.x, to.y, to.z);
            if (++life > maxLife) {
                onExpire(server);
                discard();
            }
        } else {
            Vec3 v = getDeltaMovement();
            setPos(from.x + v.x, from.y + v.y, from.z + v.z);
            clientTrail(from, position());
        }
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {}

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double dist) {
        return dist < 128 * 128;
    }
}
