package com.oathbound.entity.boss;

import com.oathbound.entity.projectile.ArcaneOrbEntity;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Archmage Veyl, the Hollow Magus: second keeper. He hovers and blinks about his sanctum. His slow Arcane Orbs
 * can be struck back at him (a returned orb stuns him and hurts badly). Twice he splits into Mirror Images;
 * only the true Veyl's staff burns gold, and each false image bursts in a spray of arcane shards when struck.
 * His Gravity Glyph lifts anyone standing in it high into the air, then lets go.
 */
public class ArchmageVeylEntity extends KeeperEntity {
    public static final int ORBS = 1, GLYPH = 2, MIRROR = 3, BLINK = 4, DAZED = 5;
    private static final EntityDataAccessor<Boolean> ILLUSION = SynchedEntityData.defineId(ArchmageVeylEntity.class, EntityDataSerializers.BOOLEAN);
    private BlockPos home;
    private Vec3 hover = Vec3.ZERO;
    private Vec3 glyphAt = Vec3.ZERO;
    private int mirrorsCast;
    private int hitsTaken;
    private UUID master;
    private int illusionLife;
    private final List<UUID> images = new ArrayList<>();

    public ArchmageVeylEntity(EntityType<? extends ArchmageVeylEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PURPLE);
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 220.0)
            .add(Attributes.ARMOR, 4.0)
            .add(Attributes.ATTACK_DAMAGE, 6.0)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FLYING_SPEED, 0.4)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.6);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(ILLUSION, false);
    }

    public boolean isIllusion() {
        return entityData.get(ILLUSION);
    }

    @Override
    protected String questId() {
        return "veyl";
    }

    @Override
    protected float baseHealth() {
        return isIllusion() ? 1f : 220f;
    }

    @Override
    protected double wakeRange() {
        return 9.0;
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        if (home == null) home = blockPosition();
        level.playSound(null, getX(), getY(), getZ(), ModSounds.VEYL_LAUGH.get(), SoundSource.HOSTILE, 3.0f, 1.0f);
        Vfx.sphere(level, ModParticles.ARCANE_GLYPH.get(), position().add(0, 1.2, 0), 2.5, 80);
    }

    private Vec3 homeVec() {
        if (home == null) home = blockPosition();
        return Vec3.atBottomCenterOf(home);
    }

    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        if (isIllusion()) {
            thinkIllusion(level, target);
            return;
        }
        // drift towards the chosen hover point
        Vec3 want = hover.equals(Vec3.ZERO) ? homeVec().add(0, 2.5, 0) : hover;
        Vec3 d = want.subtract(position());
        setDeltaMovement(getDeltaMovement().scale(0.8).add(d.scale(0.04)).add(0, Math.sin(tickCount * 0.1) * 0.01, 0));
        if (target == null) return;
        getLookControl().setLookAt(target, 30f, 30f);
        faceTarget(target);
        int t = moveTicks();
        if (mirrorsCast < 2 && move() == IDLE && getHealth() < getMaxHealth() * (mirrorsCast == 0 ? 0.66f : 0.33f)) {
            mirrorsCast++;
            startMove(MIRROR);
        }
        switch (move()) {
            case IDLE -> {
                if (tickCount % 60 == 0) pickHover(target);
                if (--cooldown <= 0) {
                    int r = random.nextInt(10);
                    startMove(r < 5 ? ORBS : r < 8 ? GLYPH : BLINK);
                }
            }
            case ORBS -> {
                int count = getHealth() < getMaxHealth() * 0.5f ? 3 : 2;
                if (t < 20) Vfx.spiralIn(level, ModParticles.ARCANE_GLYPH.get(), staffTip(), 1.5, 3, t);
                if (t >= 20 && t < 20 + count * 12 && (t - 20) % 12 == 0) {
                    ArcaneOrbEntity.cast(level, this, staffTip(), target);
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.ARCANE_ORB.get(), SoundSource.HOSTILE, 1.5f, 0.8f);
                }
                if (t > 20 + count * 12 + 10) endMove(50 + random.nextInt(20));
            }
            case GLYPH -> {
                if (t == 1) {
                    glyphAt = target.position();
                    level.playSound(null, glyphAt.x, glyphAt.y, glyphAt.z, ModSounds.VEYL_MIRROR.get(), SoundSource.HOSTILE, 1.5f, 0.6f);
                }
                if (t < 28 && t % 2 == 0) {
                    Vfx.ring(level, ModParticles.ARCANE_GLYPH.get(), glyphAt.add(0, 0.15, 0), 3.0, 30, 0.0);
                    Vfx.ring(level, ModParticles.ARCANE_GLYPH.get(), glyphAt.add(0, 0.15, 0), 1.5, 14, 0.02);
                }
                if (t == 28) {
                    Vfx.column(level, ModParticles.ARCANE_GLYPH.get(), glyphAt, 8, 60);
                    level.playSound(null, glyphAt.x, glyphAt.y, glyphAt.z, ModSounds.ARCANE_CHAIN.get(), SoundSource.HOSTILE, 2f, 0.6f);
                    for (Player p : challengers(level, 30)) {
                        if (p.position().distanceTo(glyphAt) < 3.2) p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 28, 5));
                    }
                }
                if (t > 40) endMove(40 + random.nextInt(20));
            }
            case BLINK -> {
                if (t == 1) blink(level, target);
                if (t > 6) endMove(20);
            }
            case MIRROR -> {
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.VEYL_MIRROR.get(), SoundSource.HOSTILE, 3.0f, 1.0f);
                if (t < 30) Vfx.sphere(level, ModParticles.ARCANE_GLYPH.get(), position().add(0, 1.2, 0), 1.5 + t * 0.05, 30);
                if (t == 30) splitImages(level, target);
                if (t > 40) endMove(40);
            }
            case DAZED -> {
                setDeltaMovement(getDeltaMovement().add(0, -0.03, 0));
                if (t % 5 == 0) Vfx.burst(level, ParticleTypes.CRIT, position().add(0, 2.4, 0), 4, 0.3, 0.05);
                if (t > 80) {
                    endMove(20);
                    blink(level, target);
                }
            }
            default -> endMove(20);
        }
    }

    private void faceTarget(LivingEntity t) {
        double dx = t.getX() - getX(), dz = t.getZ() - getZ();
        float yaw = (float) (Math.atan2(dz, dx) * 180 / Math.PI) - 90f;
        setYRot(yaw);
        yBodyRot = yaw;
        yHeadRot = yaw;
    }

    private void pickHover(LivingEntity target) {
        double a = random.nextDouble() * Math.PI * 2;
        hover = homeVec().add(Math.cos(a) * 4.5, 2.0 + random.nextDouble() * 2.5, Math.sin(a) * 4.5);
    }

    public Vec3 staffTip() {
        Vec3 side = Vec3.directionFromRotation(0, yBodyRot + 90);
        return position().add(side.scale(-0.55)).add(0, 2.5, 0);
    }

    private void blink(ServerLevel level, LivingEntity target) {
        Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), position().add(0, 1.2, 0), 40, 0.5, 0.1);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.VEYL_BLINK.get(), SoundSource.HOSTILE, 2.0f, 1.0f);
        for (int tries = 0; tries < 12; tries++) {
            double a = random.nextDouble() * Math.PI * 2;
            Vec3 p = homeVec().add(Math.cos(a) * (2 + random.nextDouble() * 4), 1 + random.nextDouble() * 3, Math.sin(a) * (2 + random.nextDouble() * 4));
            BlockPos bp = BlockPos.containing(p);
            BlockState s1 = level.getBlockState(bp), s2 = level.getBlockState(bp.above()), s3 = level.getBlockState(bp.above(2));
            if (s1.isAir() && s2.isAir() && s3.isAir()) {
                teleportTo(p.x, p.y, p.z);
                hover = p;
                break;
            }
        }
        Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), position().add(0, 1.2, 0), 40, 0.5, 0.1);
        hitsTaken = 0;
    }

    private void splitImages(ServerLevel level, LivingEntity target) {
        for (UUID id : images) {
            var e = level.getEntity(id);
            if (e != null) e.discard();
        }
        images.clear();
        List<Vec3> spots = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            double a = i * Math.PI / 2 + random.nextDouble() * 0.5;
            spots.add(homeVec().add(Math.cos(a) * 4, 2.2, Math.sin(a) * 4));
        }
        int real = random.nextInt(4);
        for (int i = 0; i < 4; i++) {
            Vec3 s = spots.get(i);
            if (i == real) {
                teleportTo(s.x, s.y, s.z);
                hover = s;
                continue;
            }
            ArchmageVeylEntity img = ModEntities.ARCHMAGE_VEYL.get().create(level, EntitySpawnReason.MOB_SUMMONED);
            if (img == null) continue;
            img.entityData.set(ILLUSION, true);
            img.master = getUUID();
            img.home = home;
            img.hover = s;
            img.illusionLife = 600;
            img.snapTo(s.x, s.y, s.z, getYRot(), 0);
            img.wake(level, target instanceof Player p ? p : null);
            img.bar.setVisible(false);
            var attr = img.getAttribute(Attributes.MAX_HEALTH);
            if (attr != null) attr.setBaseValue(1.0);
            img.setHealth(1.0f);
            img.setTarget(target);
            level.addFreshEntity(img);
            images.add(img.getUUID());
            Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), s.add(0, 1.2, 0), 30, 0.4, 0.1);
        }
    }

    private void thinkIllusion(ServerLevel level, LivingEntity target) {
        Vec3 d = hover.subtract(position());
        setDeltaMovement(getDeltaMovement().scale(0.8).add(d.scale(0.04)));
        var m = master == null ? null : level.getEntity(master);
        if (--illusionLife <= 0 || m == null || !m.isAlive()) {
            vanish(level, false);
            return;
        }
        if (target == null) return;
        faceTarget(target);
        if (--cooldown <= 0) {
            ArcaneOrbEntity orb = ArcaneOrbEntity.cast(level, this, staffTip(), target);
            orb.setDamage(3.0f);
            cooldown = 70 + random.nextInt(40);
        }
    }

    private void vanish(ServerLevel level, boolean struck) {
        Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), position().add(0, 1.2, 0), 50, 0.6, 0.2);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.VEYL_BLINK.get(), SoundSource.HOSTILE, 1.5f, 1.6f);
        if (struck) {
            for (Player p : challengers(level, 3.0)) p.hurtServer(level, damageSources().indirectMagic(this, this), 3.0f);
        }
        discard();
    }

    /** A reflected orb struck the Archmage. */
    public void onOrbReflected(ServerLevel level, ArcaneOrbEntity orb) {
        if (isIllusion()) {
            vanish(level, false);
            return;
        }
        Player by = orb.getOwner() instanceof Player p ? p : null;
        super.hurtServer(level, by != null ? damageSources().indirectMagic(orb, by) : damageSources().magic(), 24f);
        startMove(DAZED);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.VEYL_LAUGH.get(), SoundSource.HOSTILE, 2.0f, 0.6f);
        Vfx.sphere(level, ModParticles.SUNBURST.get(), position().add(0, 1.2, 0), 1.8, 60);
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (source.getDirectEntity() instanceof ArcaneOrbEntity) return false;
        if (isIllusion()) {
            if (source.getEntity() instanceof Player) vanish(level, true);
            return false;
        }
        if (move() == DAZED) amount *= 1.5f;
        boolean hurt = super.hurtServer(level, source, amount);
        if (hurt && source.getDirectEntity() instanceof Player && move() != DAZED && ++hitsTaken >= 3) {
            endMove(10);
            startMove(BLINK);
        }
        return hurt;
    }

    @Override
    public void die(DamageSource source) {
        if (isIllusion()) {
            discard();
            return;
        }
        if (level() instanceof ServerLevel level) {
            for (UUID id : images) {
                var e = level.getEntity(id);
                if (e != null) e.discard();
            }
        }
        super.die(source);
    }

    @Override
    protected void dropAllDeathLoot(ServerLevel level, DamageSource source) {
        if (!isIllusion()) super.dropAllDeathLoot(level, source);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide()) {
            if (random.nextInt(isIllusion() ? 4 : 2) == 0) {
                level().addParticle(ModParticles.ARCANE_GLYPH.get(), getRandomX(0.8), getY() + random.nextDouble() * 2.2, getRandomZ(0.8), 0, 0.02, 0);
            }
            if (!isIllusion() && !isSleeping()) {
                Vec3 tip = position().add(Vec3.directionFromRotation(0, yBodyRot + 90).scale(-0.55)).add(0, 2.5, 0);
                level().addParticle(ModParticles.SUNBURST.get(), tip.x, tip.y, tip.z, 0, 0.01, 0);
            }
        }
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : ModSounds.VEYL_LAUGH.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 300;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.VEYL_BLINK.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.VEYL_MIRROR.get();
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putBoolean("Illusion", isIllusion());
        if (home != null) out.putIntArray("Home", new int[]{home.getX(), home.getY(), home.getZ()});
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        entityData.set(ILLUSION, in.getBooleanOr("Illusion", false));
        in.getIntArray("Home").ifPresent(a -> {
            if (a.length == 3) home = new BlockPos(a[0], a[1], a[2]);
        });
        if (isIllusion()) discard();
    }
}
