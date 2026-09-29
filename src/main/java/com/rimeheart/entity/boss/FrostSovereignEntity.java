package com.rimeheart.entity.boss;

import com.rimeheart.Config;
import com.rimeheart.entity.mob.FrostWraithEntity;
import com.rimeheart.entity.projectile.IceShardEntity;
import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModEntities;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.registry.ModTags;
import com.rimeheart.util.FX;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
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
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * The Frost Sovereign, heart of the Long Winter. A towering spirit of ice that drifts over the snow.
 * Attacks: Icicle Barrage, Glacial Eruption (telegraphed), Frost Breath, Stomp. At half health it calls
 * Frost Wraiths, erupts three times at once and attacks twice as often.
 */
public class FrostSovereignEntity extends Monster {
    public static final int IDLE = 0, BARRAGE = 1, ERUPTION = 2, BREATH = 3, STOMP = 4, SUMMON = 5, TRANSITION = 6;
    public static final int EMERGE_TIME = 70;
    private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(FrostSovereignEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> ATTACK = SynchedEntityData.defineId(FrostSovereignEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> ATTACK_TICKS = SynchedEntityData.defineId(FrostSovereignEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> EMERGE = SynchedEntityData.defineId(FrostSovereignEntity.class, EntityDataSerializers.INT);

    private final ServerBossEvent bossEvent = new ServerBossEvent(UUID.randomUUID(), Component.translatable("entity.rimeheart.frost_sovereign"),
        BossEvent.BossBarColor.BLUE, BossEvent.BossBarOverlay.NOTCHED_10);
    private BlockPos home;
    private int attackCooldown = 40;
    private int lastAttack = -1;
    private int noTargetTicks;
    private final List<Vec3> eruptions = new ArrayList<>();
    private final List<UUID> minions = new ArrayList<>();

    public FrostSovereignEntity(EntityType<? extends FrostSovereignEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
        this.xpReward = 0;
        this.setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 400.0)
            .add(Attributes.ARMOR, 10.0)
            .add(Attributes.ARMOR_TOUGHNESS, 4.0)
            .add(Attributes.ATTACK_DAMAGE, 12.0)
            .add(Attributes.FOLLOW_RANGE, 64.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
            .add(Attributes.MOVEMENT_SPEED, 0.25)
            .add(Attributes.FLYING_SPEED, 0.3);
    }

    /** Called by the Winter Horn ritual: rise out of the ground below the altar. */
    public void beginEmerging(BlockPos home) {
        this.home = home;
        entityData.set(EMERGE, EMERGE_TIME);
        double hp = 400.0 * Config.bossHealthMultiplier();
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
    }

    public int getPhase() { return entityData.get(PHASE); }
    public int getAttack() { return entityData.get(ATTACK); }
    public int getAttackTicks() { return entityData.get(ATTACK_TICKS); }
    public int getEmerge() { return entityData.get(EMERGE); }

    private void setAttack(int attack) {
        entityData.set(ATTACK, attack);
        entityData.set(ATTACK_TICKS, 0);
    }

    @Override
    protected void registerGoals() {}

    @Override
    public boolean canFreeze() {
        return false;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            if (random.nextInt(2) == 0) level().addParticle(ParticleTypes.SNOWFLAKE, getRandomX(1.5), getY() + random.nextDouble() * 5, getRandomZ(1.5), 0, -0.05, 0);
            if (random.nextInt(3) == 0) level().addParticle(ModParticles.FROST_GLINT.get(), getRandomX(1.2), getY() + 3 + random.nextDouble() * 2, getRandomZ(1.2), 0, 0.02, 0);
            if (getPhase() >= 2) {
                for (int i = 0; i < 3; i++) {
                    level().addParticle(ModParticles.SNOW_PUFF.get(), getX() + (random.nextDouble() - 0.5) * 24, getY() + random.nextDouble() * 8, getZ() + (random.nextDouble() - 0.5) * 24, -0.2, -0.05, 0.05);
                }
            }
        }
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
        setDeltaMovement(0, 0.07, 0);
        Vec3 c = position().add(0, 2, 0);
        FX.spiralIn(level, ParticleTypes.SNOWFLAKE, c, 5.0, 10, tickCount);
        FX.burst(level, new BlockParticleOption(ParticleTypes.BLOCK, Blocks.PACKED_ICE.defaultBlockState()), getX(), getY(), getZ(), 8, 1.5, 0.3, 1.5, 0.1);
        if (emerge == EMERGE_TIME - 10) {
            level.playSound(null, getX(), getY(), getZ(), ModSounds.SOVEREIGN_ROAR.get(), SoundSource.HOSTILE, 5.0f, 0.8f);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(96))) {
                SovereignRitual.title(p, Component.translatable("entity.rimeheart.frost_sovereign").withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD),
                    Component.translatable("title.rimeheart.sovereign.sub").withStyle(ChatFormatting.WHITE, ChatFormatting.ITALIC));
            }
        }
        if (emerge == 1) {
            FX.sphere(level, ModParticles.FROST_GLINT.get(), c, 5, 140);
            FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 1, 0.5, 0);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.ICE_SHATTER.get(), SoundSource.HOSTILE, 4.0f, 0.5f);
            attackCooldown = 30;
        }
        entityData.set(EMERGE, emerge - 1);
    }

    private void updatePhase(ServerLevel level) {
        if (getPhase() == 1 && getHealth() <= getMaxHealth() * 0.5f) {
            entityData.set(PHASE, 2);
            setAttack(TRANSITION);
            bossEvent.setColor(BossEvent.BossBarColor.WHITE);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.SOVEREIGN_ROAR.get(), SoundSource.HOSTILE, 5.0f, 1.1f);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(96))) {
                p.sendSystemMessage(Component.translatable("message.rimeheart.boss.phase2").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
            }
        }
    }

    private LivingEntity acquireTarget(ServerLevel level) {
        LivingEntity target = getTarget();
        if (target instanceof Player p && (p.isCreative() || p.isSpectator())) target = null;
        if (target != null && (!target.isAlive() || target.distanceToSqr(this) > 64 * 64)) target = null;
        if (target == null) {
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
            double orbit = tickCount * 0.01;
            double radius = getAttack() == STOMP ? 2.5 : 9;
            want = target.position().add(Math.cos(orbit) * radius, 0, Math.sin(orbit) * radius);
            int ground = level().getHeight(Heightmap.Types.MOTION_BLOCKING, (int) Math.floor(want.x), (int) Math.floor(want.z));
            want = new Vec3(want.x, Math.max(ground, target.getY()) + 0.6, want.z);
            if (home != null && want.distanceToSqr(Vec3.atCenterOf(home)) > 40 * 40) {
                want = Vec3.atCenterOf(home).add(want.subtract(Vec3.atCenterOf(home)).normalize().scale(40));
            }
            double dx = target.getX() - getX(), dz = target.getZ() - getZ();
            float yaw = (float) (Mth.atan2(dz, dx) * (180f / Math.PI)) - 90f;
            setYRot(Mth.approachDegrees(getYRot(), yaw, getAttack() == BREATH ? 2.5f : 8f));
            yBodyRot = getYRot();
            yHeadRot = getYRot();
        } else {
            want = Vec3.atCenterOf(home == null ? blockPosition() : home).add(0, 1, 0);
        }
        boolean rooted = getAttack() == BREATH || getAttack() == TRANSITION || getAttack() == SUMMON;
        Vec3 to = want.subtract(position());
        double speed = rooted ? 0.0 : (getPhase() >= 2 ? 0.3 : 0.22);
        Vec3 v = to.lengthSqr() > 1 ? to.normalize().scale(speed) : to.scale(0.1);
        setDeltaMovement(getDeltaMovement().scale(0.7).add(v.scale(0.3)).add(0, Mth.sin(tickCount * 0.06f) * 0.008, 0));
    }

    private void chooseAttack(LivingEntity target) {
        double d = distanceToSqr(target);
        List<Integer> options = new ArrayList<>(List.of(BARRAGE, ERUPTION, BREATH));
        if (d < 7 * 7) {
            options.add(STOMP);
            options.add(STOMP);
        }
        if (getPhase() >= 2 && livingMinions() < 4) options.add(SUMMON);
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
        attackCooldown = getPhase() >= 2 ? cooldown / 2 : cooldown;
    }

    private Vec3 head() {
        return position().add(0, 4.4, 0);
    }

    private void tickAttack(ServerLevel level, int attack, int t, LivingEntity target) {
        switch (attack) {
            case BARRAGE -> {
                if (target != null && t % 5 == 0 && t <= 40) {
                    double a = t * 0.7;
                    Vec3 from = position().add(Math.cos(a) * 2.5, 5.2 + Math.sin(a) * 0.6, Math.sin(a) * 2.5);
                    IceShardEntity.barrage(level, this, from, target, 18, getPhase() >= 2 ? 7.0f : 6.0f);
                    FX.burst(level, ModParticles.FROST_GLINT.get(), from, 6, 0.2, 0.02);
                    level.playSound(null, from.x, from.y, from.z, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.HOSTILE, 2.0f, 0.6f);
                }
                if (t >= 60) endAttack(50);
            }
            case ERUPTION -> {
                if (t == 1) {
                    eruptions.clear();
                    if (target != null) {
                        eruptions.add(target.position());
                        if (getPhase() >= 2) {
                            for (int i = 0; i < 2; i++) {
                                eruptions.add(target.position().add(random.nextGaussian() * 4, 0, random.nextGaussian() * 4));
                            }
                        }
                    }
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.COLD_SNAP.get(), SoundSource.HOSTILE, 3.0f, 0.5f);
                }
                if (t < 28 && t % 3 == 0) {
                    for (Vec3 p : eruptions) {
                        FX.ring(level, ParticleTypes.SNOWFLAKE, p.add(0, 0.15, 0), 2.6, 24, 0.01);
                        FX.ring(level, ModParticles.FROST_GLINT.get(), p.add(0, 0.15, 0), 2.6 * (t / 28.0), 12, 0.0);
                    }
                }
                if (t == 28) {
                    var ice = new BlockParticleOption(ParticleTypes.BLOCK, Blocks.PACKED_ICE.defaultBlockState());
                    for (Vec3 p : eruptions) {
                        for (int i = 0; i < 9; i++) {
                            double a = i * Math.PI * 2 / 9;
                            Vec3 b = p.add(Math.cos(a) * 1.4, 0, Math.sin(a) * 1.4);
                            FX.line(level, ModParticles.FROST_GLINT.get(), b, b.add(0, 2.5 + (i % 3), 0), 0.25);
                            FX.burst(level, ice, b.x, b.y + 1, b.z, 8, 0.2, 1.0, 0.2, 0.15);
                        }
                        level.playSound(null, p.x, p.y, p.z, ModSounds.ICE_SHATTER.get(), SoundSource.HOSTILE, 3.0f, 0.7f);
                        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(p, p).inflate(2.8, 2.5, 2.8), this::canHarm)) {
                            e.hurtServer(level, level.damageSources().indirectMagic(this, this), getPhase() >= 2 ? 13.0f : 10.0f);
                            Frost.chill(e, 200);
                            e.setDeltaMovement(e.getDeltaMovement().add(0, 0.9, 0));
                            e.hurtMarked = true;
                        }
                    }
                }
                if (t >= 50) endAttack(60);
            }
            case BREATH -> {
                Vec3 look = Vec3.directionFromRotation(15f, getYRot());
                if (t >= 12 && t <= 56) {
                    Vec3 mouth = head().add(look.scale(1.2));
                    for (int i = 0; i < 8; i++) {
                        Vec3 dir = look.add((random.nextDouble() - 0.5) * 0.4, (random.nextDouble() - 0.5) * 0.3, (random.nextDouble() - 0.5) * 0.4).normalize();
                        level.sendParticles(i % 3 == 0 ? ModParticles.SNOW_PUFF.get() : ParticleTypes.SNOWFLAKE, true, true, mouth.x, mouth.y, mouth.z, 0, dir.x, dir.y, dir.z, 0.7);
                    }
                    if (t % 5 == 0) {
                        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(13), this::canHarm)) {
                            Vec3 to = e.getBoundingBox().getCenter().subtract(mouth);
                            if (to.length() > 13 || to.normalize().dot(look) < 0.85) continue;
                            e.hurtServer(level, level.damageSources().indirectMagic(this, this), 3.0f);
                            Frost.chill(e, 50);
                        }
                    }
                }
                if (t == 12 || t == 34) level.playSound(null, getX(), getY(), getZ(), ModSounds.BLIZZARD.get(), SoundSource.HOSTILE, 3.0f, 0.7f);
                if (t >= 62) endAttack(60);
            }
            case STOMP -> {
                if (t == 15) {
                    Vec3 c = position();
                    level.playSound(null, c.x, c.y, c.z, ModSounds.GLACIER_SLAM.get(), SoundSource.HOSTILE, 4.0f, 0.7f);
                    var ice = new BlockParticleOption(ParticleTypes.BLOCK, Blocks.PACKED_ICE.defaultBlockState());
                    for (int r = 1; r <= 6; r++) FX.ring(level, ice, c.add(0, 0.3, 0), r, r * 12, 0.4);
                    for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(6, 3, 6), this::canHarm)) {
                        Vec3 away = e.position().subtract(c).multiply(1, 0, 1);
                        e.hurtServer(level, level.damageSources().mobAttack(this), 12.0f);
                        Frost.chill(e, 100);
                        e.setDeltaMovement(away.normalize().scale(1.1).add(0, 0.6, 0));
                        e.hurtMarked = true;
                    }
                }
                if (t >= 30) endAttack(40);
            }
            case SUMMON -> {
                if (t == 20) {
                    for (int i = 0; i < 2; i++) {
                        FrostWraithEntity w = ModEntities.FROST_WRAITH.get().create(level, EntitySpawnReason.MOB_SUMMONED);
                        if (w == null) continue;
                        double a = random.nextDouble() * Math.PI * 2;
                        w.snapTo(getX() + Math.cos(a) * 4, getY() + 3, getZ() + Math.sin(a) * 4, random.nextFloat() * 360f, 0f);
                        if (target != null) w.setTarget(target);
                        level.addFreshEntity(w);
                        minions.add(w.getUUID());
                        FX.burst(level, ModParticles.WRAITH_WISP.get(), w.position().add(0, 1, 0), 30, 0.5, 0.05);
                    }
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.WRAITH_AMBIENT.get(), SoundSource.HOSTILE, 3.0f, 0.6f);
                }
                if (t >= 40) endAttack(40);
            }
            case TRANSITION -> {
                if (t % 4 == 0) FX.sphere(level, ModParticles.FROST_GLINT.get(), position().add(0, 2.5, 0), 3 + t * 0.08, 40);
                if (t == 30) FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, position().add(0, 2, 0), 1, 0, 0);
                if (t >= 60) endAttack(20);
            }
            default -> endAttack(20);
        }
    }

    private boolean canHarm(LivingEntity e) {
        if (e == this || !e.isAlive() || e.typeHolder().is(ModTags.WINTER_CREATURES)) return false;
        return !(e instanceof Player p) || (!p.isCreative() && !p.isSpectator());
    }

    // ------------------------------------------------------------------ damage, death
    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (getEmerge() > 0 || getAttack() == TRANSITION) return false;
        if (source.is(DamageTypeTags.IS_FALL) || source.is(DamageTypeTags.IS_FREEZING) || source.is(DamageTypeTags.IS_DROWNING) || source.is(DamageTypes.IN_WALL)) return false;
        if (source.getEntity() == this || (source.getEntity() != null && source.getEntity().typeHolder().is(ModTags.WINTER_CREATURES))) return false;
        amount = Math.min(amount, 40.0f);
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
                SovereignRitual.title(p, Component.translatable("title.rimeheart.victory").withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD),
                    Component.translatable("title.rimeheart.victory.sub").withStyle(ChatFormatting.WHITE));
            }
            level.playSound(null, getX(), getY(), getZ(), ModSounds.SOVEREIGN_DEATH.get(), SoundSource.HOSTILE, 6.0f, 1.0f);
        }
    }

    @Override
    protected void tickDeath() {
        deathTime++;
        setDeltaMovement(0, -0.01, 0);
        if (level() instanceof ServerLevel level) {
            Vec3 c = position().add(0, 2.5, 0);
            if (deathTime % 6 == 0) {
                FX.burst(level, new BlockParticleOption(ParticleTypes.BLOCK, Blocks.ICE.defaultBlockState()), c, 30, 1.5, 0.3);
                level.playSound(null, getX(), getY(), getZ(), ModSounds.ICE_SHATTER.get(), SoundSource.HOSTILE, 3.0f, 0.6f + random.nextFloat() * 0.4f);
            }
            FX.burst(level, ParticleTypes.SNOWFLAKE, c, 8, 2.0, 0.1);
            if (deathTime == 80) {
                FX.sphere(level, ModParticles.FROST_GLINT.get(), c, 6, 220);
                FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 2, 1, 0);
                ExperienceOrb.award(level, c, 500);
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
        return ModSounds.SOVEREIGN_ROAR.get();
    }

    @Override
    public int getAmbientSoundInterval() {
        return 360;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.GLASS_BREAK;
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
