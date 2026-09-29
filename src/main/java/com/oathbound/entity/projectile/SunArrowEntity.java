package com.oathbound.entity.projectile;

import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** A shaft of dawnlight from the Dawnstring Longbow. Fully drawn shots pierce and Sunmark their targets. */
public class SunArrowEntity extends OathProjectile {
    private boolean full;

    public SunArrowEntity(EntityType<? extends SunArrowEntity> type, Level level) {
        super(type, level);
        this.lifetime = 60;
        this.gravity = 0.012f;
    }

    public SunArrowEntity(Level level, LivingEntity owner, boolean full) {
        this(ModEntities.SUN_ARROW.get(), level);
        setOwner(owner);
        this.full = full;
        this.pierce = full ? 3 : 0;
    }


    @Override
    protected void strike(ServerLevel level, Entity hit) {
        Entity owner = getOwner();
        var src = owner instanceof LivingEntity l ? level.damageSources().mobProjectile(this, l) : level.damageSources().magic();
        hit.hurtServer(level, src, damage);
        if (hit instanceof LivingEntity l && full) {
            GameEvents.sunmark(l, 200);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.SUNMARK.get(), SoundSource.PLAYERS, 1.0f, 1.0f);
        }
        Vfx.burst(level, ModParticles.SUNBURST.get(), hit.getBoundingBox().getCenter(), 10, 0.2, 0.1);
    }

    @Override
    protected void impact(ServerLevel level, BlockHitResult hit) {
        Vfx.burst(level, ModParticles.SUNBURST.get(), hit.getLocation(), 8, 0.1, 0.05);
        Vfx.burst(level, ModParticles.EMBER.get(), hit.getLocation(), 6, 0.1, 0.05);
    }

    @Override
    protected void trail(Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        for (int i = 0; i < 3; i++) {
            Vec3 p = from.add(d.scale(i / 3.0));
            level().addAlwaysVisibleParticle(ModParticles.SUNBURST.get(), p.x, p.y, p.z, 0, 0, 0);
        }
    }
}
