package com.oathbound.entity.projectile;

import com.oathbound.entity.boss.ArchmageVeylEntity;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Archmage Veyl's slow, homing arcane orb. Strike it with a weapon and it flies back at whoever cast it: a
 * reflected orb deals heavy damage to Veyl and staggers him.
 */
public class ArcaneOrbEntity extends OathProjectile {
    private LivingEntity target;
    private boolean reflected;

    public ArcaneOrbEntity(EntityType<? extends ArcaneOrbEntity> type, Level level) {
        super(type, level);
        this.lifetime = 160;
        this.damage = 7.0f;
    }

    public static ArcaneOrbEntity cast(ServerLevel level, LivingEntity owner, Vec3 from, LivingEntity target) {
        ArcaneOrbEntity e = new ArcaneOrbEntity(ModEntities.ARCANE_ORB.get(), level);
        e.setOwner(owner);
        e.setPos(from.x, from.y, from.z);
        e.target = target;
        e.setDeltaMovement(target.getEyePosition().subtract(from).normalize().scale(0.35));
        level.addFreshEntity(e);
        return e;
    }

    public boolean isReflected() {
        return reflected;
    }

    @Override
    protected void guide() {
        if (target != null && target.isAlive() && !reflected) {
            Vec3 want = target.getEyePosition().subtract(position()).normalize().scale(0.38);
            setDeltaMovement(getDeltaMovement().lerp(want, 0.06));
        }
    }

    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public float getPickRadius() {
        return 0.6f;
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (reflected || !(source.getEntity() instanceof Player player)) return false;
        Entity caster = getOwner();
        reflected = true;
        setOwner(player);
        target = caster instanceof LivingEntity l ? l : null;
        Vec3 dir = target != null ? target.getBoundingBox().getCenter().subtract(position()).normalize() : player.getLookAngle();
        setDeltaMovement(dir.scale(1.1));
        age = 0;
        lifetime = 80;
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ORB_REFLECT.get(), SoundSource.PLAYERS, 1.5f, 1.0f);
        Vfx.burst(level, ModParticles.SUNBURST.get(), position(), 16, 0.2, 0.15);
        return true;
    }

    @Override
    protected void strike(ServerLevel level, Entity hit) {
        if (reflected && hit instanceof ArchmageVeylEntity veyl) {
            veyl.onOrbReflected(level, this);
        } else {
            dealDamage(level, hit, damage);
            if (hit instanceof LivingEntity l) l.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOWNESS, 40, 1));
        }
        burst(level);
    }

    @Override
    protected void impact(ServerLevel level, BlockHitResult hit) {
        burst(level);
    }

    @Override
    protected void fizzle(ServerLevel level) {
        burst(level);
    }

    private void burst(ServerLevel level) {
        Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), position(), 20, 0.3, 0.1);
        Vfx.burst(level, ParticleTypes.WITCH, position(), 8, 0.3, 0.1);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ARCANE_ORB.get(), SoundSource.HOSTILE, 0.8f, 1.4f);
    }

    @Override
    protected void trail(Vec3 from, Vec3 to) {
        level().addAlwaysVisibleParticle(reflected ? ModParticles.SUNBURST.get() : ModParticles.ARCANE_GLYPH.get(), to.x, to.y, to.z, 0, 0, 0);
        for (int i = 0; i < 2; i++) {
            level().addParticle(ModParticles.ARCANE_GLYPH.get(), to.x + (random.nextDouble() - 0.5) * 0.5, to.y + (random.nextDouble() - 0.5) * 0.5, to.z + (random.nextDouble() - 0.5) * 0.5, 0, 0, 0);
        }
    }
}
