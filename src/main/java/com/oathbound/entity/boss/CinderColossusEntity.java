package com.oathbound.entity.boss;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.entity.mob.FaunaEntity;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * The Cinder Colossus: a war-engine of the old sun-cult, a furnace given legs, still stoking itself in its
 * buried sanctum. Water is its enemy; so is standing still in front of it.
 * <ul>
 *   <li><b>Ember Cleave</b>: raises its blade and brings it down in a straight line that keeps burning.</li>
 *   <li><b>Eruption</b>: marks the ground under everyone, then the ground becomes a column of fire.</li>
 *   <li><b>Furnace Heart</b>: opens its chest and vents: deadly up close, but the open core takes double harm.</li>
 *   <li><b>Molten</b> (below a third of its health): it runs hot, fights faster and every step scorches.</li>
 * </ul>
 * Rain or water makes it hiss and crack: it takes a third more harm while wet.
 */
public class CinderColossusEntity extends KeeperEntity implements FaunaEntity {
    public static final int CLEAVE = 1, ERUPT = 2, FURNACE = 3;
    private static final EntityDataAccessor<Boolean> RAISED = SynchedEntityData.defineId(CinderColossusEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> MOLTEN = SynchedEntityData.defineId(CinderColossusEntity.class, EntityDataSerializers.BOOLEAN);
    private record Burn(Vec3 a, Vec3 b, int until) {}
    private final List<Burn> burns = new ArrayList<>();
    private final List<Vec3> vents = new ArrayList<>();
    private Vec3 cleaveDir = Vec3.ZERO;

    public CinderColossusEntity(EntityType<? extends CinderColossusEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.RED);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 260.0)
            .add(Attributes.ARMOR, 14.0)
            .add(Attributes.ARMOR_TOUGHNESS, 4.0)
            .add(Attributes.ATTACK_DAMAGE, 13.0)
            .add(Attributes.MOVEMENT_SPEED, 0.22)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
            .add(Attributes.STEP_HEIGHT, 1.5);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(RAISED, false);
        builder.define(MOLTEN, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(RAISED);
    }

    /** Variant 1 once it has gone molten: the renderer brightens its core. */
    @Override
    public int fauna$variant() {
        return entityData.get(MOLTEN) ? 1 : 0;
    }

    private boolean molten() {
        return entityData.get(MOLTEN);
    }

    private void raised(boolean on) {
        if (entityData.get(RAISED) != on) entityData.set(RAISED, on);
    }

    @Override
    protected String questId() {
        return "cinder_colossus";
    }

    @Override
    protected float baseHealth() {
        return 260f;
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
        return 10.0;
    }

    @Override
    protected SpellMarkEntity.Hue hue() {
        return SpellMarkEntity.Hue.EMBER;
    }

    @Override
    protected float damageCap() {
        return 28f;
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        level.playSound(null, getX(), getY(), getZ(), ModSounds.COLOSSUS_ROAR.get(), SoundSource.HOSTILE, 4.0f, 0.8f);
        Vfx.ring(level, ParticleTypes.FLAME, position().add(0, 0.3, 0), 5, 80, 0.06);
        Vfx.burst(level, ParticleTypes.LAVA, position().add(0, 2.5, 0), 30, 1.0, 0.3);
        cooldown = 30;
    }

    private boolean wet() {
        return isInWaterOrRain();
    }

    private int pace(int ticks) {
        return molten() ? (int) (ticks * 0.65f) : ticks;
    }

    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        tickBurns(level);
        if (!molten() && getHealth() < getMaxHealth() / 3f) {
            entityData.set(MOLTEN, true);
            var speed = getAttribute(Attributes.MOVEMENT_SPEED);
            if (speed != null) speed.setBaseValue(0.29);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.COLOSSUS_ROAR.get(), SoundSource.HOSTILE, 5.0f, 0.6f);
            SpellMarkEntity.ring(level, position(), 12f, SpellMarkEntity.Hue.EMBER, 20);
            SpellMarkEntity.pillar(level, position(), 1.8f, SpellMarkEntity.Hue.EMBER, 30);
            Vfx.burst(level, ParticleTypes.LAVA, position().add(0, 2, 0), 60, 1.5, 0.4);
            for (Player p : challengers(level, 30)) {
                p.sendOverlayMessage(Component.translatable("message.oathbound.cinder_colossus.molten").withStyle(net.minecraft.ChatFormatting.GOLD));
            }
        }
        if (wet() && tickCount % 5 == 0) {
            Vfx.burst(level, ParticleTypes.CLOUD, position().add(0, 2.5, 0), 4, 1.0, 0.05);
            if (tickCount % 40 == 0) level.playSound(null, getX(), getY(), getZ(), SoundEvents.FIRE_EXTINGUISH, SoundSource.HOSTILE, 1.2f, 0.6f);
        }
        if (molten() && tickCount % 10 == 0 && onGround() && getDeltaMovement().horizontalDistanceSqr() > 0.001) {
            // scorched footprints
            burns.add(new Burn(position(), position(), tickCount + 60));
        }
        if (target == null) {
            getNavigation().stop();
            raised(false);
            return;
        }
        if (move() != CLEAVE || moveTicks() < 12) getLookControl().setLookAt(target, 20f, 20f);
        int t = moveTicks();
        switch (move()) {
            case IDLE -> {
                raised(false);
                double d = distanceToSqr(target);
                if (d > 3.5 * 3.5) getNavigation().moveTo(target, 1.0);
                else {
                    getNavigation().stop();
                    if (tickCount % 24 == 0) {
                        swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                        if (doHurtTarget(level, target)) target.igniteForSeconds(4);
                    }
                }
                if (--cooldown <= 0) {
                    getNavigation().stop();
                    int roll = random.nextInt(10);
                    if (d < 6 * 6 && roll < 3) startMove(FURNACE);
                    else if (d < 10 * 10 && roll < 7) startMove(CLEAVE);
                    else startMove(ERUPT);
                }
            }
            case CLEAVE -> cleave(level, target, t);
            case ERUPT -> erupt(level, t);
            case FURNACE -> furnace(level, t);
            default -> endMove(20);
        }
    }

    private void cleave(ServerLevel level, LivingEntity target, int t) {
        int strike = pace(20);
        if (t == 1) {
            raised(true);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.COLOSSUS_ROAR.get(), SoundSource.HOSTILE, 2.0f, 1.2f);
        }
        if (t < strike - 6) {
            cleaveDir = target.position().subtract(position()).multiply(1, 0, 1).normalize();
            Vfx.burst(level, ParticleTypes.FLAME, position().add(0, 4.2, 0).add(cleaveDir.scale(0.8)), 4, 0.3, 0.05);
        }
        if (t == strike - 6) {
            // the line it will cut, shown just before it lands
            SpellMarkEntity.beam(level, position().add(0, 0.15, 0), position().add(cleaveDir.scale(11)).add(0, 0.15, 0), 1.4f, SpellMarkEntity.Hue.EMBER, 8);
        }
        if (t == strike) {
            raised(false);
            swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            Vec3 a = position(), b = position().add(cleaveDir.scale(11));
            level.playSound(null, getX(), getY(), getZ(), ModSounds.FLAIL_SLAM.get(), SoundSource.HOSTILE, 3.0f, 0.5f);
            level.playSound(null, getX(), getY(), getZ(), SoundEvents.BLAZE_SHOOT, SoundSource.HOSTILE, 2.0f, 0.6f);
            for (int i = 1; i <= 11; i++) {
                Vec3 p = a.add(cleaveDir.scale(i));
                Vfx.burst(level, ParticleTypes.FLAME, p.add(0, 0.3, 0), 12, 0.5, 0.12);
                Vfx.burst(level, ParticleTypes.LAVA, p.add(0, 0.3, 0), 2, 0.3, 0.2);
                Vfx.burst(level, ModParticles.EMBER.get(), p.add(0, 0.6, 0), 6, 0.4, 0.1);
            }
            for (Player p : challengers(level, 13)) {
                if (distToSegment(p.position(), a, b) < 1.4 && Math.abs(p.getY() - getY()) < 2.5) {
                    p.hurtServer(level, damageSources().mobAttack(this), 16f);
                    p.igniteForSeconds(5);
                    p.setDeltaMovement(p.getDeltaMovement().add(0, 0.5, 0));
                    p.hurtMarked = true;
                }
            }
            burns.add(new Burn(a, b, tickCount + 80));
        }
        if (t > strike + 14) endMove(pace(30) + random.nextInt(16));
    }

    private void erupt(ServerLevel level, int t) {
        int blast = pace(28);
        raised(t < blast);
        if (t == 1) {
            vents.clear();
            level.playSound(null, getX(), getY(), getZ(), ModSounds.COLOSSUS_ROAR.get(), SoundSource.HOSTILE, 3.0f, 0.7f);
            for (Player p : challengers(level, 26)) vents.add(p.position());
            for (int i = 0; i < 3 + (molten() ? 3 : 0); i++) {
                double a = random.nextDouble() * Math.PI * 2, r = 4 + random.nextDouble() * 8;
                vents.add(position().add(Math.cos(a) * r, 0, Math.sin(a) * r));
            }
            for (Vec3 v : vents) SpellMarkEntity.sigil(level, v.add(0, 0.05, 0), 1.9f, SpellMarkEntity.Hue.EMBER, blast);
        }
        if (t < blast && t % 3 == 0) {
            for (Vec3 v : vents) {
                Vfx.burst(level, ParticleTypes.SMOKE, v.add(0, 0.2, 0), 3, 0.6, 0.02);
                Vfx.burst(level, ModParticles.EMBER.get(), v.add(0, 0.2, 0), 2, 0.8, 0.05);
            }
        }
        if (t == blast) {
            for (Vec3 v : vents) {
                level.playSound(null, v.x, v.y, v.z, SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1.5f, 1.2f);
                SpellMarkEntity.pillar(level, v, 1.2f, SpellMarkEntity.Hue.EMBER, 18);
                Vfx.column(level, ParticleTypes.FLAME, v, 6, 50);
                Vfx.burst(level, ParticleTypes.LAVA, v.add(0, 0.5, 0), 8, 0.4, 0.4);
                for (Player p : challengers(level, 30)) {
                    if (p.position().multiply(1, 0, 1).distanceTo(v.multiply(1, 0, 1)) < 2.0 && Math.abs(p.getY() - v.y) < 4) {
                        p.hurtServer(level, damageSources().inFire(), 10f);
                        p.igniteForSeconds(6);
                        p.setDeltaMovement(p.getDeltaMovement().x, 1.0, p.getDeltaMovement().z);
                        p.hurtMarked = true;
                    }
                }
            }
        }
        if (t > blast + 12) endMove(pace(34) + random.nextInt(16));
    }

    private void furnace(ServerLevel level, int t) {
        getNavigation().stop();
        raised(true);
        if (t == 1) {
            level.playSound(null, getX(), getY(), getZ(), SoundEvents.BLAZE_AMBIENT, SoundSource.HOSTILE, 3.0f, 0.4f);
            SpellMarkEntity.halo(level, position().add(0, 2.4, 0), 1.2f, SpellMarkEntity.Hue.EMBER, 70);
            SpellMarkEntity.sigil(level, position().add(0, 0.05, 0), 5f, SpellMarkEntity.Hue.EMBER, 70);
        }
        if (t > 10 && t < 70) {
            double r = 1.5 + (t % 12) * 0.35;
            Vfx.ring(level, ParticleTypes.FLAME, position().add(0, 0.4, 0), r, (int) (r * 6), 0.04);
            if (t % 2 == 0) Vfx.burst(level, ModParticles.EMBER.get(), position().add(0, 2.4, 0), 6, 0.4, 0.15);
            if (t % 10 == 0) {
                level.playSound(null, getX(), getY(), getZ(), SoundEvents.FIRE_AMBIENT, SoundSource.HOSTILE, 2.0f, 0.5f);
                for (Player p : challengers(level, 5.5)) {
                    p.hurtServer(level, damageSources().inFire(), 4f);
                    p.igniteForSeconds(3);
                }
            }
        }
        if (t > 76) {
            raised(false);
            endMove(pace(30) + random.nextInt(16));
        }
    }

    private void tickBurns(ServerLevel level) {
        burns.removeIf(b -> tickCount > b.until());
        if (tickCount % 4 != 0) return;
        for (Burn b : burns) {
            double len = b.a().distanceTo(b.b());
            for (double d = 0; d <= len; d += 1.0) {
                Vec3 p = len == 0 ? b.a() : b.a().add(b.b().subtract(b.a()).scale(d / len));
                if (random.nextInt(2) == 0) Vfx.burst(level, ParticleTypes.SMALL_FLAME, p.add(0, 0.1, 0), 1, 0.4, 0.01);
            }
            if (tickCount % 10 == 0) {
                for (Player p : challengers(level, 16)) {
                    if (distToSegment(p.position(), b.a(), b.b()) < 1.0 && p.onGround()) {
                        p.hurtServer(level, damageSources().inFire(), 2f);
                        p.igniteForSeconds(2);
                    }
                }
            }
        }
    }

    private static double distToSegment(Vec3 p, Vec3 a, Vec3 b) {
        Vec3 ab = b.subtract(a).multiply(1, 0, 1), ap = p.subtract(a).multiply(1, 0, 1);
        double len = ab.lengthSqr();
        double k = len == 0 ? 0 : Math.max(0, Math.min(1, ap.dot(ab) / len));
        return ap.subtract(ab.scale(k)).length();
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (source.is(net.minecraft.tags.DamageTypeTags.IS_FIRE)) return false;
        if (move() == FURNACE && moveTicks() > 10) {
            amount *= 2f;
            Vfx.burst(level, ParticleTypes.LAVA, position().add(0, 2.4, 0), 4, 0.3, 0.2);
        }
        if (wet()) amount *= 1.33f;
        return super.hurtServer(level, source, amount);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : ModSounds.COLOSSUS_ROAR.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 360;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.IRON_GOLEM_HURT;
    }

    @Override
    public float getVoicePitch() {
        return 0.5f;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.COLOSSUS_ROAR.get();
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide()) {
            if (random.nextInt(isSleeping() ? 5 : 1) == 0) {
                level().addParticle(ModParticles.EMBER.get(), getRandomX(1.2), getY() + 1.5 + random.nextDouble() * 2.5, getRandomZ(1.2), 0, 0.04, 0);
            }
            if (molten() && random.nextInt(2) == 0) {
                level().addParticle(ParticleTypes.LAVA, getRandomX(1.0), getY() + 2 + random.nextDouble() * 2, getRandomZ(1.0), 0, 0, 0);
            }
            if (!isSleeping() && random.nextInt(4) == 0) {
                level().addParticle(ParticleTypes.LARGE_SMOKE, getX(), getY() + 4.6, getZ(), 0, 0.06, 0);
            }
        }
    }
}
