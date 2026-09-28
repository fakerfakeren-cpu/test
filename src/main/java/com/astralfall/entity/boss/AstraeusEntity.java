package com.astralfall.entity.boss;

import com.astralfall.Config;
import com.astralfall.entity.SingularityEntity;
import com.astralfall.entity.mob.VoidGazerEntity;
import com.astralfall.entity.mob.VoidStalkerEntity;
import com.astralfall.entity.projectile.CrystalShardEntity;
import com.astralfall.event.Starfall;
import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Astraeus, Devourer of Stars. A floating titan of armour and nebula with a star burning in its chest,
 * a halo of runes and six orbiting crystals. Three phases, seven attacks, one very dramatic death.
 */
public class AstraeusEntity extends Monster {
    public static final int IDLE = 0, METEOR_RAIN = 1, STAR_LANCE = 2, SHARD_BARRAGE = 3, GRAVITY_COLLAPSE = 4,
        SUMMON = 5, SINGULARITY = 6, SLAM = 7, TRANSITION = 8;
    public static final int EMERGE_TIME = 110;
    public static final int MAX_SHARDS = 6;

    private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(AstraeusEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> ATTACK = SynchedEntityData.defineId(AstraeusEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> ATTACK_TICKS = SynchedEntityData.defineId(AstraeusEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> EMERGE = SynchedEntityData.defineId(AstraeusEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> SHARDS = SynchedEntityData.defineId(AstraeusEntity.class, EntityDataSerializers.INT);

    private final ServerBossEvent bossEvent = new ServerBossEvent(UUID.randomUUID(), Component.translatable("entity.astralfall.astraeus"),
        BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.NOTCHED_10);
    private BlockPos home;
    private int attackCooldown = 60;
    private int lastAttack = IDLE;
    private int shardRegen;
    private Vec3 beamDir = Vec3.ZERO;
    private final List<UUID> minions = new ArrayList<>();
    private int noTargetTicks;

    public AstraeusEntity(EntityType<? extends AstraeusEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
        this.xpReward = 0;
        this.bossEvent.setDarkenScreen(true);
        this.setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 600.0)
            .add(Attributes.ARMOR, 12.0)
            .add(Attributes.ARMOR_TOUGHNESS, 6.0)
            .add(Attributes.ATTACK_DAMAGE, 14.0)
            .add(Attributes.FOLLOW_RANGE, 64.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
            .add(Attributes.MOVEMENT_SPEED, 0.25)
            .add(Attributes.FLYING_SPEED, 0.3);
    }

    /** Called by the summoning ritual. */
    public void beginEmerging(BlockPos home) {
        this.home = home;
        entityData.set(EMERGE, EMERGE_TIME);
        double hp = 600.0 * Config.bossHealthMultiplier();
        var attr = getAttribute(Attributes.MAX_HEALTH);
        if (attr != null) attr.setBaseValue(hp);
        setHealth((float) hp);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(PHASE, 1);
        builder.define(ATTACK, IDLE);
        builder.define(ATTACK_TICKS, 0);
        builder.define(EMERGE, 0);
        builder.define(SHARDS, MAX_SHARDS);
    }

    public int getPhase() { return entityData.get(PHASE); }
    public int getAttack() { return entityData.get(ATTACK); }
    public int getAttackTicks() { return entityData.get(ATTACK_TICKS); }
    public int getEmerge() { return entityData.get(EMERGE); }
    public int getShards() { return entityData.get(SHARDS); }

    private void setAttack(int attack) {
        entityData.set(ATTACK, attack);
        entityData.set(ATTACK_TICKS, 0);
    }

    // ------------------------------------------------------------------ core loop
    @Override
    protected void registerGoals() {}

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) clientEffects();
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (home == null) home = blockPosition();
        bossEvent.setProgress(getHealth() / getMaxHealth());

        int emerge = getEmerge();
        if (emerge > 0) {
            tickEmerge(level, emerge);
            return;
        }

        updatePhase(level);
        LivingEntity target = acquireTarget(level);
        move(target);

        if (++shardRegen > (getPhase() >= 2 ? 70 : 110) && getShards() < MAX_SHARDS) {
            shardRegen = 0;
            entityData.set(SHARDS, getShards() + 1);
        }
        if (getPhase() == 3 && tickCount % 45 == 0 && target != null) {
            BlockPos p = target.blockPosition().offset(random.nextInt(15) - 7, 0, random.nextInt(15) - 7);
            Starfall.spawnMeteor(level, p, Starfall.Variant.SMALL, 0.8f);
        }

        int attack = getAttack();
        if (attack == IDLE) {
            if (target != null && --attackCooldown <= 0) chooseAttack(target);
        } else {
            int t = getAttackTicks() + 1;
            entityData.set(ATTACK_TICKS, t);
            tickAttack(level, attack, t, target);
        }
    }

    private void tickEmerge(ServerLevel level, int emerge) {
        setDeltaMovement(0, 0.045, 0);
        Vec3 c = position().add(0, 2, 0);
        FX.spiralIn(level, ModParticles.VOID_MOTE.get(), c, 6.0, 8, tickCount);
        FX.burst(level, ParticleTypes.LARGE_SMOKE, getX(), getY(), getZ(), 4, 1.5, 0.3, 1.5, 0.02);
        if (emerge == EMERGE_TIME - 20) {
            level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_ROAR.get(), SoundSource.HOSTILE, 6.0f, 0.7f);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(96))) {
                Starfall.title(p, Component.translatable("entity.astralfall.astraeus").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD),
                    Component.translatable("title.astralfall.astraeus.sub").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
            }
        }
        if (emerge == 1) {
            FX.sphere(level, ModParticles.STAR_SPARKLE.get(), c, 6, 160);
            FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 2, 1, 0);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_ROAR.get(), SoundSource.HOSTILE, 6.0f, 1.0f);
            attackCooldown = 40;
        }
        entityData.set(EMERGE, emerge - 1);
    }

    private void updatePhase(ServerLevel level) {
        float frac = getHealth() / getMaxHealth();
        int phase = getPhase();
        int want = frac <= 0.2f ? 3 : frac <= 0.5f ? 2 : 1;
        if (want > phase) {
            entityData.set(PHASE, want);
            setAttack(TRANSITION);
            bossEvent.setColor(want == 3 ? BossEvent.BossBarColor.RED : BossEvent.BossBarColor.PINK);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_ROAR.get(), SoundSource.HOSTILE, 6.0f, want == 3 ? 1.2f : 0.9f);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(96))) {
                p.sendSystemMessage(Component.translatable(want == 3 ? "message.astralfall.boss.phase3" : "message.astralfall.boss.phase2").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
            }
        }
    }

    private LivingEntity acquireTarget(ServerLevel level) {
        LivingEntity target = getTarget();
        if (target instanceof Player p && (p.isCreative() || p.isSpectator())) target = null;
        if (target == null || !target.isAlive() || target.distanceToSqr(this) > 64 * 64) {
            Player best = null;
            double bestD = 48 * 48;
            for (Player p : level.players()) {
                if (p.isCreative() || p.isSpectator()) continue;
                double d = p.distanceToSqr(this);
                if (d < bestD) {
                    bestD = d;
                    best = p;
                }
            }
            target = best;
            setTarget(best);
        }
        if (target == null) {
            if (++noTargetTicks > 100 && tickCount % 20 == 0) heal(2.0f);
        } else {
            noTargetTicks = 0;
        }
        return target;
    }

    private void move(LivingEntity target) {
        Vec3 want;
        if (target != null) {
            getLookControl().setLookAt(target, 20f, 20f);
            double orbit = tickCount * 0.012;
            double radius = getAttack() == SLAM ? 3 : 11;
            want = target.position().add(Math.cos(orbit) * radius, 0, Math.sin(orbit) * radius);
            int ground = level().getHeight(Heightmap.Types.MOTION_BLOCKING, (int) Math.floor(want.x), (int) Math.floor(want.z));
            want = new Vec3(want.x, Math.max(ground, target.getY()) + (getAttack() == SLAM ? 1.5 : 4.5), want.z);
            if (home != null && want.distanceToSqr(Vec3.atCenterOf(home)) > 48 * 48) {
                want = Vec3.atCenterOf(home).add(want.subtract(Vec3.atCenterOf(home)).normalize().scale(48));
            }
            double dx = target.getX() - getX(), dz = target.getZ() - getZ();
            float yaw = (float) (Mth.atan2(dz, dx) * (180f / Math.PI)) - 90f;
            setYRot(Mth.approachDegrees(getYRot(), yaw, 8f));
            yBodyRot = getYRot();
            yHeadRot = getYRot();
        } else {
            BlockPos h = home == null ? blockPosition() : home;
            want = Vec3.atCenterOf(h).add(0, 4, 0);
        }
        boolean rooted = getAttack() == STAR_LANCE || getAttack() == GRAVITY_COLLAPSE || getAttack() == TRANSITION;
        Vec3 to = want.subtract(position());
        double speed = rooted ? 0.0 : (getPhase() >= 2 ? 0.42 : 0.32);
        Vec3 v = to.lengthSqr() > 1 ? to.normalize().scale(speed) : to.scale(0.1);
        setDeltaMovement(getDeltaMovement().scale(0.7).add(v.scale(0.3)).add(0, Mth.sin(tickCount * 0.08f) * 0.01, 0));
    }

    private void chooseAttack(LivingEntity target) {
        double d = distanceToSqr(target);
        int phase = getPhase();
        List<Integer> options = new ArrayList<>();
        options.add(METEOR_RAIN);
        options.add(STAR_LANCE);
        if (getShards() >= 3) options.add(SHARD_BARRAGE);
        options.add(GRAVITY_COLLAPSE);
        if (d < 8 * 8) {
            options.add(SLAM);
            options.add(SLAM);
        }
        if (phase >= 2) {
            options.add(SINGULARITY);
            if (livingMinions() < 5) options.add(SUMMON);
        }
        options.remove(Integer.valueOf(lastAttack));
        int pick = options.get(random.nextInt(options.size()));
        lastAttack = pick;
        setAttack(pick);
    }

    private int livingMinions() {
        if (!(level() instanceof ServerLevel server)) return 0;
        minions.removeIf(id -> {
            Entity e = server.getEntity(id);
            return e == null || !e.isAlive();
        });
        return minions.size();
    }

    private void endAttack(int cooldown) {
        setAttack(IDLE);
        int phase = getPhase();
        attackCooldown = phase == 3 ? cooldown / 3 : phase == 2 ? cooldown / 2 : cooldown;
    }

    private Vec3 core() {
        return position().add(0, getBbHeight() * 0.62, 0);
    }

    private void tickAttack(ServerLevel level, int attack, int t, LivingEntity target) {
        switch (attack) {
            case METEOR_RAIN -> {
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_ROAR.get(), SoundSource.HOSTILE, 4.0f, 1.3f);
                int count = getPhase() >= 2 ? 10 : 7;
                if (t >= 15 && t < 15 + count * 5 && t % 5 == 0) {
                    List<ServerPlayer> ps = level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(48), p -> !p.isCreative() && !p.isSpectator());
                    LivingEntity victim = ps.isEmpty() ? target : ps.get(random.nextInt(ps.size()));
                    if (victim != null) {
                        BlockPos p = victim.blockPosition().offset(random.nextInt(9) - 4, 0, random.nextInt(9) - 4);
                        Starfall.spawnMeteor(level, p, Starfall.Variant.SMALL, 1.0f);
                    }
                }
                FX.burst(level, ModParticles.COMET_TRAIL.get(), core().add(0, 3, 0), 3, 1.0, 0.05);
                if (t > 15 + count * 5 + 10) endAttack(70);
            }
            case STAR_LANCE -> {
                Vec3 core = core();
                if (t == 1) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.GAZER_CHARGE.get(), SoundSource.HOSTILE, 4.0f, 0.5f);
                    beamDir = target != null ? target.getEyePosition().subtract(core).normalize() : getLookAngle();
                }
                if (t < 30) {
                    FX.spiralIn(level, ModParticles.STAR_SPARKLE.get(), core, 3.0, 6, t);
                } else if (t < 90) {
                    if (t == 30) level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_BEAM.get(), SoundSource.HOSTILE, 5.0f, 1.0f);
                    if (target != null) {
                        Vec3 want = target.getEyePosition().subtract(core).normalize();
                        beamDir = beamDir.lerp(want, getPhase() >= 2 ? 0.07 : 0.045).normalize();
                    }
                    fireBeam(level, core, beamDir);
                } else {
                    endAttack(80);
                }
            }
            case SHARD_BARRAGE -> {
                if (t % 6 == 0 && getShards() > 0) {
                    List<ServerPlayer> ps = level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(48), p -> !p.isCreative() && !p.isSpectator());
                    LivingEntity victim = ps.isEmpty() ? target : ps.get(random.nextInt(ps.size()));
                    int shard = getShards() - 1;
                    double a = tickCount * 0.1 + shard * Math.PI / 3;
                    Vec3 from = core().add(Math.cos(a) * 3.2, 0.5, Math.sin(a) * 3.2);
                    if (victim != null) CrystalShardEntity.launch(level, this, from, victim, 10);
                    entityData.set(SHARDS, shard);
                }
                if (t > 50 || getShards() == 0) endAttack(60);
            }
            case GRAVITY_COLLAPSE -> {
                Vec3 c = core();
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.SINGULARITY_HUM.get(), SoundSource.HOSTILE, 5.0f, 0.5f);
                if (t < 50) {
                    FX.spiralIn(level, ModParticles.VOID_MOTE.get(), c, 12, 10, t);
                    for (Player p : level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(26), p -> !p.isCreative() && !p.isSpectator())) {
                        Vec3 pull = c.subtract(p.position()).normalize().scale(0.13);
                        p.setDeltaMovement(p.getDeltaMovement().add(pull.x, pull.y * 0.4, pull.z));
                        p.hurtMarked = true;
                    }
                } else if (t == 50) {
                    shockwave(level, c, 10, 12.0f, 1.6);
                } else if (t > 70) {
                    endAttack(80);
                }
            }
            case SUMMON -> {
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_ROAR.get(), SoundSource.HOSTILE, 4.0f, 0.6f);
                if (t == 25) {
                    for (int i = 0; i < 3; i++) {
                        Mob m = (i == 2 ? ModEntities.VOID_GAZER.get() : ModEntities.VOID_STALKER.get()).create(level, EntitySpawnReason.MOB_SUMMONED);
                        if (m == null) continue;
                        double a = random.nextDouble() * Math.PI * 2;
                        double x = getX() + Math.cos(a) * 6, z = getZ() + Math.sin(a) * 6;
                        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, (int) Math.floor(x), (int) Math.floor(z));
                        m.snapTo(x, m instanceof VoidGazerEntity ? y + 4 : y, z, random.nextFloat() * 360, 0);
                        if (target != null) m.setTarget(target);
                        m.setPersistenceRequired();
                        level.addFreshEntity(m);
                        minions.add(m.getUUID());
                        FX.burst(level, ParticleTypes.REVERSE_PORTAL, m.position().add(0, 1, 0), 60, 0.5, 0.4);
                        FX.burst(level, ModParticles.VOID_MOTE.get(), m.position().add(0, 1, 0), 30, 0.5, 0.1);
                    }
                }
                if (t > 40) endAttack(60);
            }
            case SINGULARITY -> {
                if (t == 10 && target != null) {
                    SingularityEntity.spawn(level, target.position().add(0, 1.5, 0), this, 80, 8.0f, 14.0f, true);
                }
                if (t > 30) endAttack(60);
            }
            case SLAM -> {
                if (t == 18) shockwave(level, position().add(0, 0.5, 0), 7.5, 10.0f, 1.2);
                if (t > 32) endAttack(40);
            }
            case TRANSITION -> {
                Vec3 c = core();
                FX.spiralIn(level, ModParticles.STAR_SPARKLE.get(), c, 5, 10, t);
                if (t == 30) {
                    shockwave(level, c, 14, 8.0f, 2.0);
                    FX.sphere(level, ModParticles.VOID_MOTE.get(), c, 8, 200);
                    entityData.set(SHARDS, MAX_SHARDS);
                }
                if (t > 50) endAttack(20);
            }
            default -> endAttack(40);
        }
    }

    private void fireBeam(ServerLevel level, Vec3 from, Vec3 dir) {
        Vec3 end = from.add(dir.scale(42));
        BlockHitResult hit = level.clip(new ClipContext(from, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
        if (hit.getType() != HitResult.Type.MISS) end = hit.getLocation();
        FX.line(level, ModParticles.STAR_SPARKLE.get(), from, end, 0.45);
        FX.line(level, ParticleTypes.END_ROD, from, end, 1.5);
        FX.burst(level, ParticleTypes.FLAME, end, 6, 0.3, 0.05);
        FX.burst(level, ParticleTypes.LAVA, end, 1, 0.2, 0);
        AABB box = new AABB(from, end).inflate(1.5);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, box, e -> e != this && !(e instanceof VoidStalkerEntity) && !(e instanceof VoidGazerEntity))) {
            Vec3 c = e.getBoundingBox().getCenter();
            Vec3 seg = end.subtract(from);
            double t = Mth.clamp(c.subtract(from).dot(seg) / seg.lengthSqr(), 0, 1);
            if (from.add(seg.scale(t)).distanceTo(c) < 1.3) {
                if (e.hurtServer(level, level.damageSources().indirectMagic(this, this), getPhase() >= 2 ? 7.0f : 5.0f)) e.igniteForSeconds(3);
            }
        }
    }

    private void shockwave(ServerLevel level, Vec3 c, double radius, float damage, double launch) {
        level.playSound(null, c.x, c.y, c.z, ModSounds.SHOCKWAVE.get(), SoundSource.HOSTILE, 5.0f, 0.8f);
        for (int ring = 1; ring <= 3; ring++) {
            FX.ring(level, ModParticles.VOID_MOTE.get(), c, radius * ring / 3.0, 36 * ring, 0.05);
            FX.ring(level, ParticleTypes.EXPLOSION, c, radius * ring / 3.0, 8 * ring, 0.0);
        }
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(radius), e -> e != this && !(e instanceof VoidStalkerEntity) && !(e instanceof VoidGazerEntity))) {
            if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
            Vec3 away = e.position().subtract(c).multiply(1, 0, 1);
            double d = Math.max(1, away.length());
            if (d > radius) continue;
            e.hurtServer(level, level.damageSources().mobAttack(this), damage);
            e.setDeltaMovement(away.normalize().scale(launch).add(0, launch * 0.55, 0));
            e.hurtMarked = true;
        }
    }

    private void clientEffects() {
        Vec3 core = position().add(0, getBbHeight() * 0.62, 0);
        if (getEmerge() > 0) return;
        if (random.nextInt(2) == 0) {
            level().addParticle(ModParticles.VOID_MOTE.get(), getX() + (random.nextDouble() - 0.5) * 2, getY() + random.nextDouble() * 2, getZ() + (random.nextDouble() - 0.5) * 2, 0, -0.05, 0);
        }
        level().addParticle(ModParticles.GOLD_SPARKLE.get(), core.x + (random.nextDouble() - 0.5), core.y + (random.nextDouble() - 0.5), core.z + (random.nextDouble() - 0.5), 0, 0, 0);
        if (getPhase() >= 2 && random.nextInt(2) == 0) {
            level().addParticle(ParticleTypes.SOUL_FIRE_FLAME, getX() + (random.nextDouble() - 0.5) * 3, getY() + random.nextDouble() * 5, getZ() + (random.nextDouble() - 0.5) * 3, 0, 0.02, 0);
        }
        if (getAttack() == GRAVITY_COLLAPSE || getAttack() == TRANSITION) {
            com.astralfall.client.ClientFX.shakeFrom(position(), 0.8f, 40);
        }
    }

    // ------------------------------------------------------------------ damage, death
    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (getEmerge() > 0 || getAttack() == TRANSITION) return false;
        if (source.is(DamageTypeTags.IS_FALL) || source.is(DamageTypeTags.IS_FIRE) || source.is(DamageTypeTags.IS_DROWNING) || source.is(DamageTypes.IN_WALL)) return false;
        if (source.getEntity() == this) return false;
        if (source.getEntity() instanceof VoidStalkerEntity || source.getEntity() instanceof VoidGazerEntity) return false;
        amount = Math.min(amount, 45.0f);
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (level() instanceof ServerLevel level) {
            for (UUID id : minions) {
                Entity e = level.getEntity(id);
                if (e instanceof LivingEntity l && l.isAlive()) l.kill(level);
            }
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(96))) {
                Starfall.title(p, Component.translatable("title.astralfall.victory").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD),
                    Component.translatable("title.astralfall.victory.sub").withStyle(ChatFormatting.YELLOW));
            }
            level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_DEATH.get(), SoundSource.HOSTILE, 8.0f, 1.0f);
        }
    }

    @Override
    protected void tickDeath() {
        deathTime++;
        setDeltaMovement(0, 0.02, 0);
        if (level() instanceof ServerLevel level) {
            Vec3 c = core();
            if (deathTime % 8 == 0) {
                FX.burst(level, ParticleTypes.EXPLOSION, c, 4, 2.0, 0);
                level.playSound(null, getX(), getY(), getZ(), net.minecraft.sounds.SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 3.0f, 0.8f + random.nextFloat() * 0.4f);
            }
            for (int i = 0; i < 3; i++) {
                double a = random.nextDouble() * Math.PI * 2, b = random.nextDouble() * Math.PI - Math.PI / 2;
                Vec3 dir = new Vec3(Math.cos(a) * Math.cos(b), Math.sin(b), Math.sin(a) * Math.cos(b));
                FX.line(level, ParticleTypes.END_ROD, c, c.add(dir.scale(8 + deathTime * 0.1)), 0.7);
            }
            if (deathTime == 100) {
                FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 3, 2, 0);
                FX.sphere(level, ModParticles.GOLD_SPARKLE.get(), c, 8, 250);
                ExperienceOrb.award(level, c, 800);
                level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withSuppressedOutput(), "time set minecraft:day");
                remove(RemovalReason.KILLED);
            }
        }
    }

    // ------------------------------------------------------------------ boilerplate
    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        bossEvent.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        bossEvent.removePlayer(player);
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distanceSqr) {
        return false;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double dist) {
        return dist < 256 * 256;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.BOSS_ROAR.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 400;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return net.minecraft.sounds.SoundEvents.WITHER_HURT;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0f;
    }

    @Override
    public float getVoicePitch() {
        return 0.6f;
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putInt("Phase", getPhase());
        if (home != null) out.putIntArray("Home", new int[]{home.getX(), home.getY(), home.getZ()});
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        entityData.set(PHASE, in.getIntOr("Phase", 1));
        in.getIntArray("Home").ifPresent(a -> {
            if (a.length == 3) home = new BlockPos(a[0], a[1], a[2]);
        });
        if (hasCustomName()) bossEvent.setName(getDisplayName());
    }
}
