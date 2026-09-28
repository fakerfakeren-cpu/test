package com.astralfall.entity;

import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

import java.util.UUID;

/**
 * A miniature black hole. Drags creatures and items towards its core, then collapses with a
 * violent shockwave. Spawned by the Riftcaller, Singularity Grenades and Astraeus.
 */
public class SingularityEntity extends Entity {
    private static final EntityDataAccessor<Integer> LIFE = SynchedEntityData.defineId(SingularityEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> MAX_LIFE = SynchedEntityData.defineId(SingularityEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> RADIUS = SynchedEntityData.defineId(SingularityEntity.class, EntityDataSerializers.FLOAT);

    private UUID ownerId;
    private boolean hostile;
    private float collapseDamage = 10.0f;

    public SingularityEntity(EntityType<? extends SingularityEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public static SingularityEntity spawn(ServerLevel level, Vec3 at, LivingEntity owner, int life, float radius, float collapseDamage, boolean hostile) {
        SingularityEntity e = new SingularityEntity(ModEntities.SINGULARITY.get(), level);
        e.setPos(at.x, at.y, at.z);
        e.entityData.set(LIFE, life);
        e.entityData.set(MAX_LIFE, life);
        e.entityData.set(RADIUS, radius);
        e.ownerId = owner == null ? null : owner.getUUID();
        e.hostile = hostile;
        e.collapseDamage = collapseDamage;
        level.addFreshEntity(e);
        level.playSound(null, at.x, at.y, at.z, ModSounds.SINGULARITY_HUM.get(), SoundSource.PLAYERS, 2.0f, 1.0f);
        return e;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(LIFE, 80);
        builder.define(MAX_LIFE, 80);
        builder.define(RADIUS, 7.0f);
    }

    public float getRadius() {
        return entityData.get(RADIUS);
    }

    /** 0 → 1 over the lifetime; used by the renderer for grow / collapse animation. */
    public float getProgress(float partialTick) {
        int max = Math.max(1, entityData.get(MAX_LIFE));
        return Mth.clamp((max - entityData.get(LIFE) + partialTick) / max, 0f, 1f);
    }

    private boolean shouldAffect(Entity e) {
        if (e == this || !e.isAlive() || e.isSpectator()) return false;
        if (ownerId != null && e.getUUID().equals(ownerId)) return false;
        if (e instanceof Player p && p.isCreative()) return false;
        if (e instanceof com.astralfall.entity.boss.AstraeusEntity) return false;
        if (hostile) return e instanceof Player || e instanceof ItemEntity;
        if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isTame()) return false;
        return e instanceof LivingEntity || e instanceof ItemEntity;
    }

    @Override
    public void tick() {
        super.tick();
        float radius = getRadius();
        Vec3 c = position();
        if (level() instanceof ServerLevel server) {
            int life = entityData.get(LIFE) - 1;
            entityData.set(LIFE, life);
            for (Entity e : server.getEntities(this, getBoundingBox().inflate(radius), this::shouldAffect)) {
                Vec3 to = c.subtract(e.position().add(0, e.getBbHeight() * 0.5, 0));
                double d = to.length();
                if (d > radius || d < 0.01) continue;
                double strength = 0.12 + 0.35 * (1 - d / radius);
                e.setDeltaMovement(e.getDeltaMovement().scale(0.8).add(to.normalize().scale(strength)));
                e.hurtMarked = true;
                e.resetFallDistance();
                if (d < 2.2 && tickCount % 10 == 0 && e instanceof LivingEntity living) {
                    living.hurtServer(server, damageSource(server), 2.0f);
                }
            }
            if (tickCount % 20 == 0) server.playSound(null, c.x, c.y, c.z, ModSounds.SINGULARITY_HUM.get(), SoundSource.PLAYERS, 1.2f, 0.8f + random.nextFloat() * 0.3f);
            if (life <= 0) collapse(server);
        } else {
            float t = tickCount;
            for (int i = 0; i < 6; i++) {
                double a = t * 0.25 + i * Math.PI / 3;
                double r = radius * (0.35 + random.nextDouble() * 0.65);
                double x = c.x + Math.cos(a) * r, z = c.z + Math.sin(a) * r;
                double y = c.y + (random.nextDouble() - 0.5) * radius * 0.5;
                Vec3 v = c.subtract(x, y, z).normalize().scale(0.25 + random.nextDouble() * 0.2);
                level().addAlwaysVisibleParticle(i % 2 == 0 ? ModParticles.VOID_MOTE.get() : ParticleTypes.REVERSE_PORTAL, x, y, z, v.x + Math.sin(a) * 0.1, v.y, v.z - Math.cos(a) * 0.1);
            }
            level().addParticle(new DustParticleOptions(0x6a1fd0, 1.6f), c.x + (random.nextDouble() - 0.5), c.y + (random.nextDouble() - 0.5), c.z + (random.nextDouble() - 0.5), 0, 0, 0);
        }
    }

    private DamageSource damageSource(ServerLevel server) {
        Entity owner = ownerId == null ? null : server.getEntity(ownerId);
        return owner instanceof LivingEntity living ? server.damageSources().indirectMagic(this, living) : server.damageSources().magic();
    }

    private void collapse(ServerLevel server) {
        Vec3 c = position();
        float radius = getRadius();
        DamageSource src = damageSource(server);
        for (Entity e : server.getEntities(this, getBoundingBox().inflate(radius * 0.75), this::shouldAffect)) {
            Vec3 away = e.position().subtract(c);
            double d = Math.max(0.5, away.length());
            if (e instanceof LivingEntity living) {
                living.hurtServer(server, src, collapseDamage * (float) Mth.clamp(1.2 - d / (radius * 0.75), 0.3, 1.0));
            }
            e.setDeltaMovement(away.normalize().scale(1.6).add(0, 0.6, 0));
            e.hurtMarked = true;
        }
        FX.burst(server, ParticleTypes.EXPLOSION_EMITTER, c, 1, 0, 0);
        FX.sphere(server, ModParticles.VOID_MOTE.get(), c, radius * 0.6, 90);
        FX.ring(server, ParticleTypes.REVERSE_PORTAL, c, 1.0, 48, 0.0);
        FX.burst(server, ParticleTypes.END_ROD, c, 40, 0.3, 0.5);
        server.playSound(null, c.x, c.y, c.z, ModSounds.SINGULARITY_COLLAPSE.get(), SoundSource.PLAYERS, 3.0f, 1.0f);
        discard();
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        return false;
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double dist) {
        return dist < 160 * 160;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {}

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {}
}
