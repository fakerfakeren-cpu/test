package com.oathbound.entity.boss;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.entity.mob.SpectralHousecarlEntity;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * Hrodgar, the Barrow-King: third keeper, a giant in grave-gold with a chain flail. His Flail Sweep cuts
 * everything in front of him; his Grave Slam sends a ring of force racing outward (jump it!). He raises
 * Spectral Housecarls who are oath-tethered to him: while any lives, he shrugs off most harm. Below a third
 * of his health he Devours what remains of his guard to heal.
 */
public class HrodgarEntity extends KeeperEntity {
    public static final int SWEEP = 1, SLAM = 2, RAISE = 3, DEVOUR = 4;
    private static final EntityDataAccessor<Integer> TETHERS = SynchedEntityData.defineId(HrodgarEntity.class, EntityDataSerializers.INT);
    private final List<UUID> guard = new ArrayList<>();
    private final Set<UUID> slamHit = new HashSet<>();
    private boolean devoured;
    private int raises;
    private Vec3 slamCenter = Vec3.ZERO;

    public HrodgarEntity(EntityType<? extends HrodgarEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.YELLOW);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 300.0)
            .add(Attributes.ARMOR, 10.0)
            .add(Attributes.ARMOR_TOUGHNESS, 4.0)
            .add(Attributes.ATTACK_DAMAGE, 12.0)
            .add(Attributes.MOVEMENT_SPEED, 0.23)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
            .add(Attributes.STEP_HEIGHT, 1.5);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(TETHERS, 0);
    }

    public int tethers() {
        return entityData.get(TETHERS);
    }

    @Override
    protected String questId() {
        return "hrodgar";
    }

    @Override
    protected float baseHealth() {
        return 300f;
    }

    @Override
    protected double wakeRange() {
        return 12.0;
    }

    @Override
    protected SpellMarkEntity.Hue hue() {
        return SpellMarkEntity.Hue.SPIRIT;
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        level.playSound(null, getX(), getY(), getZ(), ModSounds.HRODGAR_ROAR.get(), SoundSource.HOSTILE, 4.0f, 0.8f);
        Vfx.ring(level, ModParticles.SPIRIT.get(), position().add(0, 0.2, 0), 4, 50, 0.1);
        cooldown = 30;
        startMove(RAISE);
    }

    private List<SpectralHousecarlEntity> livingGuard(ServerLevel level) {
        List<SpectralHousecarlEntity> out = new ArrayList<>();
        guard.removeIf(id -> {
            Entity e = level.getEntity(id);
            if (e instanceof SpectralHousecarlEntity h && h.isAlive()) {
                out.add(h);
                return false;
            }
            return true;
        });
        return out;
    }

    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        List<SpectralHousecarlEntity> alive = livingGuard(level);
        if (alive.size() != tethers()) {
            if (alive.size() < tethers()) level.playSound(null, getX(), getY(), getZ(), ModSounds.TETHER_SNAP.get(), SoundSource.HOSTILE, 2.0f, 1.0f);
            entityData.set(TETHERS, alive.size());
        }
        if (tickCount % 4 == 0) {
            for (SpectralHousecarlEntity h : alive) Vfx.line(level, ModParticles.SPIRIT.get(), h.position().add(0, 1.2, 0), position().add(0, 2.6, 0), 0.7);
        }
        if (tickCount % 10 == 0 && move() != DEVOUR) {
            // the oath-tethers, drawn as living beams from each housecarl to their king
            for (SpectralHousecarlEntity h : alive) {
                SpellMarkEntity.beam(level, h.position().add(0, 1.3, 0), position().add(0, 2.8, 0), 0.22f, SpellMarkEntity.Hue.SPIRIT, 12);
            }
        }
        if (target == null) {
            getNavigation().stop();
            return;
        }
        getLookControl().setLookAt(target, 20f, 20f);
        if (!devoured && getHealth() < getMaxHealth() * 0.33f && move() == IDLE) {
            devoured = true;
            startMove(DEVOUR);
        }
        int t = moveTicks();
        switch (move()) {
            case IDLE -> {
                double d = distanceToSqr(target);
                if (d > 4 * 4) getNavigation().moveTo(target, 1.0);
                else getNavigation().stop();
                if (--cooldown <= 0) {
                    if (alive.isEmpty() && raises < 4 && random.nextInt(3) == 0 && !devoured) startMove(RAISE);
                    else if (d < 5 * 5 && random.nextBoolean()) startMove(SWEEP);
                    else startMove(SLAM);
                    getNavigation().stop();
                }
            }
            case SWEEP -> {
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.HRODGAR_ROAR.get(), SoundSource.HOSTILE, 1.5f, 1.3f);
                if (t == 14) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.FLAIL_SLAM.get(), SoundSource.HOSTILE, 2.0f, 1.2f);
                    Vec3 fwd = Vec3.directionFromRotation(0, getYRot());
                    for (int i = -3; i <= 3; i++) {
                        Vec3 dir = fwd.yRot(i * 0.35f);
                        Vfx.burst(level, ParticleTypes.SWEEP_ATTACK, position().add(dir.scale(3.5)).add(0, 1.4, 0), 1, 0, 0);
                    }
                    for (Player p : challengers(level, 5.5)) {
                        Vec3 to = p.position().subtract(position()).multiply(1, 0, 1).normalize();
                        if (to.dot(fwd) > -0.1 && p.distanceTo(this) < 5.5) {
                            p.hurtServer(level, damageSources().mobAttack(this), 14f);
                            p.setDeltaMovement(to.scale(1.2).add(0, 0.4, 0));
                            p.hurtMarked = true;
                        }
                    }
                }
                if (t > 26) endMove(24 + random.nextInt(16));
            }
            case SLAM -> {
                if (t == 1) {
                    setDeltaMovement(0, 0.7, 0);
                    slamHit.clear();
                }
                if (t == 12) {
                    slamCenter = position();
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.FLAIL_SLAM.get(), SoundSource.HOSTILE, 3.0f, 0.6f);
                    // the shockwave itself: it grows at the same pace as the damage ring, so jump when it reaches you
                    SpellMarkEntity.ring(level, slamCenter, 15.4f, SpellMarkEntity.Hue.SPIRIT, 18);
                    SpellMarkEntity.sigil(level, slamCenter, 3f, SpellMarkEntity.Hue.SPIRIT, 30);
                    Vfx.burst(level, ParticleTypes.EXPLOSION_EMITTER, position(), 1, 0, 0);
                }
                if (t >= 12 && t < 30) {
                    double r = (t - 12) * 0.8 + 1;
                    Vfx.ring(level, ModParticles.SPIRIT.get(), slamCenter.add(0, 0.25, 0), r, (int) (r * 8), 0.02);
                    Vfx.ring(level, ParticleTypes.CLOUD, slamCenter.add(0, 0.1, 0), r, (int) (r * 3), 0.01);
                    for (Player p : challengers(level, 16)) {
                        double pd = p.position().multiply(1, 0, 1).distanceTo(slamCenter.multiply(1, 0, 1));
                        if (Math.abs(pd - r) < 0.9 && p.onGround() && Math.abs(p.getY() - slamCenter.y) < 1.5 && slamHit.add(p.getUUID())) {
                            p.hurtServer(level, damageSources().mobAttack(this), 10f);
                            p.setDeltaMovement(p.getDeltaMovement().add(0, 0.8, 0));
                            p.hurtMarked = true;
                        }
                    }
                }
                if (t > 36) endMove(30 + random.nextInt(20));
            }
            case RAISE -> {
                if (t == 1) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.HOUSECARL_RISE.get(), SoundSource.HOSTILE, 3.0f, 0.8f);
                    SpellMarkEntity.sigil(level, position(), 5f, SpellMarkEntity.Hue.SPIRIT, 36);
                }
                if (t < 24) Vfx.spiralIn(level, ModParticles.SPIRIT.get(), position().add(0, 2, 0), 6, 6, t);
                if (t == 24) {
                    raises++;
                    for (int i = 0; i < 3; i++) {
                        SpectralHousecarlEntity h = ModEntities.SPECTRAL_HOUSECARL.get().create(level, EntitySpawnReason.MOB_SUMMONED);
                        if (h == null) continue;
                        double a = i * Math.PI * 2 / 3 + random.nextDouble();
                        h.snapTo(getX() + Math.cos(a) * 5, getY(), getZ() + Math.sin(a) * 5, random.nextFloat() * 360, 0);
                        h.setTarget(target);
                        level.addFreshEntity(h);
                        guard.add(h.getUUID());
                        Vfx.column(level, ModParticles.SPIRIT.get(), h.position(), 3, 30);
                        SpellMarkEntity.pillar(level, h.position(), 0.8f, SpellMarkEntity.Hue.SPIRIT, 20);
                        SpellMarkEntity.sigil(level, h.position(), 1.4f, SpellMarkEntity.Hue.SPIRIT, 40);
                    }
                }
                if (t > 34) endMove(30);
            }
            case DEVOUR -> {
                getNavigation().stop();
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.HRODGAR_ROAR.get(), SoundSource.HOSTILE, 4.0f, 0.5f);
                for (SpectralHousecarlEntity h : alive) {
                    Vec3 pull = position().subtract(h.position()).normalize().scale(0.35);
                    h.setDeltaMovement(pull.x, 0.05, pull.z);
                    h.hurtMarked = true;
                    Vfx.line(level, ModParticles.SPIRIT.get(), h.position().add(0, 1, 0), position().add(0, 2.4, 0), 0.4);
                    if (t % 4 == 1) SpellMarkEntity.beam(level, h.position().add(0, 1, 0), position().add(0, 2.4, 0), 0.5f, SpellMarkEntity.Hue.SPIRIT, 5);
                }
                if (t == 40) {
                    int eaten = alive.size();
                    for (SpectralHousecarlEntity h : alive) {
                        Vfx.burst(level, ModParticles.SPIRIT.get(), h.position().add(0, 1, 0), 30, 0.4, 0.2);
                        h.discard();
                    }
                    heal(getMaxHealth() * 0.08f * eaten);
                    if (eaten == 0) {
                        var speed = getAttribute(Attributes.MOVEMENT_SPEED);
                        if (speed != null) speed.setBaseValue(0.3);
                    }
                    Vfx.sphere(level, ModParticles.SPIRIT.get(), position().add(0, 2, 0), 3, 100);
                    SpellMarkEntity.ring(level, position(), 9f, SpellMarkEntity.Hue.SPIRIT, 16);
                    SpellMarkEntity.halo(level, position().add(0, 0.2, 0), 2.6f, SpellMarkEntity.Hue.SPIRIT, 40);
                }
                if (t > 50) endMove(20);
            }
            default -> endMove(20);
        }
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (tethers() > 0 && !isSleeping()) {
            amount *= 0.2f;
            if (source.getEntity() instanceof Player p) p.sendOverlayMessage(net.minecraft.network.chat.Component.translatable("message.oathbound.hrodgar.tethered")
                .withStyle(net.minecraft.ChatFormatting.AQUA));
            Vfx.burst(level, ModParticles.SPIRIT.get(), position().add(0, 2, 0), 6, 0.6, 0.05);
        }
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void die(DamageSource source) {
        if (level() instanceof ServerLevel level) {
            for (SpectralHousecarlEntity h : livingGuard(level)) h.discard();
        }
        super.die(source);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : ModSounds.HRODGAR_ROAR.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 360;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return net.minecraft.sounds.SoundEvents.SKELETON_HURT;
    }

    @Override
    public float getVoicePitch() {
        return 0.5f;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HRODGAR_ROAR.get();
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && !isSleeping() && random.nextInt(3) == 0) {
            level().addParticle(ModParticles.SPIRIT.get(), getRandomX(1.2), getY() + random.nextDouble() * 3.5, getRandomZ(1.2), 0, 0.02, 0);
        }
    }
}
