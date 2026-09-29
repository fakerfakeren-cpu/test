package com.oathbound.entity;

import com.oathbound.registry.ModEntities;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

/**
 * A short-lived, purely visual spell effect drawn with real geometry rather than particles: a spinning rune
 * sigil, a pillar of light, an expanding shockwave ring, a beam between two points, or a floating halo.
 * Spawned on the server (so every nearby client sees the same moment) and never saved.
 */
public class SpellMarkEntity extends Entity {
    public enum Kind { SIGIL, WALL_SIGIL, PILLAR, RING, BEAM, HALO }

    /** Effect colours, as RGB. */
    public enum Hue {
        DAWN(0xFFD36B), GLOAM(0xA35CFF), ARCANE(0x6FA8FF), SPIRIT(0x6FF5E0), TIDE(0x3FE0C0), EMBER(0xFF7A2E), BLOOD(0xFF3048);

        public final int rgb;

        Hue(int rgb) {
            this.rgb = rgb;
        }
    }

    private static final EntityDataAccessor<Integer> KIND = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> HUE = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> SIZE = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> LIFE = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> EX = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> EY = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> EZ = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> GLYPH = SynchedEntityData.defineId(SpellMarkEntity.class, EntityDataSerializers.INT);

    public SpellMarkEntity(EntityType<? extends SpellMarkEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
        setNoGravity(true);
    }

    // ------------------------------------------------------------------ spawning helpers
    private static SpellMarkEntity make(ServerLevel level, Kind kind, Hue hue, Vec3 at, float size, int life) {
        SpellMarkEntity e = new SpellMarkEntity(ModEntities.SPELL_MARK.get(), level);
        e.setPos(at.x, at.y, at.z);
        e.entityData.set(KIND, kind.ordinal());
        e.entityData.set(HUE, hue.ordinal());
        e.entityData.set(SIZE, size);
        e.entityData.set(LIFE, Math.max(2, life));
        e.entityData.set(GLYPH, level.getRandom().nextInt(4));
        return e;
    }

    /** A rune circle lying on the ground (radius in blocks). */
    public static SpellMarkEntity sigil(ServerLevel level, Vec3 at, float radius, Hue hue, int life) {
        SpellMarkEntity e = make(level, Kind.SIGIL, hue, at.add(0, 0.03, 0), radius, life);
        level.addFreshEntity(e);
        return e;
    }

    /** A rune circle standing upright, facing along {@code facing} (a horizontal direction). */
    public static SpellMarkEntity wallSigil(ServerLevel level, Vec3 at, float radius, Hue hue, int life, float yaw) {
        SpellMarkEntity e = make(level, Kind.WALL_SIGIL, hue, at, radius, life);
        e.setYRot(yaw);
        level.addFreshEntity(e);
        return e;
    }

    /** A column of light rising from {@code at}; {@code radius} sets its width, height is 12x the radius. */
    public static SpellMarkEntity pillar(ServerLevel level, Vec3 at, float radius, Hue hue, int life) {
        SpellMarkEntity e = make(level, Kind.PILLAR, hue, at, radius, life);
        level.addFreshEntity(e);
        return e;
    }

    /** A ring that races outward along the ground to {@code radius} over its life. */
    public static SpellMarkEntity ring(ServerLevel level, Vec3 at, float radius, Hue hue, int life) {
        SpellMarkEntity e = make(level, Kind.RING, hue, at.add(0, 0.05, 0), radius, life);
        level.addFreshEntity(e);
        return e;
    }

    /** A crackling beam from {@code from} to {@code to}; {@code width} in blocks. */
    public static SpellMarkEntity beam(ServerLevel level, Vec3 from, Vec3 to, float width, Hue hue, int life) {
        SpellMarkEntity e = make(level, Kind.BEAM, hue, from, width, life);
        Vec3 d = to.subtract(from);
        e.entityData.set(EX, (float) d.x);
        e.entityData.set(EY, (float) d.y);
        e.entityData.set(EZ, (float) d.z);
        level.addFreshEntity(e);
        return e;
    }

    /** A floating crown of light (above a head, around a lantern). */
    public static SpellMarkEntity halo(ServerLevel level, Vec3 at, float radius, Hue hue, int life) {
        SpellMarkEntity e = make(level, Kind.HALO, hue, at, radius, life);
        level.addFreshEntity(e);
        return e;
    }

    // ------------------------------------------------------------------ state
    public Kind kind() {
        return Kind.values()[Math.floorMod(entityData.get(KIND), Kind.values().length)];
    }

    public Hue hue() {
        return Hue.values()[Math.floorMod(entityData.get(HUE), Hue.values().length)];
    }

    public float size() {
        return entityData.get(SIZE);
    }

    public int life() {
        return entityData.get(LIFE);
    }

    public int glyph() {
        return entityData.get(GLYPH);
    }

    public Vec3 end() {
        return new Vec3(entityData.get(EX), entityData.get(EY), entityData.get(EZ));
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(KIND, 0);
        builder.define(HUE, 0);
        builder.define(SIZE, 1f);
        builder.define(LIFE, 20);
        builder.define(EX, 0f);
        builder.define(EY, 0f);
        builder.define(EZ, 0f);
        builder.define(GLYPH, 0);
    }

    @Override
    public void tick() {
        super.tick();
        if (tickCount > life() && !level().isClientSide()) discard();
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
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double dist) {
        return dist < 192 * 192;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {}

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {}
}
