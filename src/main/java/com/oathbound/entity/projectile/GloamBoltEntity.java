package com.oathbound.entity.projectile;

import com.oathbound.registry.ModEffects;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Vfx;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** A bolt of solid dusk, loosed by Morvane when he is the Hollow. Weakly homing; inflicts Gloamrot. */
public class GloamBoltEntity extends OathProjectile {
    private LivingEntity target;

    public GloamBoltEntity(EntityType<? extends GloamBoltEntity> type, Level level) {
        super(type, level);
        this.lifetime = 100;
        this.damage = 6.0f;
    }

    public static void shoot(ServerLevel level, LivingEntity owner, Vec3 from, LivingEntity target, float damage) {
        GloamBoltEntity e = new GloamBoltEntity(ModEntities.GLOAM_BOLT.get(), level);
        e.setOwner(owner);
        e.setPos(from.x, from.y, from.z);
        e.target = target;
        e.damage = damage;
        e.setDeltaMovement(target.getEyePosition().subtract(from).normalize().scale(0.6));
        level.addFreshEntity(e);
    }

    @Override
    protected boolean canHitEntity(Entity t) {
        return !t.typeHolder().is(ModTags.GLOAM_CREATURES) && super.canHitEntity(t);
    }

    @Override
    protected void guide() {
        if (target != null && target.isAlive() && age < 50) {
            setDeltaMovement(getDeltaMovement().lerp(target.getEyePosition().subtract(position()).normalize().scale(0.6), 0.05));
        }
    }

    @Override
    protected void strike(ServerLevel level, Entity hit) {
        dealDamage(level, hit, damage);
        if (hit instanceof LivingEntity l) l.addEffect(new MobEffectInstance(ModEffects.holder(ModEffects.GLOAMROT), 100, 0));
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position(), 16, 0.3, 0.06);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ARCANE_ORB.get(), SoundSource.HOSTILE, 0.8f, 0.6f);
    }

    @Override
    protected void impact(ServerLevel level, BlockHitResult hit) {
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), hit.getLocation(), 10, 0.2, 0.05);
    }

    @Override
    protected void trail(Vec3 from, Vec3 to) {
        level().addAlwaysVisibleParticle(ModParticles.GLOAM_WISP.get(), to.x, to.y, to.z, 0, 0, 0);
        level().addParticle(ModParticles.GLOAM_WISP.get(), from.x, from.y, from.z, 0, 0.01, 0);
    }
}
