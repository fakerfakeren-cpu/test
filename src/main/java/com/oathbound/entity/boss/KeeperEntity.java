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
import net.minecraft.world.phys.Vec3;

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
    /** Where it keeps its vigil, so a failed challenge can put it back. */
    private Vec3 rest;
    private float restYaw;
    /** Ticks with no challenger left standing nearby, and the most challengers it has faced this fight. */
    private int alone;
    private int challengersSeen = 1;
    private boolean challenged;
    private static final net.minecraft.resources.Identifier PARTY_DAMAGE = net.minecraft.resources.Identifier.fromNamespaceAndPath("oathbound", "party_damage");
    /** Each extra challenger adds this much health (x base) and damage (x base). */
    private static final double PARTY_HEALTH = 0.6, PARTY_DAMAGE_PER = 0.15;
    /** How long the arena must stand empty (or every challenger lie dead) before the keeper resets. */
    private static final int RESET_AFTER = 100;

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

    /**
     * Story keepers sleep behind their structure's puzzle: until it is solved they cannot be woken or harmed, so
     * digging round a ward gains nothing. Solving the puzzle unseals every keeper nearby ({@link #unsealNear}).
     * Keepers saved before seals existed load unsealed.
     */
    private boolean sealed = guardedByPuzzle();

    protected boolean guardedByPuzzle() {
        return false;
    }

    public boolean isSealed() {
        return sealed;
    }

    public static void unsealNear(ServerLevel level, net.minecraft.core.BlockPos pos, double radius) {
        for (KeeperEntity k : level.getEntitiesOfClass(KeeperEntity.class, new net.minecraft.world.phys.AABB(pos).inflate(radius))) k.sealed = false;
    }

    private void sealedNotice(Player p) {
        p.sendOverlayMessage(Component.translatable("message.oathbound.keeper.sealed").withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
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
        alone = 0;
        challenged = false;
        scaleFor(level, Math.max(1, challengers(level, 32).size()));
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
        if (rest == null) {
            rest = position();
            restYaw = getYRot();
        }
        if (!isSleeping() && tickCount % 20 == 0) {
            int n = challengers(level, 40).size();
            if (n > challengersSeen) scaleFor(level, n);
            if (n > 0) challenged = true;
            alone = n == 0 ? alone + 20 : 0;
            // only a fight someone actually started can be lost (woken by a command or a test, it fights on)
            if (challenged && alone >= RESET_AFTER) {
                reset(level);
                return;
            }
        }
        if (isSleeping()) {
            setDeltaMovement(getDeltaMovement().multiply(0, 1, 0));
            if (tickCount % 10 == 0) {
                for (Player p : level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(wakeRange()), this::isChallenger)) {
                    if (hasLineOfSight(p)) {
                        if (sealed) {
                            if (tickCount % 60 == 0) sealedNotice(p);
                            continue;
                        }
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

    /**
     * Toughens the keeper for a party: health grows with each challenger (keeping the share it has left) and so
     * does its damage. Only ever grows during a fight; a reset brings it back to a single challenger's measure.
     */
    private void scaleFor(ServerLevel level, int n) {
        challengersSeen = n;
        applyScaling();
        var hp = getAttribute(Attributes.MAX_HEALTH);
        if (hp != null) {
            float share = getHealth() / getMaxHealth();
            hp.setBaseValue(baseHealth() * healthMultiplier() * (1 + PARTY_HEALTH * (n - 1)));
            setHealth(Math.max(1f, share * getMaxHealth()));
        }
        var dmg = getAttribute(Attributes.ATTACK_DAMAGE);
        if (dmg != null) {
            dmg.removeModifier(PARTY_DAMAGE);
            if (n > 1) dmg.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(PARTY_DAMAGE, PARTY_DAMAGE_PER * (n - 1),
                net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
        }
    }

    /**
     * The challenge failed (every challenger fell or fled): the keeper returns to its vigil whole, and the fight
     * must be won again from the start. The puzzle that guarded it stays solved.
     */
    public void reset(ServerLevel level) {
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(blockPosition()).inflate(64))) {
            p.connection.send(new ClientboundStopSoundPacket(theme().location(), SoundSource.RECORDS));
            p.sendSystemMessage(Component.translatable("message.oathbound.keeper.reset", getDisplayName()).withStyle(net.minecraft.ChatFormatting.GRAY, net.minecraft.ChatFormatting.ITALIC));
        }
        setTarget(null);
        endMove(40);
        entityData.set(SLEEPING, true);
        bar.setVisible(false);
        removeAllEffects();
        clearFire();
        alone = 0;
        challenged = false;
        scaleFor(level, 1);
        setHealth(getMaxHealth());
        if (rest != null) {
            teleportTo(rest.x, rest.y, rest.z);
            setYRot(restYaw);
            setYHeadRot(restYaw);
            yBodyRot = restYaw;
        }
        setDeltaMovement(Vec3.ZERO);
        onReset(level);
    }

    /** Subclasses put their own fight state back (phases, summons, arena seals). */
    protected void onReset(ServerLevel level) {}

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
        if (isSleeping() && sealed && !source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            if (source.getEntity() instanceof Player p) sealedNotice(p);
            return false;
        }
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
        out.putBoolean("Sealed", sealed);
        if (rest != null) out.putIntArray("Rest", new int[]{(int) Math.round(rest.x * 16), (int) Math.round(rest.y * 16), (int) Math.round(rest.z * 16), Math.round(restYaw)});
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        entityData.set(SLEEPING, in.getBooleanOr("Sleeping", true));
        sealed = in.getBooleanOr("Sealed", false);
        in.getIntArray("Rest").ifPresent(a -> {
            if (a.length == 4) {
                rest = new Vec3(a[0] / 16.0, a[1] / 16.0, a[2] / 16.0);
                restYaw = a[3];
            }
        });
        bar.setVisible(!isSleeping());
        scaled = true;
    }
}
