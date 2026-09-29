package com.oathbound.entity.projectile;

import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Vfx;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * One of the six blades of Morvane's Crown of Blades. It circles the king's head for a while, then turns and
 * flies straight at its victim. Its flight is telegraphed by a thin violet line before it launches.
 */
public class CrownBladeEntity extends OathProjectile {
    private static final EntityDataAccessor<Boolean> LAUNCHED = SynchedEntityData.defineId(CrownBladeEntity.class, EntityDataSerializers.BOOLEAN);
    private LivingEntity target;
    private int slot;
    private int launchAt;

    public CrownBladeEntity(EntityType<? extends CrownBladeEntity> type, Level level) {
        super(type, level);
        this.lifetime = 200;
        this.damage = 8.0f;
    }

    public static CrownBladeEntity summon(ServerLevel level, LivingEntity owner, LivingEntity target, int slot, int launchAt, float damage) {
        CrownBladeEntity e = new CrownBladeEntity(ModEntities.CROWN_BLADE.get(), level);
        e.setOwner(owner);
        e.target = target;
        e.slot = slot;
        e.launchAt = launchAt;
        e.damage = damage;
        Vec3 p = e.orbitPos(owner, 0);
        e.setPos(p.x, p.y, p.z);
        level.addFreshEntity(e);
        return e;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(LAUNCHED, false);
    }

    public boolean isLaunched() {
        return entityData.get(LAUNCHED);
    }

    private Vec3 orbitPos(Entity owner, int t) {
        double a = t * 0.12 + slot * Math.PI / 3;
        return owner.position().add(Math.cos(a) * 2.6, owner.getBbHeight() + 0.8 + Math.sin(t * 0.2 + slot) * 0.2, Math.sin(a) * 2.6);
    }

    @Override
    protected boolean solid() {
        return isLaunched();
    }

    @Override
    protected boolean canHitEntity(Entity t) {
        return isLaunched() && !t.typeHolder().is(ModTags.GLOAM_CREATURES) && super.canHitEntity(t);
    }

    @Override
    protected void guide() {
        Entity owner = getOwner();
        if (!isLaunched()) {
            if (owner == null || !owner.isAlive()) {
                discard();
                return;
            }
            Vec3 want = orbitPos(owner, age + 1);
            setDeltaMovement(want.subtract(position()));
            if (age == launchAt - 10 && target != null && level() instanceof ServerLevel s) {
                Vfx.line(s, ModParticles.GLOAM_WISP.get(), position(), target.getEyePosition(), 0.6);
            }
            if (age >= launchAt) {
                entityData.set(LAUNCHED, true);
                Vec3 aim = target != null && target.isAlive() ? target.getEyePosition().subtract(position()).normalize() : new Vec3(0, -1, 0);
                setDeltaMovement(aim.scale(1.25));
                playSound(ModSounds.BLADE_CROWN.get(), 1.2f, 1.3f);
            }
        }
    }

    @Override
    protected void strike(ServerLevel level, Entity hit) {
        dealDamage(level, hit, damage);
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position(), 12, 0.2, 0.1);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_SLASH.get(), SoundSource.HOSTILE, 1.0f, 1.4f);
    }

    @Override
    protected void impact(ServerLevel level, BlockHitResult hit) {
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), hit.getLocation(), 10, 0.2, 0.05);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ANCHOR_HIT.get(), SoundSource.HOSTILE, 0.8f, 1.5f);
    }

    @Override
    protected void trail(Vec3 from, Vec3 to) {
        if (isLaunched() || tickCount % 3 == 0) level().addAlwaysVisibleParticle(ModParticles.GLOAM_WISP.get(), from.x, from.y, from.z, 0, 0, 0);
    }
}
