package com.oathbound.entity.projectile;

import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.util.Vfx;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** A spinning rune torn from an Animated Tome's pages. Stings and briefly weakens. */
public class GlyphBoltEntity extends OathProjectile {
    public GlyphBoltEntity(EntityType<? extends GlyphBoltEntity> type, Level level) {
        super(type, level);
        this.lifetime = 50;
        this.damage = 3.5f;
    }

    public static void shoot(ServerLevel level, LivingEntity owner, Vec3 from, Vec3 velocity) {
        GlyphBoltEntity e = new GlyphBoltEntity(ModEntities.GLYPH_BOLT.get(), level);
        e.setOwner(owner);
        e.setPos(from.x, from.y, from.z);
        e.setDeltaMovement(velocity);
        level.addFreshEntity(e);
    }

    @Override
    protected boolean canHitEntity(Entity t) {
        return !(t instanceof com.oathbound.entity.mob.AnimatedTomeEntity) && super.canHitEntity(t);
    }

    @Override
    protected void strike(ServerLevel level, Entity hit) {
        dealDamage(level, hit, damage);
        if (hit instanceof LivingEntity l) l.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 60, 0));
        Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), position(), 8, 0.2, 0.05);
    }

    @Override
    protected void impact(ServerLevel level, BlockHitResult hit) {
        Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), hit.getLocation(), 6, 0.1, 0.05);
    }

    @Override
    protected void trail(Vec3 from, Vec3 to) {
        level().addAlwaysVisibleParticle(ModParticles.ARCANE_GLYPH.get(), to.x, to.y, to.z, 0, 0, 0);
        level().addParticle(net.minecraft.core.particles.ParticleTypes.ENCHANT, from.x, from.y, from.z, 0, 0, 0);
    }
}
