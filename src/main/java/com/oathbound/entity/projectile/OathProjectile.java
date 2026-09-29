package com.oathbound.entity.projectile;

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

import java.util.HashSet;
import java.util.Set;

/**
 * Base for every spell, blade and bolt in Oathbound. Movement is simulated on the server (with optional
 * gravity and drag and a {@link #guide()} hook for homing/orbiting); clients just extrapolate and draw a
 * particle {@link #trail}. A projectile may pass through up to {@link #pierce} creatures.
 */
public abstract class OathProjectile extends Projectile {
    protected int age;
    protected int lifetime = 60;
    protected float damage = 5.0f;
    protected float gravity;
    protected float drag = 1.0f;
    protected int pierce;
    protected double reach = 0.3;
    private final Set<Integer> struck = new HashSet<>();

    protected OathProjectile(EntityType<? extends OathProjectile> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public void setDamage(float damage) {
        this.damage = damage;
    }

    /** Whether terrain stops this projectile. */
    protected boolean solid() {
        return true;
    }

    /** Called on the server every tick before moving (homing, orbiting). */
    protected void guide() {}

    protected abstract void trail(Vec3 from, Vec3 to);

    /** Default hit: magic-projectile damage from the owner. */
    protected void strike(ServerLevel level, Entity target) {
        dealDamage(level, target, damage);
    }

    protected final void dealDamage(ServerLevel level, Entity target, float amount) {
        Entity owner = getOwner();
        DamageSource src = owner instanceof LivingEntity l ? level.damageSources().mobProjectile(this, l) : level.damageSources().magic();
        target.hurtServer(level, src, amount);
    }

    protected void impact(ServerLevel level, BlockHitResult hit) {}

    protected void fizzle(ServerLevel level) {}

    @Override
    protected boolean canHitEntity(Entity target) {
        if (!(target instanceof LivingEntity) || !target.isAlive() || target.isSpectator()) return false;
        Entity owner = getOwner();
        if (owner == null) return true;
        if (target == owner || owner.isAlliedTo(target) || target.isPassengerOfSameVehicle(owner)) return false;
        return !(target instanceof net.minecraft.world.entity.TamableAnimal pet && owner instanceof LivingEntity lo && pet.isOwnedBy(lo));
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 from = position();
        if (!(level() instanceof ServerLevel server)) {
            Vec3 v = getDeltaMovement();
            setPos(from.add(v));
            trail(from, position());
            return;
        }
        guide();
        if (isRemoved()) return;
        Vec3 v = getDeltaMovement().scale(drag).add(0, -gravity, 0);
        setDeltaMovement(v);
        Vec3 to = from.add(v);
        if (solid()) {
            BlockHitResult wall = server.clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
            if (wall.getType() != HitResult.Type.MISS) {
                impact(server, wall);
                discard();
                return;
            }
        }
        AABB swept = getBoundingBox().expandTowards(v).inflate(reach);
        for (Entity e : server.getEntities(this, swept, this::canHitEntity)) {
            if (!struck.add(e.getId())) continue;
            strike(server, e);
            if (isRemoved()) return;
            if (struck.size() > pierce) {
                discard();
                return;
            }
        }
        setPos(to);
        if (++age >= lifetime) {
            fizzle(server);
            discard();
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
        return dist < 160 * 160;
    }
}
