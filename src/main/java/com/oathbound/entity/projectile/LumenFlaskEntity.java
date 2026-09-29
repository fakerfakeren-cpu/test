package com.oathbound.entity.projectile;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.block.WisplightBlock;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Vfx;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** A thrown Lumen Flask: a flare of daylight that blinds, burns the Gloam, and leaves lingering wisplights. */
public class LumenFlaskEntity extends ThrowableItemProjectile {
    public LumenFlaskEntity(EntityType<? extends LumenFlaskEntity> type, Level level) {
        super(type, level);
    }

    public LumenFlaskEntity(Level level, LivingEntity owner, ItemStack stack) {
        super(ModEntities.LUMEN_FLASK.get(), owner, level, stack);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.LUMEN_FLASK.get();
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel server) {
            flare(server, hit.getLocation(), getOwner());
            discard();
        }
    }

    public static void flare(ServerLevel level, Vec3 at, Entity owner) {
        level.playSound(null, at.x, at.y, at.z, ModSounds.FLASK_SHATTER.get(), SoundSource.PLAYERS, 1.4f, 1.0f);
        Vfx.burst(level, ModParticles.SUNBURST.get(), at, 30, 0.3, 0.25);
        Vfx.sphere(level, ModParticles.SUNBURST.get(), at, 2.5, 60);
        Vfx.burst(level, ModParticles.LUMEN_MOTE.get(), at, 40, 1.5, 0.05);
        SpellMarkEntity.ring(level, at.add(0, -0.3, 0), 5.5f, SpellMarkEntity.Hue.DAWN, 12);
        SpellMarkEntity.halo(level, at, 1.1f, SpellMarkEntity.Hue.DAWN, 20);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(5))) {
            if (e == owner || !e.isAlive() || e.distanceToSqr(at) > 25) continue;
            if (e.typeHolder().is(ModTags.GLOAM_CREATURES)) {
                e.hurtServer(level, level.damageSources().magic(), 8.0f);
                e.igniteForSeconds(4);
            }
            if (!(e instanceof net.minecraft.world.entity.player.Player)) e.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 80, 0));
            e.addEffect(new MobEffectInstance(MobEffects.GLOWING, 160, 0));
        }
        BlockPos c = BlockPos.containing(at);
        var r = level.getRandom();
        for (int i = 0; i < 6; i++) {
            BlockPos p = c.offset(r.nextInt(7) - 3, r.nextInt(3), r.nextInt(7) - 3);
            WisplightBlock.place(level, p, true);
        }
        WisplightBlock.place(level, c.above(), true);
    }
}
