package com.oathbound.entity.boss;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.entity.mob.FaunaEntity;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
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
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * Elderhorn, the Grove King: a stag the size of a cart, crowned with antlers that have grown runes. He is the
 * old woods' own keeper and answers anyone who draws steel in his grove.
 * <ul>
 *   <li><b>Gore Charge</b>: lowers his crown, paws twice and runs straight through; sidestep it.</li>
 *   <li><b>Rootsnare</b>: green sigils open under every challenger and thorned roots burst up a second later.</li>
 *   <li><b>Bellow</b>: a roar that blows everyone in front of him back in a storm of leaves.</li>
 *   <li><b>Verdant Bloom</b> (below half health): kneels and drinks from the grove, healing fast, until struck
 *       hard enough to break the trance.</li>
 * </ul>
 */
public class ElderhornEntity extends KeeperEntity implements FaunaEntity {
    public static final int CHARGE = 1, ROOTS = 2, BELLOW = 3, BLOOM = 4;
    private static final EntityDataAccessor<Boolean> HEAD_DOWN = SynchedEntityData.defineId(ElderhornEntity.class, EntityDataSerializers.BOOLEAN);
    private static final float BLOOM_BREAK = 24f;
    private final List<Vec3> snares = new ArrayList<>();
    private final Set<UUID> chargeHit = new HashSet<>();
    private Vec3 chargeDir = Vec3.ZERO;
    private float bloomDamage;
    private int blooms;

    public ElderhornEntity(EntityType<? extends ElderhornEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.GREEN);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 220.0)
            .add(Attributes.ARMOR, 8.0)
            .add(Attributes.ATTACK_DAMAGE, 10.0)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.9)
            .add(Attributes.STEP_HEIGHT, 1.5);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(HEAD_DOWN, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(HEAD_DOWN) || isSleeping();
    }

    @Override
    protected String questId() {
        return "grove_king";
    }

    @Override
    protected float baseHealth() {
        return 220f;
    }

    @Override
    protected SoundEvent theme() {
        return ModSounds.THEME_WILDS.get();
    }

    @Override
    protected int themeLength() {
        return 700;
    }

    @Override
    protected double wakeRange() {
        return 9.0;
    }

    @Override
    protected SpellMarkEntity.Hue hue() {
        return SpellMarkEntity.Hue.GROVE;
    }

    @Override
    protected float damageCap() {
        return 26f;
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ELDERHORN_BELLOW.get(), SoundSource.HOSTILE, 4.0f, 0.9f);
        Vfx.ring(level, ModParticles.PETAL.get(), position().add(0, 0.3, 0), 5, 70, 0.08);
        cooldown = 30;
    }

    private void headDown(boolean down) {
        if (entityData.get(HEAD_DOWN) != down) entityData.set(HEAD_DOWN, down);
    }

    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        if (tickCount % 3 == 0) {
            // the grove answers him: petals ride the air around his crown
            Vfx.burst(level, ModParticles.PETAL.get(), position().add(0, 3.6, 0), 2, 1.3, 0.02);
        }
        if (target == null) {
            getNavigation().stop();
            headDown(false);
            return;
        }
        if (move() != CHARGE) getLookControl().setLookAt(target, 20f, 20f);
        if (blooms < 2 && move() == IDLE && getHealth() < getMaxHealth() * (blooms == 0 ? 0.5f : 0.25f)) {
            blooms++;
            startMove(BLOOM);
        }
        int t = moveTicks();
        switch (move()) {
            case IDLE -> {
                headDown(false);
                double d = distanceToSqr(target);
                if (d > 3.5 * 3.5) getNavigation().moveTo(target, 1.0);
                else {
                    getNavigation().stop();
                    if (tickCount % 20 == 0) {
                        swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                        doHurtTarget(level, target);
                    }
                }
                if (--cooldown <= 0) {
                    getNavigation().stop();
                    int roll = random.nextInt(10);
                    if (d > 6 * 6 && roll < 5) startMove(CHARGE);
                    else if (d < 7 * 7 && roll < 4) startMove(BELLOW);
                    else if (roll < 8) startMove(ROOTS);
                    else startMove(CHARGE);
                }
            }
            case CHARGE -> charge(level, target, t);
            case ROOTS -> roots(level, t);
            case BELLOW -> bellow(level, t);
            case BLOOM -> bloom(level, t);
            default -> endMove(20);
        }
    }

    private void charge(ServerLevel level, LivingEntity target, int t) {
        headDown(true);
        if (t == 1) {
            chargeHit.clear();
            level.playSound(null, getX(), getY(), getZ(), ModSounds.ELDERHORN_BELLOW.get(), SoundSource.HOSTILE, 2.0f, 1.3f);
        }
        if (t < 24) {
            // pawing the ground: the path he will take glows with falling petals
            getLookControl().setLookAt(target, 30f, 30f);
            chargeDir = target.position().subtract(position()).multiply(1, 0, 1).normalize();
            setYRot((float) (Math.atan2(chargeDir.z, chargeDir.x) * 180 / Math.PI) - 90f);
            yBodyRot = getYRot();
            if (t % 8 == 0) {
                Vfx.burst(level, new BlockParticleOption(ParticleTypes.BLOCK, Blocks.ROOTED_DIRT.defaultBlockState()), position(), 18, 0.5, 0.1);
                level.playSound(null, getX(), getY(), getZ(), net.minecraft.sounds.SoundEvents.RAVAGER_STEP, SoundSource.HOSTILE, 1.4f, 0.7f);
            }
            if (t % 4 == 0) {
                for (int i = 2; i < 18; i += 2) {
                    Vec3 p = position().add(chargeDir.scale(i));
                    Vfx.burst(level, ModParticles.PETAL.get(), p.add(0, 0.2, 0), 1, 0.3, 0.0);
                }
            }
            if (t == 16) SpellMarkEntity.beam(level, position().add(0, 0.15, 0), position().add(chargeDir.scale(18)).add(0, 0.15, 0), 1.6f,
                SpellMarkEntity.Hue.GROVE, 10);
            return;
        }
        if (t < 44) {
            setDeltaMovement(chargeDir.x * 0.95, getDeltaMovement().y, chargeDir.z * 0.95);
            hurtMarked = true;
            Vfx.burst(level, ModParticles.PETAL.get(), position().add(0, 1.5, 0), 4, 1.0, 0.05);
            if (t % 3 == 0) Vfx.burst(level, ParticleTypes.CLOUD, position().add(0, 0.2, 0), 3, 0.6, 0.02);
            for (Player p : challengers(level, 3.2)) {
                if (chargeHit.add(p.getUUID())) {
                    p.hurtServer(level, damageSources().mobAttack(this), 15f);
                    Vec3 fling = p.position().subtract(position()).multiply(1, 0, 1).normalize().add(chargeDir).normalize().scale(1.6);
                    p.setDeltaMovement(fling.x, 0.75, fling.z);
                    p.hurtMarked = true;
                    level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.FLAIL_SLAM.get(), SoundSource.HOSTILE, 1.5f, 1.4f);
                }
            }
            // ran into something solid: he staggers, stunned and open to blows
            if (horizontalCollision && t > 28) {
                level.playSound(null, getX(), getY(), getZ(), ModSounds.FLAIL_SLAM.get(), SoundSource.HOSTILE, 2.5f, 0.6f);
                Vfx.burst(level, ParticleTypes.EXPLOSION, position().add(chargeDir.scale(1.5)).add(0, 1.5, 0), 2, 0.4, 0);
                SpellMarkEntity.ring(level, position(), 5f, SpellMarkEntity.Hue.GROVE, 12);
                endMove(70);
                headDown(false);
            }
            return;
        }
        setDeltaMovement(getDeltaMovement().multiply(0.3, 1, 0.3));
        headDown(false);
        endMove(30 + random.nextInt(20));
    }

    private void roots(ServerLevel level, int t) {
        if (t == 1) {
            snares.clear();
            level.playSound(null, getX(), getY(), getZ(), ModSounds.ELDERHORN_BELLOW.get(), SoundSource.HOSTILE, 2.0f, 0.7f);
            SpellMarkEntity.halo(level, position().add(0, 4.2, 0), 1.6f, SpellMarkEntity.Hue.GROVE, 30);
            for (Player p : challengers(level, 24)) {
                snares.add(p.position());
                // one where they stand, one where they are heading
                Vec3 lead = p.position().add(p.getDeltaMovement().multiply(14, 0, 14));
                if (lead.distanceToSqr(p.position()) > 4) snares.add(lead);
            }
            for (Vec3 s : snares) SpellMarkEntity.sigil(level, s.add(0, 0.05, 0), 1.8f, SpellMarkEntity.Hue.GROVE, 26);
        }
        if (t > 1 && t < 22) {
            for (Vec3 s : snares) Vfx.ring(level, ModParticles.PETAL.get(), s.add(0, 0.1, 0), 1.8 - t * 0.07, 6, 0.0);
        }
        if (t == 22) {
            for (Vec3 s : snares) {
                level.playSound(null, s.x, s.y, s.z, net.minecraft.sounds.SoundEvents.ROOTED_DIRT_BREAK, SoundSource.HOSTILE, 2.0f, 0.6f);
                SpellMarkEntity.pillar(level, s, 1.0f, SpellMarkEntity.Hue.GROVE, 14);
                Vfx.burst(level, new BlockParticleOption(ParticleTypes.BLOCK, Blocks.ROOTED_DIRT.defaultBlockState()), s.add(0, 0.5, 0), 40, 0.6, 0.3);
                Vfx.column(level, ModParticles.PETAL.get(), s, 3, 20);
                for (Player p : challengers(level, 30)) {
                    if (p.position().distanceToSqr(s) < 2.2 * 2.2) {
                        p.hurtServer(level, damageSources().thorns(this), 9f);
                        p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 50, 4));
                        p.setDeltaMovement(0, 0.5, 0);
                        p.hurtMarked = true;
                    }
                }
            }
        }
        if (t > 34) endMove(30 + random.nextInt(20));
    }

    private void bellow(ServerLevel level, int t) {
        headDown(t > 6 && t < 20);
        if (t == 8) {
            level.playSound(null, getX(), getY(), getZ(), ModSounds.ELDERHORN_BELLOW.get(), SoundSource.HOSTILE, 4.0f, 0.6f);
            Vec3 fwd = Vec3.directionFromRotation(0, getYRot());
            for (int i = 1; i <= 9; i++) {
                for (int k = -2; k <= 2; k++) {
                    Vec3 p = position().add(fwd.scale(i)).add(fwd.yRot((float) Math.PI / 2).scale(k * i * 0.25)).add(0, 1.4, 0);
                    Vfx.burst(level, ModParticles.PETAL.get(), p, 2, 0.3, 0.2);
                }
            }
            SpellMarkEntity.wallSigil(level, position().add(fwd.scale(2.5)).add(0, 2.2, 0), 2.2f, SpellMarkEntity.Hue.GROVE, 16, getYRot());
            for (Player p : challengers(level, 10)) {
                Vec3 to = p.position().subtract(position()).multiply(1, 0, 1);
                if (to.normalize().dot(fwd) > 0.35) {
                    p.hurtServer(level, damageSources().mobAttack(this), 6f);
                    Vec3 push = to.normalize().scale(2.1);
                    p.setDeltaMovement(push.x, 0.6, push.z);
                    p.hurtMarked = true;
                    p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 80, 0));
                }
            }
        }
        if (t > 26) endMove(24 + random.nextInt(16));
    }

    private void bloom(ServerLevel level, int t) {
        getNavigation().stop();
        headDown(true);
        if (t == 1) {
            bloomDamage = 0;
            level.playSound(null, getX(), getY(), getZ(), ModSounds.ELDERHORN_BELLOW.get(), SoundSource.HOSTILE, 3.0f, 1.5f);
            SpellMarkEntity.sigil(level, position().add(0, 0.05, 0), 5.5f, SpellMarkEntity.Hue.GROVE, 90);
            SpellMarkEntity.halo(level, position().add(0, 4.4, 0), 2.2f, SpellMarkEntity.Hue.GROVE, 90);
            for (Player p : challengers(level, 30)) {
                p.sendOverlayMessage(Component.translatable("message.oathbound.elderhorn.bloom").withStyle(net.minecraft.ChatFormatting.GREEN));
            }
        }
        if (t % 2 == 0) Vfx.spiralIn(level, ModParticles.PETAL.get(), position().add(0, 1.5, 0), 7, 6, t);
        if (t % 10 == 0) {
            heal(getMaxHealth() * 0.03f);
            Vfx.burst(level, ParticleTypes.HAPPY_VILLAGER, position().add(0, 2.2, 0), 12, 1.2, 0.05);
        }
        if (bloomDamage >= BLOOM_BREAK) {
            // the trance breaks: he rears, stunned
            level.playSound(null, getX(), getY(), getZ(), ModSounds.WARD_DISSOLVE.get(), SoundSource.HOSTILE, 2.5f, 1.2f);
            SpellMarkEntity.ring(level, position(), 8f, SpellMarkEntity.Hue.GROVE, 14);
            Vfx.burst(level, ModParticles.PETAL.get(), position().add(0, 2, 0), 80, 1.6, 0.3);
            headDown(false);
            endMove(60);
            return;
        }
        if (t > 90) {
            headDown(false);
            endMove(30);
        }
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        boolean hurt = super.hurtServer(level, source, amount);
        if (hurt && move() == BLOOM && source.getEntity() instanceof Player) bloomDamage += Math.min(amount, damageCap());
        return hurt;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : ModSounds.ELDERHORN_BELLOW.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 400;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.FAWN_HURT.get();
    }

    @Override
    public float getVoicePitch() {
        return 0.45f;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.ELDERHORN_BELLOW.get();
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(isSleeping() ? 6 : 2) == 0) {
            level().addParticle(ModParticles.PETAL.get(), getRandomX(1.4), getY() + 3 + random.nextDouble() * 1.5, getRandomZ(1.4), 0, -0.01, 0);
        }
    }
}
