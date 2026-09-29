package com.rimeheart.entity.projectile;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModEntities;
import com.rimeheart.registry.ModItems;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.util.FX;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Thrown Frost Charge: a freezing burst that chills mobs and skins nearby water with (melting) ice. */
public class FrostChargeEntity extends ThrowableItemProjectile {
    public FrostChargeEntity(EntityType<? extends FrostChargeEntity> type, Level level) {
        super(type, level);
    }

    public FrostChargeEntity(Level level, LivingEntity owner, ItemStack stack) {
        super(ModEntities.FROST_CHARGE.get(), owner, level, stack);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.FROST_CHARGE.get();
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel server) {
            burst(server, hit.getLocation(), getOwner());
            discard();
        }
    }

    public static void burst(ServerLevel level, Vec3 at, Entity owner) {
        FX.burst(level, ParticleTypes.SNOWFLAKE, at, 60, 1.2, 0.08);
        FX.burst(level, ModParticles.SNOW_PUFF.get(), at, 25, 0.8, 0.03);
        FX.sphere(level, ModParticles.FROST_GLINT.get(), at, 2.5, 50);
        level.playSound(null, at.x, at.y, at.z, ModSounds.ICE_SHATTER.get(), SoundSource.PLAYERS, 1.3f, 0.8f);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(3.5))) {
            if (e == owner || !e.isAlive()) continue;
            if (e.distanceToSqr(at) > 3.5 * 3.5) continue;
            e.hurtServer(level, owner instanceof LivingEntity l ? level.damageSources().indirectMagic(l, l) : level.damageSources().magic(), 2.0f);
            Frost.chill(e, 200);
        }
        BlockPos c = BlockPos.containing(at);
        for (BlockPos p : BlockPos.betweenClosed(c.offset(-3, -2, -3), c.offset(3, 1, 3))) {
            if (p.distSqr(c) > 10) continue;
            BlockState s = level.getBlockState(p);
            if (s.is(Blocks.WATER) && s.getFluidState().is(Fluids.WATER) && s.getFluidState().isSource() && level.getBlockState(p.above()).isAir()) {
                level.setBlockAndUpdate(p, Blocks.FROSTED_ICE.defaultBlockState());
                level.scheduleTick(p.immutable(), Blocks.FROSTED_ICE, Mth.nextInt(level.getRandom(), 60, 120));
            }
        }
    }
}
