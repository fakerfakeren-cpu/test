package com.oathbound.entity.boss;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.entity.mob.FaunaEntity;
import com.oathbound.entity.projectile.GloamBoltEntity;
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
import java.util.List;
import java.util.UUID;

/**
 * The Bog Mother: the first of the mire hags, grown vast and patient in her stilt-house. She keeps her
 * distance behind two green lanterns and fights with the swamp itself.
 * <ul>
 *   <li><b>Hex Volley</b>: three bursts of green witch-fire, one aimed at every challenger.</li>
 *   <li><b>Mire Pools</b>: marked ground turns to sucking bog for five seconds; it poisons and slows.</li>
 *   <li><b>Lantern Step</b>: when a blade gets close she snuffs her lanterns and is somewhere else, and the
 *       marsh-gas she leaves behind blinds.</li>
 *   <li><b>Brood</b> (at half and a quarter health): calls her bone-children up out of the mud. While they live,
 *       her lanterns shield her.</li>
 * </ul>
 */
public class BogMotherEntity extends KeeperEntity implements FaunaEntity {
    public static final int HEX = 1, POOLS = 2, STEP = 3, BROOD = 4;
    private static final EntityDataAccessor<Boolean> CASTING = SynchedEntityData.defineId(BogMotherEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> VEILED = SynchedEntityData.defineId(BogMotherEntity.class, EntityDataSerializers.BOOLEAN);
    private record Pool(Vec3 at, int until) {}
    private final List<Pool> pools = new ArrayList<>();
    private final List<UUID> brood = new ArrayList<>();
    private int broods;
    private int stepCooldown;

    public BogMotherEntity(EntityType<? extends BogMotherEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.GREEN);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 180.0)
            .add(Attributes.ARMOR, 4.0)
            .add(Attributes.ATTACK_DAMAGE, 8.0)
            .add(Attributes.MOVEMENT_SPEED, 0.26)
            .add(Attributes.FOLLOW_RANGE, 40.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 0.6);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CASTING, false);
        builder.define(VEILED, false);
    }

    @Override
    public boolean fauna$action() {
        return entityData.get(CASTING);
    }

    @Override
    public boolean fauna$ghost() {
        return entityData.get(VEILED);
    }

    private void casting(boolean on) {
        if (entityData.get(CASTING) != on) entityData.set(CASTING, on);
    }

    @Override
    protected String questId() {
        return "bog_mother";
    }

    @Override
    protected float baseHealth() {
        return 180f;
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
        return SpellMarkEntity.Hue.MIRE;
    }

    @Override
    protected float damageCap() {
        return 24f;
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CACKLE.get(), SoundSource.HOSTILE, 4.0f, 0.6f);
        Vfx.ring(level, ModParticles.SPORE.get(), position().add(0, 0.3, 0), 4, 60, 0.05);
        cooldown = 20;
    }

    private List<Monster> livingBrood(ServerLevel level) {
        List<Monster> out = new ArrayList<>();
        brood.removeIf(id -> {
            Entity e = level.getEntity(id);
            if (e instanceof Monster m && m.isAlive()) {
                out.add(m);
                return false;
            }
            return true;
        });
        return out;
    }

    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        tickPools(level);
        List<Monster> children = livingBrood(level);
        if (tickCount % 8 == 0) {
            for (Monster m : children) Vfx.line(level, ModParticles.SPORE.get(), m.position().add(0, 0.6, 0), position().add(0, 2.2, 0), 0.8);
        }
        if (stepCooldown > 0) stepCooldown--;
        if (target == null) {
            getNavigation().stop();
            casting(false);
            return;
        }
        getLookControl().setLookAt(target, 20f, 20f);
        if (broods < 2 && move() == IDLE && getHealth() < getMaxHealth() * (broods == 0 ? 0.5f : 0.25f)) {
            broods++;
            startMove(BROOD);
        }
        // a blade too close: she steps away at once, whatever she was doing
        if (stepCooldown <= 0 && move() != STEP && move() != BROOD && distanceToSqr(target) < 3.2 * 3.2) {
            startMove(STEP);
        }
        int t = moveTicks();
        switch (move()) {
            case IDLE -> {
                casting(false);
                double d = distanceToSqr(target);
                // she keeps to the middle distance
                if (d > 14 * 14) getNavigation().moveTo(target, 1.0);
                else if (d < 7 * 7) {
                    Vec3 away = position().subtract(target.position()).normalize().scale(5).add(position());
                    getNavigation().moveTo(away.x, away.y, away.z, 1.1);
                } else getNavigation().stop();
                if (--cooldown <= 0) {
                    getNavigation().stop();
                    startMove(random.nextInt(5) < 3 ? HEX : POOLS);
                }
            }
            case HEX -> {
                casting(true);
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CURSE.get(), SoundSource.HOSTILE, 2.5f, 0.7f);
                if (t < 10) Vfx.spiralIn(level, ModParticles.SPORE.get(), position().add(0, 2.4, 0), 2.5, 4, t);
                if (t == 10 || t == 18 || t == 26) {
                    SpellMarkEntity.wallSigil(level, position().add(0, 2.4, 0).add(Vec3.directionFromRotation(0, getYRot()).scale(1.2)), 1.0f,
                        SpellMarkEntity.Hue.MIRE, 8, getYRot());
                    for (Player p : challengers(level, 28)) {
                        if (hasLineOfSight(p)) GloamBoltEntity.shoot(level, this, position().add(0, 2.4, 0), p, 7f);
                    }
                }
                if (t > 32) endMove(26 + random.nextInt(18));
            }
            case POOLS -> {
                casting(true);
                if (t == 1) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CACKLE.get(), SoundSource.HOSTILE, 2.5f, 0.8f);
                    for (Player p : challengers(level, 28)) {
                        Vec3 at = p.position();
                        pools.add(new Pool(at, tickCount + 20 + 100));
                        SpellMarkEntity.sigil(level, at.add(0, 0.05, 0), 2.6f, SpellMarkEntity.Hue.MIRE, 20);
                    }
                }
                if (t > 22) endMove(30 + random.nextInt(20));
            }
            case STEP -> {
                if (t == 1) {
                    entityData.set(VEILED, true);
                    getNavigation().stop();
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CACKLE.get(), SoundSource.HOSTILE, 2.0f, 1.3f);
                    Vec3 from = position();
                    Vfx.burst(level, ParticleTypes.LARGE_SMOKE, from.add(0, 1.2, 0), 50, 0.8, 0.03);
                    Vfx.burst(level, ModParticles.SPORE.get(), from.add(0, 1.2, 0), 60, 1.2, 0.05);
                    for (Player p : challengers(level, 4)) {
                        p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50, 0));
                        p.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0));
                    }
                    blink(level, target);
                    SpellMarkEntity.sigil(level, position().add(0, 0.05, 0), 1.6f, SpellMarkEntity.Hue.MIRE, 20);
                }
                if (t == 12) entityData.set(VEILED, false);
                if (t > 14) {
                    stepCooldown = 100;
                    endMove(8);
                    startMove(HEX);
                }
            }
            case BROOD -> {
                casting(true);
                getNavigation().stop();
                if (t == 1) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.HAG_CURSE.get(), SoundSource.HOSTILE, 3.5f, 0.5f);
                    SpellMarkEntity.sigil(level, position().add(0, 0.05, 0), 5f, SpellMarkEntity.Hue.MIRE, 40);
                }
                if (t < 28 && t % 2 == 0) Vfx.spiralIn(level, ModParticles.SPORE.get(), position().add(0, 1, 0), 6, 6, t);
                if (t == 28) {
                    int n = 3 + broods;
                    for (int i = 0; i < n; i++) {
                        Monster m = ModEntities.GRAVE_CRAWLER.get().create(level, EntitySpawnReason.MOB_SUMMONED);
                        if (m == null) continue;
                        double a = i * Math.PI * 2 / n + random.nextDouble() * 0.5;
                        m.snapTo(getX() + Math.cos(a) * 4, getY(), getZ() + Math.sin(a) * 4, random.nextFloat() * 360, 0);
                        m.setTarget(target);
                        level.addFreshEntity(m);
                        brood.add(m.getUUID());
                        Vfx.burst(level, ParticleTypes.MYCELIUM, m.position(), 30, 0.5, 0.1);
                        SpellMarkEntity.pillar(level, m.position(), 0.6f, SpellMarkEntity.Hue.MIRE, 16);
                    }
                }
                if (t > 40) endMove(30);
            }
            default -> endMove(20);
        }
    }

    /** Somewhere behind the target, on solid ground, 8 to 12 blocks from where she stood. */
    private void blink(ServerLevel level, LivingEntity target) {
        for (int attempt = 0; attempt < 16; attempt++) {
            double a = random.nextDouble() * Math.PI * 2;
            double r = 8 + random.nextDouble() * 4;
            BlockPos base = BlockPos.containing(target.getX() + Math.cos(a) * r, getY() + 4, target.getZ() + Math.sin(a) * r);
            for (int dy = 0; dy < 10; dy++) {
                BlockPos p = base.below(dy);
                if (level.getBlockState(p.below()).isSolid() && level.isEmptyBlock(p) && level.isEmptyBlock(p.above())) {
                    teleportTo(p.getX() + 0.5, p.getY(), p.getZ() + 0.5);
                    Vfx.burst(level, ModParticles.SPORE.get(), position().add(0, 1.2, 0), 50, 0.6, 0.05);
                    return;
                }
            }
        }
    }

    private void tickPools(ServerLevel level) {
        pools.removeIf(p -> tickCount > p.until());
        for (Pool p : pools) {
            int left = p.until() - tickCount;
            if (left > 100) continue;   // still only marked
            if (left == 100) {
                level.playSound(null, p.at().x, p.at().y, p.at().z, net.minecraft.sounds.SoundEvents.MUD_BREAK, SoundSource.HOSTILE, 2.0f, 0.5f);
                SpellMarkEntity.ring(level, p.at().add(0, 0.05, 0), 2.6f, SpellMarkEntity.Hue.MIRE, 100);
            }
            if (tickCount % 3 == 0) {
                Vfx.ring(level, ModParticles.SPORE.get(), p.at().add(0, 0.15, 0), 1.5 + random.nextDouble(), 5, 0.01);
                Vfx.burst(level, ParticleTypes.BUBBLE_POP, p.at().add(0, 0.2, 0), 3, 1.2, 0.02);
            }
            if (tickCount % 10 == 0) {
                for (Player pl : challengers(level, 40)) {
                    if (pl.position().distanceToSqr(p.at()) < 2.6 * 2.6 && Math.abs(pl.getY() - p.at().y) < 2) {
                        pl.hurtServer(level, damageSources().magic(), 2f);
                        pl.addEffect(new MobEffectInstance(MobEffects.POISON, 40, 1));
                        pl.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 20, 2));
                    }
                }
            }
        }
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (entityData.get(VEILED)) return false;
        if (!brood.isEmpty() && !isSleeping() && !livingBrood(level).isEmpty()) {
            amount *= 0.35f;
            Vfx.burst(level, ModParticles.SPORE.get(), position().add(0, 1.6, 0), 8, 0.5, 0.04);
            if (source.getEntity() instanceof Player p) p.sendOverlayMessage(net.minecraft.network.chat.Component.translatable("message.oathbound.bog_mother.brood")
                .withStyle(net.minecraft.ChatFormatting.GREEN));
        }
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void die(DamageSource source) {
        if (level() instanceof ServerLevel level) {
            for (Monster m : livingBrood(level)) m.kill(level);
        }
        super.die(source);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : ModSounds.HAG_CACKLE.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 240;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.HAG_CURSE.get();
    }

    @Override
    public float getVoicePitch() {
        return 0.7f;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.HAG_CURSE.get();
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && !entityData.get(VEILED)) {
            // her two lanterns, held out to either side
            float yaw = yBodyRot * net.minecraft.util.Mth.DEG_TO_RAD;
            for (int side = -1; side <= 1; side += 2) {
                double lx = getX() + Math.cos(yaw) * 1.1 * side, lz = getZ() + Math.sin(yaw) * 1.1 * side;
                if (random.nextInt(3) == 0) level().addParticle(ModParticles.SPORE.get(), lx, getY() + 1.6, lz, 0, 0.02, 0);
            }
            if (random.nextInt(4) == 0) level().addParticle(ParticleTypes.FALLING_SPORE_BLOSSOM, getRandomX(1.0), getY() + 2.5, getRandomZ(1.0), 0, 0, 0);
        }
    }
}
