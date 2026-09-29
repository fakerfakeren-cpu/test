package com.oathbound.entity.boss;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.Config;
import com.oathbound.event.GloamingTravel;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundStopSoundPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;

import java.util.List;
import java.util.UUID;

/**
 * Shared machinery for the seal keepers and the Hollow King: they sleep until challenged, then show a boss
 * bar, run a move-by-move state machine ({@link #move}/{@link #moveTicks}), cap burst damage, never despawn,
 * play their theme to nearby players and credit every nearby player's Chronicle when they fall.
 */
public abstract class KeeperEntity extends Monster {
    private static final EntityDataAccessor<Boolean> SLEEPING = SynchedEntityData.defineId(KeeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> MOVE = SynchedEntityData.defineId(KeeperEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> MOVE_TICKS = SynchedEntityData.defineId(KeeperEntity.class, EntityDataSerializers.INT);

    public static final int IDLE = 0;

    protected final ServerBossEvent bar;
    protected int cooldown = 40;
    private int themeTimer;
    private boolean scaled;

    protected KeeperEntity(EntityType<? extends KeeperEntity> type, Level level, BossEvent.BossBarColor color) {
        super(type, level);
        this.bar = new ServerBossEvent(UUID.randomUUID(), Component.translatable(type.getDescriptionId()), color, BossEvent.BossBarOverlay.NOTCHED_12);
        this.bar.setVisible(false);
        this.xpReward = 0;
        setPersistenceRequired();
    }

    // ------------------------------------------------------------------ hooks for subclasses
    /** Quest id credited to nearby players on death ("caldris", "veyl", ...). */
    protected abstract String questId();

    protected abstract float baseHealth();

    protected double healthMultiplier() {
        return Config.keeperHealthMultiplier();
    }

    protected SoundEvent theme() {
        return ModSounds.THEME_KEEPER.get();
    }

    protected int themeLength() {
        return 640;
    }

    protected double wakeRange() {
        return 11.0;
    }

    /** Called once when the keeper wakes. */
    protected void onWake(ServerLevel level, Player by) {}

    /** Server brain while awake and not mid-death. */
    protected abstract void think(ServerLevel level, LivingEntity target);

    /** Largest single hit this keeper will take. */
    protected float damageCap() {
        return 30.0f;
    }

    // ------------------------------------------------------------------ state
    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(SLEEPING, true);
        builder.define(MOVE, IDLE);
        builder.define(MOVE_TICKS, 0);
    }

    public boolean isSleeping() {
        return entityData.get(SLEEPING);
    }

    public int move() {
        return entityData.get(MOVE);
    }

    public int moveTicks() {
        return entityData.get(MOVE_TICKS);
    }

    protected void startMove(int move) {
        entityData.set(MOVE, move);
        entityData.set(MOVE_TICKS, 0);
    }

    protected void endMove(int cooldown) {
        entityData.set(MOVE, IDLE);
        entityData.set(MOVE_TICKS, 0);
        this.cooldown = cooldown;
    }

    // ------------------------------------------------------------------ lifecycle
    @Override
    protected void registerGoals() {}

    private void applyScaling() {
        if (scaled) return;
        scaled = true;
        var attr = getAttribute(Attributes.MAX_HEALTH);
        if (attr != null) {
            double hp = baseHealth() * healthMultiplier();
            if (Math.abs(attr.getBaseValue() - hp) > 0.5) {
                attr.setBaseValue(hp);
                setHealth((float) hp);
            }
        }
    }

    public void wake(ServerLevel level, Player by) {
        if (!isSleeping()) return;
        entityData.set(SLEEPING, false);
        bar.setVisible(true);
        themeTimer = 0;
        if (by != null) setTarget(by);
        onWake(level, by);
        if (flaresOnWake()) {
            SpellMarkEntity.sigil(level, position(), 3.5f, hue(), 60);
            SpellMarkEntity.ring(level, position(), 12f, hue(), 24);
        }
    }

    /** The colour of this keeper's magic, for spell marks. */
    protected SpellMarkEntity.Hue hue() {
        return SpellMarkEntity.Hue.GLOAM;
    }

    protected boolean flaresOnWake() {
        return true;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        applyScaling();
        bar.setProgress(getHealth() / getMaxHealth());
        if (isSleeping()) {
            setDeltaMovement(getDeltaMovement().multiply(0, 1, 0));
            if (tickCount % 10 == 0) {
                for (Player p : level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(wakeRange()), this::isChallenger)) {
                    if (hasLineOfSight(p)) {
                        wake(level, p);
                        break;
                    }
                }
            }
            return;
        }
        LivingEntity target = pickTarget(level);
        if (--themeTimer <= 0) {
            themeTimer = themeLength();
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(48))) {
                level.playSound(null, p.getX(), p.getY(), p.getZ(), theme(), SoundSource.RECORDS, 0.9f, 1.0f);
            }
        }
        if (move() != IDLE) entityData.set(MOVE_TICKS, moveTicks() + 1);
        think(level, target);
    }

    protected boolean isChallenger(Player p) {
        return p.isAlive() && !p.isCreative() && !p.isSpectator();
    }

    private LivingEntity pickTarget(ServerLevel level) {
        LivingEntity t = getTarget();
        if (t instanceof Player p && !isChallenger(p)) t = null;
        if (t == null || !t.isAlive() || t.distanceToSqr(this) > 48 * 48) {
            Player best = null;
            double bd = 40 * 40;
            for (Player p : level.players()) {
                if (!isChallenger(p)) continue;
                double d = p.distanceToSqr(this);
                if (d < bd) {
                    bd = d;
                    best = p;
                }
            }
            t = best;
            setTarget(best);
        }
        if (t == null && tickCount % 40 == 0) heal(2.0f);
        return t;
    }

    protected List<Player> challengers(ServerLevel level, double radius) {
        return level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(radius), this::isChallenger);
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (source.is(DamageTypeTags.IS_FALL) || source.is(DamageTypes.IN_WALL) || source.is(DamageTypes.DROWN)) return false;
        if (source.getEntity() == this) return false;
        if (isSleeping() && source.getEntity() instanceof Player p) wake(level, p);
        return super.hurtServer(level, source, Math.min(amount, damageCap()));
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (level() instanceof ServerLevel level) {
            bar.setVisible(false);
            SpellMarkEntity.pillar(level, position(), 1.4f, hue(), 50);
            SpellMarkEntity.ring(level, position(), 16f, hue(), 30);
            SpellMarkEntity.sigil(level, position(), 4.5f, hue(), 90);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(blockPosition()).inflate(64))) {
                QuestLog.grant(p, questId(), "slain");
                p.connection.send(new ClientboundStopSoundPacket(theme().location(), SoundSource.RECORDS));
                GloamingTravel.title(p, Component.translatable("title.oathbound." + questId() + ".slain").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD),
                    Component.translatable("title.oathbound." + questId() + ".slain.sub").withStyle(ChatFormatting.YELLOW, ChatFormatting.ITALIC));
            }
        }
    }

    // ------------------------------------------------------------------ boilerplate
    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        bar.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        bar.removePlayer(player);
    }

    @Override
    public boolean removeWhenFarAway(double distanceSqr) {
        return false;
    }

    @Override
    public boolean isPushable() {
        return !isSleeping() && super.isPushable();
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double dist) {
        return dist < 160 * 160;
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putBoolean("Sleeping", isSleeping());
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        entityData.set(SLEEPING, in.getBooleanOr("Sleeping", true));
        bar.setVisible(!isSleeping());
        scaled = true;
    }
}
