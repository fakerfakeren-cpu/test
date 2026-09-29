package com.rimeheart.entity.projectile;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModEntities;
import com.rimeheart.registry.ModItems;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.registry.ModTags;
import com.rimeheart.util.FX;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ItemSupplier;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** A spinning shard of rime ice. Fired by the Rimebow, Frost Wraiths and the Frost Sovereign; chills what it hits. */
public class IceShardEntity extends MagicProjectile implements ItemSupplier {
    private int chill = 60;
    private LivingEntity target;
    private int delay;

    public IceShardEntity(EntityType<? extends IceShardEntity> type, Level level) {
        super(type, level);
        this.maxLife = 80;
        this.damage = 5.0f;
    }

    public static IceShardEntity shoot(ServerLevel level, LivingEntity owner, Vec3 from, Vec3 velocity, float damage, int chill) {
        IceShardEntity e = new IceShardEntity(ModEntities.ICE_SHARD.get(), level);
        e.setOwner(owner);
        e.setPos(from.x, from.y, from.z);
        e.setDeltaMovement(velocity);
        e.damage = damage;
        e.chill = chill;
        level.addFreshEntity(e);
        return e;
    }

    /** A shard that hangs in the air for {@code delay} ticks, then homes in on {@code target}. */
    public static IceShardEntity barrage(ServerLevel level, LivingEntity owner, Vec3 from, LivingEntity target, int delay, float damage) {
        IceShardEntity e = shoot(level, owner, from, new Vec3(level.getRandom().nextGaussian() * 0.05, 0.12, level.getRandom().nextGaussian() * 0.05), damage, 70);
        e.target = target;
        e.delay = delay;
        e.maxLife = 140;
        return e;
    }

    @Override
    protected boolean canHitEntity(Entity t) {
        Entity owner = getOwner();
        if (owner != null && owner.typeHolder().is(ModTags.WINTER_CREATURES) && t.typeHolder().is(ModTags.WINTER_CREATURES)) return false;
        return super.canHitEntity(t);
    }

    @Override
    protected void steer() {
        if (target == null) return;
        if (life < delay) {
            setDeltaMovement(getDeltaMovement().scale(0.85));
            return;
        }
        if (life == delay) playSound(ModSounds.ICICLE_SHOOT.get(), 1.5f, 0.8f);
        if (target.isAlive()) {
            Vec3 want = target.getEyePosition().subtract(position()).normalize().scale(0.8);
            setDeltaMovement(getDeltaMovement().lerp(want, life < delay + 16 ? 0.3 : 0.05));
        }
    }

    @Override
    protected void onHitTarget(ServerLevel level, Entity hit) {
        super.onHitTarget(level, hit);
        if (hit instanceof LivingEntity l) Frost.chill(l, chill);
        FX.burst(level, ModParticles.FROST_GLINT.get(), hit.getBoundingBox().getCenter(), 12, 0.3, 0.1);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ICE_SHATTER.get(), SoundSource.NEUTRAL, 0.8f, 1.3f);
    }

    @Override
    protected void onHitWall(ServerLevel level, BlockHitResult hit) {
        FX.burst(level, ParticleTypes.SNOWFLAKE, hit.getLocation(), 10, 0.2, 0.05);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ICE_SHATTER.get(), SoundSource.NEUTRAL, 0.6f, 1.5f);
    }

    @Override
    protected void clientTrail(Vec3 from, Vec3 to) {
        level().addParticle(ParticleTypes.SNOWFLAKE, from.x, from.y, from.z, 0, 0, 0);
        if (tickCount % 2 == 0) level().addAlwaysVisibleParticle(ModParticles.FROST_GLINT.get(), to.x, to.y, to.z, 0, 0, 0);
    }

    @Override
    public ItemStack getItem() {
        return new ItemStack(ModItems.RIME_SHARD.get());
    }
}
