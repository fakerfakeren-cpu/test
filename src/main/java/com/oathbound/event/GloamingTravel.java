package com.oathbound.event;

import com.oathbound.entity.boss.MorvaneEntity;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModWorldgen;
import com.oathbound.util.Vfx;
import com.oathbound.world.SketchPlacer;
import com.oathbound.world.Sketches;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;

/**
 * Crossing between the overworld and the Gloaming. The Hollow Throne is raised around (0, {@link #ARENA_Y}, 0)
 * the first time anyone crosses; its arrival causeway and return veil lie to the south.
 */
public final class GloamingTravel {
    public static final int ARENA_Y = 70;
    public static final BlockPos THRONE = new BlockPos(0, ARENA_Y, 0);
    /** Where travellers step out of the veil, facing the throne (north). */
    public static final Vec3 ARRIVAL = new Vec3(0.5, ARENA_Y + 1, 46.5);

    private GloamingTravel() {}

    /** Builds the throne arena (once per world) and wakes nothing: Morvane sits dormant until challenged. */
    public static void ensureThrone(ServerLevel gloaming) {
        if (gloaming.getBlockState(THRONE.below()).is(ModBlocks.CHISELED_WARDSTONE.get())) return;
        SketchPlacer.placeNow(gloaming, Sketches.draw(Sketches.Type.THRONE, 0x5EED0F7L), THRONE);
        MorvaneEntity king = ModEntities.MORVANE.get().create(gloaming, EntitySpawnReason.STRUCTURE);
        if (king != null) {
            king.snapTo(0.5, ARENA_Y + 2.5, -12.4, 0f, 0f);
            king.setHome(THRONE);
            gloaming.addFreshEntity(king);
        }
    }

    public static void toGloaming(ServerPlayer player, BlockPos gate) {
        ServerLevel gloaming = player.level().getServer().getLevel(ModWorldgen.GLOAMING);
        if (gloaming == null) {
            player.sendSystemMessage(Component.translatable("message.oathbound.gloaming.missing").withStyle(ChatFormatting.RED));
            return;
        }
        CompoundTag root = player.getPersistentData();
        CompoundTag persisted = root.getCompoundOrEmpty("PlayerPersisted");
        persisted.putIntArray("oathbound_gate", new int[]{gate.getX(), gate.getY(), gate.getZ()});
        root.put("PlayerPersisted", persisted);
        ensureThrone(gloaming);
        player.teleport(new TeleportTransition(gloaming, ARRIVAL, Vec3.ZERO, 180f, 0f, TeleportTransition.DO_NOTHING));
        gloaming.playSound(null, ARRIVAL.x, ARRIVAL.y, ARRIVAL.z, ModSounds.GATE_OPEN.get(), SoundSource.PLAYERS, 1.5f, 0.7f);
        Vfx.burst(gloaming, ModParticles.GLOAM_WISP.get(), ARRIVAL.add(0, 1, 0), 60, 0.6, 0.08);
        title(player, Component.translatable("title.oathbound.gloaming").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD),
            Component.translatable("title.oathbound.gloaming.sub").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
    }

    public static void toOverworld(ServerPlayer player) {
        ServerLevel overworld = player.level().getServer().overworld();
        int[] g = player.getPersistentData().getCompoundOrEmpty("PlayerPersisted").getIntArray("oathbound_gate").orElse(new int[0]);
        TeleportTransition t;
        if (g.length == 3) {
            Vec3 at = new Vec3(g[0] + 0.5, g[1], g[2] + 3.5);
            t = new TeleportTransition(overworld, at, Vec3.ZERO, 0f, 0f, TeleportTransition.DO_NOTHING);
        } else {
            t = TeleportTransition.createDefault(player, TeleportTransition.DO_NOTHING);
        }
        player.teleport(t);
        overworld.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.GATE_OPEN.get(), SoundSource.PLAYERS, 1.2f, 1.2f);
    }

    public static void title(ServerPlayer p, Component title, Component subtitle) {
        p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 70, 20));
        p.connection.send(new ClientboundSetSubtitleTextPacket(subtitle));
        p.connection.send(new ClientboundSetTitleTextPacket(title));
    }
}
