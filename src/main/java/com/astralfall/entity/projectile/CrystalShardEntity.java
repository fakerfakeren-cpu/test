package com.astralfall.entity.projectile;

import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModParticles;
import com.astralfall.util.FX;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ItemSupplier;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** One of Astraeus' orbiting crystals, launched at a player. Rendered as a spinning Skyshard. */
public class CrystalShardEntity extends AstralProjectile implements ItemSupplier {
    private LivingEntity target;
    private int delay;

    public CrystalShardEntity(EntityType<? extends CrystalShardEntity> type, Level level) {
        super(type, level);
        this.maxLife = 120;
        this.damage = 7.0f;
    }

    public static CrystalShardEntity launch(Level level, LivingEntity owner, Vec3 from, LivingEntity target, int delay) {
        CrystalShardEntity e = new CrystalShardEntity(ModEntities.CRYSTAL_SHARD.get(), level);
        e.setOwner(owner);
        e.setPos(from.x, from.y, from.z);
        e.target = target;
        e.delay = delay;
        e.setDeltaMovement(new Vec3(level.getRandom().nextGaussian() * 0.1, 0.25, level.getRandom().nextGaussian() * 0.1));
        level.addFreshEntity(e);
        return e;
    }

    @Override
    protected boolean voidBane() {
        return false;
    }

    @Override
    protected void steer() {
        if (life < delay) {
            setDeltaMovement(getDeltaMovement().scale(0.9));
            return;
        }
        if (life == delay) playSound(SoundEvents.AMETHYST_BLOCK_CHIME, 2.0f, 0.5f);
        if (target != null && target.isAlive()) {
            Vec3 want = target.getEyePosition().subtract(position()).normalize().scale(0.85);
            setDeltaMovement(getDeltaMovement().lerp(want, life < delay + 20 ? 0.25 : 0.06));
        }
    }

    @Override
    protected void onHitTarget(ServerLevel level, Entity hit) {
        super.onHitTarget(level, hit);
        FX.burst(level, ModParticles.STAR_SPARKLE.get(), hit.getBoundingBox().getCenter(), 16, 0.4, 0.2);
        level.playSound(null, getX(), getY(), getZ(), SoundEvents.AMETHYST_CLUSTER_BREAK, SoundSource.HOSTILE, 1.5f, 1.2f);
    }

    @Override
    protected void onHitWall(ServerLevel level, BlockHitResult hit) {
        FX.burst(level, ModParticles.STAR_SPARKLE.get(), hit.getLocation(), 16, 0.4, 0.2);
        level.playSound(null, getX(), getY(), getZ(), SoundEvents.AMETHYST_CLUSTER_BREAK, SoundSource.HOSTILE, 1.2f, 1.0f);
    }

    @Override
    protected void clientTrail(Vec3 from, Vec3 to) {
        level().addAlwaysVisibleParticle(ModParticles.VOID_MOTE.get(), to.x, to.y, to.z, 0, 0, 0);
        if (tickCount % 2 == 0) level().addParticle(ParticleTypes.END_ROD, from.x, from.y, from.z, 0, 0, 0);
    }

    @Override
    public ItemStack getItem() {
        return new ItemStack(ModItems.SKYSHARD.get());
    }
}
