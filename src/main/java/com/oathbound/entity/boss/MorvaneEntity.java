package com.oathbound.entity.boss;

import com.oathbound.Config;
import com.oathbound.block.WardLanternBlock;
import com.oathbound.entity.mob.ForswornKnightEntity;
import com.oathbound.entity.projectile.CrownBladeEntity;
import com.oathbound.entity.projectile.GloamBoltEntity;
import com.oathbound.event.GloamingTravel;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Puzzles;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Morvane, the Hollow King. He waits on his throne until someone steps inside the ring of Ward Lanterns.
 * <ol>
 *   <li><b>Oathbreaker</b> (100–60%): three-cut sword combos, the Gloam Lunge, and the Oath of Ruin stance
 *       (strike him in melee during it and he counters; an arrow or spell breaks it).</li>
 *   <li><b>Hollow Sorcerer</b> (60–25%): he rises into the air; Crown of Blades, Eclipse Pillars and Call
 *       the Forsworn.</li>
 *   <li><b>The Hollow</b> (25–0%): the Ward Lanterns gutter out and he becomes untouchable shadow. Relight all
 *       four and he is Unveiled: stunned, and wide open. Then the dark returns.</li>
 * </ol>
 */
public class MorvaneEntity extends KeeperEntity {
    public static final int COMBO = 1, LUNGE = 2, RUIN = 3, BLADES = 4, PILLARS = 5, FORSWORN = 6, TRANSITION = 7,
        BOLTS = 8, SHADOWSTEP = 9, UNVEILED = 10, RISING = 11;
    private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(MorvaneEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> HOLLOW = SynchedEntityData.defineId(MorvaneEntity.class, EntityDataSerializers.BOOLEAN);
    private BlockPos home;
    private Vec3 lungeDir = Vec3.ZERO;
    private final List<Vec3> pillars = new ArrayList<>();
    private final List<UUID> knights = new ArrayList<>();
    private boolean countered;
    private int lastMove;

    public MorvaneEntity(EntityType<? extends MorvaneEntity> type, Level level) {
        super(type, level, BossEvent.BossBarColor.PURPLE);
        bar.setDarkenScreen(true);
        bar.setCreateWorldFog(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
            .add(Attributes.MAX_HEALTH, 800.0)
            .add(Attributes.ARMOR, 14.0)
            .add(Attributes.ARMOR_TOUGHNESS, 6.0)
            .add(Attributes.ATTACK_DAMAGE, 14.0)
            .add(Attributes.MOVEMENT_SPEED, 0.3)
            .add(Attributes.FOLLOW_RANGE, 64.0)
            .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
            .add(Attributes.STEP_HEIGHT, 1.5);
    }

    public void setHome(BlockPos home) {
        this.home = home;
    }

    private BlockPos home() {
        return home != null ? home : GloamingTravel.THRONE;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(PHASE, 1);
        builder.define(HOLLOW, false);
    }

    public int phase() {
        return entityData.get(PHASE);
    }

    public boolean isHollow() {
        return entityData.get(HOLLOW);
    }

    @Override
    protected String questId() {
        return "morvane";
    }

    @Override
    protected float baseHealth() {
        return 800f;
    }

    @Override
    protected double healthMultiplier() {
        return Config.bossHealthMultiplier();
    }

    @Override
    protected SoundEvent theme() {
        return ModSounds.THEME_MORVANE.get();
    }

    @Override
    protected int themeLength() {
        return 760;
    }

    @Override
    protected float damageCap() {
        return 40f;
    }

    @Override
    protected double wakeRange() {
        return 0;
    }

    // ------------------------------------------------------------------ the challenge
    private List<BlockPos> lanterns(ServerLevel level) {
        return Puzzles.find(level, home(), 13, ModBlocks.WARD_LANTERN.get());
    }

    private void sealArena(ServerLevel level, boolean sealed) {
        BlockPos h = home();
        for (int x = -2; x <= 2; x++)
            for (int y = 1; y <= 5; y++) {
                BlockPos p = h.offset(x, y, 17);
                if (sealed && level.getBlockState(p).isAir()) level.setBlock(p, ModBlocks.ARCANE_WARD.get().defaultBlockState(), 3);
                if (!sealed && level.getBlockState(p).is(ModBlocks.ARCANE_WARD.get())) level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
            }
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        if (isSleeping() && tickCount % 10 == 0) {
            Vec3 c = Vec3.atBottomCenterOf(home());
            for (Player p : level.getEntitiesOfClass(Player.class, new AABB(home()).inflate(16, 8, 16), this::isChallenger)) {
                if (p.position().multiply(1, 0, 1).distanceTo(c.multiply(1, 0, 1)) < 14.5) {
                    wake(level, p);
                    break;
                }
            }
        }
        super.customServerAiStep(level);
    }

    @Override
    protected void onWake(ServerLevel level, Player by) {
        sealArena(level, true);
        startMove(RISING);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_VOICE.get(), SoundSource.HOSTILE, 4.0f, 1.0f);
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(64))) {
            QuestLog.grant(p, "throne", "challenged");
            GloamingTravel.title(p, Component.translatable("entity.oathbound.morvane").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD),
                Component.translatable("title.oathbound.morvane.sub").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            p.sendSystemMessage(Component.translatable("message.oathbound.morvane.wake").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
        }
    }

    // ------------------------------------------------------------------ brain
    @Override
    protected void think(ServerLevel level, LivingEntity target) {
        updatePhase(level);
        int t = moveTicks();
        boolean flying = phase() == 2 && move() != TRANSITION;
        setNoGravity(flying || isHollow());
        if (flying) hoverOver(target);
        if (target != null && move() != UNVEILED) getLookControl().setLookAt(target, 30f, 30f);
        switch (move()) {
            case RISING -> {
                getNavigation().stop();
                if (t % 12 == 0 && t <= 48) {
                    List<BlockPos> ls = lanterns(level);
                    int i = t / 12 - 1;
                    if (i >= 0 && i < ls.size()) {
                        WardLanternBlock.snuff(level, ls.get(i));
                        plume(level, ls.get(i));
                    }
                }
                if (t < 60) Vfx.spiralIn(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.5, 0), 5, 8, t);
                if (t == 60) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_ROAR.get(), SoundSource.HOSTILE, 5.0f, 0.8f);
                    Vfx.sphere(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.6, 0), 4, 120);
                    Vfx.burst(level, ParticleTypes.EXPLOSION_EMITTER, position().add(0, 1, 0), 1, 0, 0);
                    for (BlockPos l : lanterns(level)) WardLanternBlock.relight(level, l);
                }
                if (t > 70) endMove(20);
            }
            case IDLE -> {
                if (target == null) return;
                if (phase() == 1) {
                    double d = distanceToSqr(target);
                    if (d > 3 * 3) getNavigation().moveTo(target, 1.1);
                    else getNavigation().stop();
                }
                if (--cooldown <= 0) chooseMove(target);
            }
            case COMBO -> combo(level, target, t);
            case LUNGE -> lunge(level, target, t);
            case RUIN -> {
                getNavigation().stop();
                if (t == 1) {
                    countered = false;
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_VOICE.get(), SoundSource.HOSTILE, 2.5f, 0.7f);
                }
                if (t % 3 == 0) Vfx.ring(level, ModParticles.GLOAM_WISP.get(), position().add(0, 0.2, 0), 1.6, 16, 0.08);
                if (t > 50) endMove(30);
            }
            case BLADES -> {
                if (t == 1 && target != null) {
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.BLADE_CROWN.get(), SoundSource.HOSTILE, 3.0f, 0.8f);
                    for (int i = 0; i < 6; i++) CrownBladeEntity.summon(level, this, target, i, 40 + i * 8, 9f);
                }
                if (t > 100) endMove(40);
            }
            case PILLARS -> pillars(level, target, t);
            case FORSWORN -> {
                if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_VOICE.get(), SoundSource.HOSTILE, 3.0f, 0.5f);
                if (t == 25) summonKnights(level, target);
                if (t > 35) endMove(40);
            }
            case TRANSITION -> transition(level, t);
            case BOLTS -> {
                if (target != null && t % 10 == 0 && t <= 50) {
                    GloamBoltEntity.shoot(level, this, position().add(0, 2.4, 0), target, 7f);
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.ARCANE_ORB.get(), SoundSource.HOSTILE, 1.5f, 0.5f);
                }
                if (t > 60) endMove(20);
            }
            case SHADOWSTEP -> {
                if (t == 1) shadowstep(level, target);
                if (t == 12 && target != null) {
                    for (int i = 0; i < 2; i++) {
                        var g = ModEntities.GLOAMLING.get().create(level, EntitySpawnReason.MOB_SUMMONED);
                        if (g == null) continue;
                        double a = random.nextDouble() * Math.PI * 2;
                        g.snapTo(getX() + Math.cos(a) * 2, getY(), getZ() + Math.sin(a) * 2, 0, 0);
                        g.setTarget(target);
                        level.addFreshEntity(g);
                    }
                }
                if (t > 20) endMove(30);
            }
            case UNVEILED -> {
                getNavigation().stop();
                setDeltaMovement(0, getDeltaMovement().y, 0);
                if (t % 4 == 0) Vfx.burst(level, ModParticles.SUNBURST.get(), position().add(0, 2.6, 0), 4, 0.5, 0.05);
                if (t > 200) {
                    // the dark returns: two lanterns fail
                    List<BlockPos> ls = new ArrayList<>(lanterns(level));
                    java.util.Collections.shuffle(ls, new java.util.Random(random.nextLong()));
                    for (int i = 0; i < Math.min(2, ls.size()); i++) WardLanternBlock.snuff(level, ls.get(i));
                    entityData.set(HOLLOW, true);
                    level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_VOICE.get(), SoundSource.HOSTILE, 3.0f, 0.6f);
                    endMove(20);
                }
            }
            default -> endMove(20);
        }
        if (isHollow() && tickCount % 20 == 0) checkUnveil(level);
        if (isHollow() && tickCount % 40 == 0) {
            for (Player p : challengers(level, 40)) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, false, false));
        }
    }

    /** Small helper: a guttering-lantern plume. */
    private static void plume(ServerLevel level, BlockPos p) {
        Vfx.column(level, ModParticles.GLOAM_WISP.get(), Vec3.atBottomCenterOf(p), 4, 20);
    }

    private void chooseMove(LivingEntity target) {
        List<Integer> opts = new ArrayList<>();
        double d = distanceToSqr(target);
        switch (phase()) {
            case 1 -> {
                if (d < 4.5 * 4.5) {
                    opts.add(COMBO);
                    opts.add(COMBO);
                }
                opts.add(LUNGE);
                opts.add(RUIN);
            }
            case 2 -> {
                opts.add(BLADES);
                opts.add(PILLARS);
                opts.add(PILLARS);
                opts.add(LUNGE);
                if (knights.size() < 3) opts.add(FORSWORN);
            }
            default -> {
                if (isHollow()) {
                    opts.add(BOLTS);
                    opts.add(BOLTS);
                    opts.add(SHADOWSTEP);
                } else {
                    opts.add(PILLARS);
                    opts.add(COMBO);
                }
            }
        }
        opts.remove(Integer.valueOf(lastMove));
        if (opts.isEmpty()) opts.add(PILLARS);
        int pick = opts.get(random.nextInt(opts.size()));
        lastMove = pick;
        startMove(pick);
    }

    private void updatePhase(ServerLevel level) {
        if (move() == RISING) return;
        float f = getHealth() / getMaxHealth();
        int want = f <= 0.25f ? 3 : f <= 0.6f ? 2 : 1;
        if (want > phase()) {
            entityData.set(PHASE, want);
            startMove(TRANSITION);
            bar.setColor(want == 3 ? BossEvent.BossBarColor.WHITE : BossEvent.BossBarColor.RED);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(64))) {
                p.sendSystemMessage(Component.translatable("message.oathbound.morvane.phase" + want).withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
            }
        }
    }

    private void transition(ServerLevel level, int t) {
        getNavigation().stop();
        Vec3 c = position().add(0, 1.6, 0);
        if (t == 1) level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_ROAR.get(), SoundSource.HOSTILE, 5.0f, phase() == 3 ? 0.6f : 0.9f);
        Vfx.spiralIn(level, ModParticles.GLOAM_WISP.get(), c, 7, 10, t);
        if (phase() == 2 && t < 40) setDeltaMovement(0, 0.08, 0);
        if (phase() == 3) {
            List<BlockPos> ls = lanterns(level);
            if (t % 10 == 0 && t / 10 - 1 < ls.size() && t >= 10) WardLanternBlock.snuff(level, ls.get(t / 10 - 1));
        }
        if (t == 50) {
            Vfx.sphere(level, ModParticles.GLOAM_WISP.get(), c, 6, 200);
            for (Player p : challengers(level, 10)) {
                p.setDeltaMovement(p.position().subtract(position()).normalize().scale(1.4).add(0, 0.6, 0));
                p.hurtMarked = true;
            }
            if (phase() == 3 && !lanterns(level).isEmpty()) {
                entityData.set(HOLLOW, true);
                teleportTo(home().getX() + 0.5, home().getY() + 1, home().getZ() + 0.5);
            }
        }
        if (t > 60) endMove(20);
    }

    private void hoverOver(LivingEntity target) {
        if (target == null || move() == LUNGE) return;
        double a = tickCount * 0.02;
        Vec3 want = target.position().add(Math.cos(a) * 7, 4.5, Math.sin(a) * 7);
        Vec3 c = Vec3.atBottomCenterOf(home());
        Vec3 flat = want.subtract(c).multiply(1, 0, 1);
        if (flat.length() > 13) want = c.add(flat.normalize().scale(13)).add(0, want.y - c.y, 0);
        Vec3 d = want.subtract(position());
        setDeltaMovement(getDeltaMovement().scale(0.8).add(d.scale(0.03)));
    }

    private void combo(ServerLevel level, LivingEntity target, int t) {
        if (target != null) getNavigation().moveTo(target, 0.6);
        if (t == 10 || t == 22 || t == 38) {
            float dmg = t == 38 ? 15f : 10f;
            Vec3 fwd = Vec3.directionFromRotation(0, getYRot());
            level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_SLASH.get(), SoundSource.HOSTILE, 2.0f, t == 38 ? 0.6f : 0.9f);
            for (int i = -2; i <= 2; i++) {
                Vfx.burst(level, ParticleTypes.SWEEP_ATTACK, position().add(fwd.yRot(i * 0.4f).scale(3)).add(0, 1.6, 0), 1, 0, 0);
            }
            Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(fwd.scale(2.5)).add(0, 1.4, 0), 20, 0.8, 0.1);
            for (Player p : challengers(level, 4.5)) {
                Vec3 to = p.position().subtract(position()).multiply(1, 0, 1).normalize();
                if (to.dot(fwd) > 0 && p.distanceTo(this) < 4.6) {
                    p.hurtServer(level, damageSources().mobAttack(this), dmg);
                    if (t == 38) {
                        p.setDeltaMovement(to.scale(1.3).add(0, 0.5, 0));
                        p.hurtMarked = true;
                    }
                }
            }
        }
        if (t > 50) endMove(25 + random.nextInt(15));
    }

    private void lunge(ServerLevel level, LivingEntity target, int t) {
        getNavigation().stop();
        if (t == 1 && target != null) {
            lungeDir = target.position().add(0, 0.5, 0).subtract(position()).normalize();
            level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_VOICE.get(), SoundSource.HOSTILE, 2.0f, 1.3f);
        }
        if (t < 14) {
            Vfx.line(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1, 0), position().add(0, 1, 0).add(lungeDir.scale(14)), 0.8);
        } else if (t < 24) {
            setDeltaMovement(lungeDir.scale(1.5));
            hurtMarked = true;
            Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.2, 0), 8, 0.4, 0.02);
            for (Player p : challengers(level, 1.8)) {
                p.hurtServer(level, damageSources().mobAttack(this), 12f);
                p.addEffect(new MobEffectInstance(com.oathbound.registry.ModEffects.holder(com.oathbound.registry.ModEffects.GLOAMROT), 80, 0));
            }
        } else {
            setDeltaMovement(getDeltaMovement().scale(0.3));
            endMove(35 + random.nextInt(15));
        }
    }

    private void pillars(ServerLevel level, LivingEntity target, int t) {
        if (t == 1) {
            pillars.clear();
            if (target != null) {
                pillars.add(target.position());
                for (int i = 0; i < 5; i++) {
                    double a = random.nextDouble() * Math.PI * 2, r = 2 + random.nextDouble() * 5;
                    pillars.add(target.position().add(Math.cos(a) * r, 0, Math.sin(a) * r));
                }
            }
            level.playSound(null, getX(), getY(), getZ(), ModSounds.MORVANE_VOICE.get(), SoundSource.HOSTILE, 2.5f, 0.8f);
        }
        if (t < 26 && t % 2 == 0) {
            for (Vec3 p : pillars) Vfx.ring(level, ModParticles.GLOAM_WISP.get(), p.add(0, 0.1, 0), 1.6, 12, 0.0);
        }
        if (t == 26) {
            for (Vec3 p : pillars) {
                level.playSound(null, p.x, p.y, p.z, ModSounds.ECLIPSE_PILLAR.get(), SoundSource.HOSTILE, 2.0f, 0.8f + random.nextFloat() * 0.4f);
                Vfx.column(level, ModParticles.GLOAM_WISP.get(), p, 9, 50);
                Vfx.column(level, ParticleTypes.REVERSE_PORTAL, p, 7, 30);
                for (Player pl : challengers(level, 40)) {
                    if (pl.position().multiply(1, 0, 1).distanceTo(p.multiply(1, 0, 1)) < 1.7 && Math.abs(pl.getY() - p.y) < 3) {
                        pl.hurtServer(level, damageSources().indirectMagic(this, this), 13f);
                        pl.setDeltaMovement(pl.getDeltaMovement().add(0, 1.0, 0));
                        pl.hurtMarked = true;
                    }
                }
            }
        }
        if (t > 40) endMove(40);
    }

    private void summonKnights(ServerLevel level, LivingEntity target) {
        knights.removeIf(id -> {
            Entity e = level.getEntity(id);
            return e == null || !e.isAlive();
        });
        for (int i = 0; i < 2; i++) {
            ForswornKnightEntity k = ModEntities.FORSWORN_KNIGHT.get().create(level, EntitySpawnReason.MOB_SUMMONED);
            if (k == null) continue;
            double a = random.nextDouble() * Math.PI * 2;
            BlockPos h = home();
            k.snapTo(h.getX() + 0.5 + Math.cos(a) * 8, h.getY() + 1, h.getZ() + 0.5 + Math.sin(a) * 8, random.nextFloat() * 360, 0);
            k.setTarget(target);
            k.setPersistenceRequired();
            level.addFreshEntity(k);
            knights.add(k.getUUID());
            Vfx.column(level, ModParticles.GLOAM_WISP.get(), k.position(), 3, 40);
        }
    }

    private void shadowstep(ServerLevel level, LivingEntity target) {
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.5, 0), 50, 0.6, 0.1);
        double a = random.nextDouble() * Math.PI * 2, r = 5 + random.nextDouble() * 7;
        BlockPos h = home();
        teleportTo(h.getX() + 0.5 + Math.cos(a) * r, h.getY() + 1, h.getZ() + 0.5 + Math.sin(a) * r);
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.5, 0), 50, 0.6, 0.1);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.VEYL_BLINK.get(), SoundSource.HOSTILE, 2.0f, 0.5f);
    }

    /** A Ward Lantern was relit near the throne. */
    public void onLanternLit(ServerLevel level, BlockPos lantern, Player by) {
        if (!isHollow()) return;
        Vec3 from = Vec3.atCenterOf(lantern).add(0, 0.5, 0);
        Vfx.line(level, ModParticles.SUNBURST.get(), from, position().add(0, 1.8, 0), 0.4);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.UNVEILED.get(), SoundSource.HOSTILE, 1.5f, 1.6f);
        super.hurtServer(level, by != null ? damageSources().indirectMagic(by, by) : damageSources().magic(), 10f);
        checkUnveil(level);
    }

    private boolean allLit(ServerLevel level) {
        List<BlockPos> ls = lanterns(level);
        if (ls.isEmpty()) return true;
        for (BlockPos p : ls) if (!level.getBlockState(p).getValue(WardLanternBlock.LIT)) return false;
        return true;
    }

    private void checkUnveil(ServerLevel level) {
        if (isHollow() && move() != TRANSITION && allLit(level)) {
            entityData.set(HOLLOW, false);
            startMove(UNVEILED);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.UNVEILED.get(), SoundSource.HOSTILE, 4.0f, 0.8f);
            Vfx.sphere(level, ModParticles.SUNBURST.get(), position().add(0, 1.6, 0), 3.5, 140);
            for (BlockPos p : lanterns(level)) Vfx.line(level, ModParticles.SUNBURST.get(), Vec3.atCenterOf(p).add(0, 0.5, 0), position().add(0, 1.8, 0), 0.3);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(40))) {
                p.sendOverlayMessage(Component.translatable("message.oathbound.morvane.unveiled").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
                p.removeEffect(MobEffects.DARKNESS);
            }
        }
    }

    // ------------------------------------------------------------------ damage & death
    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
        if (isSleeping() || move() == RISING || move() == TRANSITION) return false;
        if (isHollow()) {
            if (source.getEntity() instanceof Player p) {
                p.sendOverlayMessage(Component.translatable("message.oathbound.morvane.hollow").withStyle(ChatFormatting.DARK_PURPLE));
                Vfx.burst(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.6, 0), 12, 0.5, 0.05);
            }
            return false;
        }
        if (source.getEntity() instanceof ForswornKnightEntity || source.getDirectEntity() instanceof CrownBladeEntity) return false;
        if (move() == RUIN && !countered) {
            if (source.getDirectEntity() instanceof Projectile) {
                countered = true;
                endMove(10);
                level.playSound(null, getX(), getY(), getZ(), ModSounds.SHIELD_BLOCK.get(), SoundSource.HOSTILE, 2.0f, 0.5f);
                Vfx.burst(level, ModParticles.SUNBURST.get(), position().add(0, 1.8, 0), 30, 0.5, 0.2);
                return super.hurtServer(level, source, amount * 1.5f);
            }
            if (source.getEntity() instanceof Player p && source.getDirectEntity() == p) {
                countered = true;
                level.playSound(null, getX(), getY(), getZ(), ModSounds.BOSS_SLASH.get(), SoundSource.HOSTILE, 2.5f, 0.5f);
                Vfx.line(level, ModParticles.GLOAM_WISP.get(), position().add(0, 1.6, 0), p.position().add(0, 1, 0), 0.2);
                p.hurtServer(level, damageSources().mobAttack(this), 16f);
                p.setDeltaMovement(p.position().subtract(position()).normalize().scale(1.6).add(0, 0.5, 0));
                p.hurtMarked = true;
                endMove(20);
                return false;
            }
        }
        if (move() == UNVEILED) amount *= 1.5f;
        return super.hurtServer(level, source, amount);
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (level() instanceof ServerLevel level) {
            entityData.set(HOLLOW, false);
            sealArena(level, false);
            for (UUID id : knights) {
                Entity e = level.getEntity(id);
                if (e != null) e.discard();
            }
            for (BlockPos p : lanterns(level)) WardLanternBlock.relight(level, p);
            level.playSound(null, getX(), getY(), getZ(), ModSounds.CROWN_SHATTER.get(), SoundSource.HOSTILE, 6.0f, 1.0f);
        }
    }

    @Override
    protected void tickDeath() {
        deathTime++;
        setDeltaMovement(0, 0.03, 0);
        if (level() instanceof ServerLevel level) {
            Vec3 c = position().add(0, 2.4, 0);
            for (int i = 0; i < 3; i++) {
                double a = random.nextDouble() * Math.PI * 2, b = (random.nextDouble() - 0.3) * Math.PI / 2;
                Vec3 dir = new Vec3(Math.cos(a) * Math.cos(b), Math.sin(b), Math.sin(a) * Math.cos(b));
                Vfx.line(level, ModParticles.SUNBURST.get(), c, c.add(dir.scale(6 + deathTime * 0.12)), 0.6);
            }
            if (deathTime % 10 == 0) Vfx.burst(level, ModParticles.GLOAM_WISP.get(), c, 30, 1.0, 0.15);
            if (deathTime == 110) {
                Vfx.sphere(level, ModParticles.SUNBURST.get(), c, 10, 400);
                Vfx.burst(level, ModParticles.SUNBURST.get(), c, 40, 0.3, 0.3);
                ExperienceOrb.award(level, c, 1500);
                level.playSound(null, getX(), getY(), getZ(), ModSounds.DAWN_BURST.get(), SoundSource.HOSTILE, 6.0f, 0.7f);
                remove(RemovalReason.KILLED);
            }
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!level().isClientSide()) return;
        if (isSleeping()) {
            if (random.nextInt(4) == 0) level().addParticle(ModParticles.GLOAM_WISP.get(), getRandomX(1.0), getY() + 2.4 + random.nextDouble(), getRandomZ(1.0), 0, 0.02, 0);
            return;
        }
        int n = isHollow() ? 4 : 1;
        for (int i = 0; i < n; i++) {
            level().addParticle(ModParticles.GLOAM_WISP.get(), getRandomX(1.0), getY() + random.nextDouble() * 3.2, getRandomZ(1.0), 0, 0.02, 0);
        }
        // the crown burns
        level().addParticle(phase() >= 2 ? ModParticles.SUNBURST.get() : ModParticles.EMBER.get(), getX() + (random.nextDouble() - 0.5) * 0.6, getY() + 3.45, getZ() + (random.nextDouble() - 0.5) * 0.6, 0, 0.03, 0);
        if (move() == RUIN) level().addParticle(ModParticles.GLOAM_WISP.get(), getRandomX(0.4), getY() + 1.5, getRandomZ(0.4), 0, 0.1, 0);
    }

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSleeping() ? null : ModSounds.MORVANE_VOICE.get();
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
    public float getVoicePitch() {
        return 0.55f;
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putInt("Phase", phase());
        out.putBoolean("Hollow", isHollow());
        if (home != null) out.putIntArray("Home", new int[]{home.getX(), home.getY(), home.getZ()});
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        entityData.set(PHASE, in.getIntOr("Phase", 1));
        entityData.set(HOLLOW, in.getBooleanOr("Hollow", false));
        in.getIntArray("Home").ifPresent(a -> {
            if (a.length == 3) home = new BlockPos(a[0], a[1], a[2]);
        });
    }

    public float yawTo(Vec3 p) {
        return (float) (Mth.atan2(p.z - getZ(), p.x - getX()) * Mth.RAD_TO_DEG) - 90f;
    }
}
