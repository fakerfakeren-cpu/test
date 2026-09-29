package com.oathbound.event;

import com.oathbound.block.SunderedKeystoneBlock;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * The rite of the Sundered Gate. Turning the Oathkey in the keystone calls the three seals home one after
 * another (Valor, Wisdom, Sacrifice), each as a coloured beam into the arch, until the Gloam tears open and a
 * living veil fills the gate.
 * <p>Gate geometry (fixed by the Citadel blueprint): the keystone is the centre of the bottom row of a frame in
 * the X/Y plane; the opening is x-2..x+2, y+1..y+7 at the keystone's z.
 */
public final class GateRite {
    public static final int DURATION = 110;

    private static final class Rite {
        final BlockPos pos;
        int t;

        Rite(BlockPos pos) {
            this.pos = pos;
        }
    }

    private static final List<Rite> RITES = new ArrayList<>();

    private GateRite() {}

    public static boolean isRunning(ServerLevel level, BlockPos pos) {
        for (Rite r : RITES) if (r.pos.equals(pos)) return true;
        return false;
    }

    public static void begin(ServerLevel level, BlockPos keystone, net.minecraft.world.entity.player.Player player) {
        RITES.add(new Rite(keystone.immutable()));
        level.playSound(null, keystone, ModSounds.GATE_HUM.get(), SoundSource.BLOCKS, 3.0f, 0.6f);
        player.sendSystemMessage(Component.translatable("message.oathbound.gate.begin").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.ITALIC));
    }

    public static void tick(ServerLevel level) {
        Iterator<Rite> it = RITES.iterator();
        while (it.hasNext()) {
            Rite r = it.next();
            if (!level.getBlockState(r.pos).is(ModBlocks.SUNDERED_KEYSTONE.get())) {
                it.remove();
                continue;
            }
            r.t++;
            step(level, r.pos, r.t);
            if (r.t >= DURATION) it.remove();
        }
    }

    private static Vec3 center(BlockPos k) {
        return new Vec3(k.getX() + 0.5, k.getY() + 4.5, k.getZ() + 0.5);
    }

    private static void step(ServerLevel level, BlockPos k, int t) {
        Vec3 c = center(k);
        Vec3[] sconces = {new Vec3(k.getX() - 3 + 0.5, k.getY() + 9.2, k.getZ() + 0.5), new Vec3(k.getX() + 0.5, k.getY() + 10.2, k.getZ() + 0.5),
            new Vec3(k.getX() + 3 + 0.5, k.getY() + 9.2, k.getZ() + 0.5)};
        ParticleOptions[] colors = {ModParticles.TIDE.get(), ModParticles.ARCANE_GLYPH.get(), ModParticles.SPIRIT.get()};
        for (int i = 0; i < 3; i++) {
            int start = 10 + i * 20;
            if (t == start) {
                level.playSound(null, k, ModSounds.bell(i + 1), SoundSource.BLOCKS, 3.0f, 0.8f);
                Vfx.burst(level, colors[i], sconces[i], 40, 0.3, 0.1);
            }
            if (t >= start && t < DURATION - 10 && t % 2 == 0) Vfx.line(level, colors[i], sconces[i], c, 0.5);
        }
        if (t > 60 && t < DURATION) Vfx.spiralIn(level, ModParticles.GLOAM_WISP.get(), c, 5.0, 10, t);
        if (t == 70) level.playSound(null, k, ModSounds.GATE_OPEN.get(), SoundSource.BLOCKS, 4.0f, 0.8f);
        if (t == DURATION - 1) {
            openNow(level, k);
            for (int i = 0; i < 2; i++) {
                LightningBolt bolt = net.minecraft.world.entity.EntityTypes.LIGHTNING_BOLT.create(level, EntitySpawnReason.EVENT);
                if (bolt == null) continue;
                bolt.setVisualOnly(true);
                bolt.snapTo(k.getX() + (i == 0 ? -3 : 4), k.getY() + 9, k.getZ() + 0.5, 0, 0);
                level.addFreshEntity(bolt);
            }
            Vfx.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 1, 0, 0);
            Vfx.sphere(level, ModParticles.GLOAM_WISP.get(), c, 5, 160);
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(k).inflate(40))) {
                QuestLog.grant(p, "gate", "opened");
                GloamingTravel.title(p, Component.translatable("title.oathbound.gate").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD),
                    Component.translatable("title.oathbound.gate.sub").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            }
        }
    }

    /** Fills the gate with veil and marks the keystone active (also used by commands and the self-test). */
    public static int openNow(ServerLevel level, BlockPos k) {
        BlockState ks = level.getBlockState(k);
        if (ks.is(ModBlocks.SUNDERED_KEYSTONE.get())) level.setBlock(k, ks.setValue(SunderedKeystoneBlock.ACTIVE, true), 3);
        int n = 0;
        for (int dx = -2; dx <= 2; dx++) {
            for (int dy = 1; dy <= 7; dy++) {
                BlockPos p = k.offset(dx, dy, 0);
                BlockState s = level.getBlockState(p);
                if (s.isAir() || s.canBeReplaced()) {
                    level.setBlock(p, ModBlocks.GLOAM_VEIL.get().defaultBlockState(), 2);
                    n++;
                }
            }
        }
        return n;
    }

    /** Clears the veil (unused in play; the gate stays open once opened). */
    public static void close(ServerLevel level, BlockPos k) {
        for (int dx = -2; dx <= 2; dx++)
            for (int dy = 1; dy <= 7; dy++)
                if (level.getBlockState(k.offset(dx, dy, 0)).is(ModBlocks.GLOAM_VEIL.get())) level.setBlock(k.offset(dx, dy, 0), Blocks.AIR.defaultBlockState(), 2);
    }
}
