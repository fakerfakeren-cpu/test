package com.oathbound.entity.npc;

import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

/**
 * When the Lanternguard's pilgrims come: often soon after someone kindles a wayshrine, now and then on the road.
 * Never more than one near a player, and each moves on after a day.
 */
public final class PilgrimVisits {
    private static final int STAY = 24000;

    private PilgrimVisits() {}

    private static boolean onePresent(ServerLevel level, BlockPos near, int radius) {
        return !level.getEntitiesOfClass(LanternguardPilgrimEntity.class, new AABB(near).inflate(radius)).isEmpty();
    }

    /** Spawns a pilgrim walking in toward {@code toward}; returns it, or null if there was nowhere to stand. */
    public static LanternguardPilgrimEntity arrive(ServerLevel level, BlockPos toward, int min, int max) {
        BlockPos at = LanternguardPilgrimEntity.standingNear(level, toward, level.getRandom(), min, max);
        if (at == null) return null;
        LanternguardPilgrimEntity p = ModEntities.LANTERNGUARD_PILGRIM.get().create(level, EntitySpawnReason.EVENT);
        if (p == null) return null;
        p.snapTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, level.getRandom().nextFloat() * 360, 0);
        p.setDespawnDelay(STAY);
        p.setWanderTarget(toward);
        level.addFreshEntity(p);
        Vfx.column(level, ModParticles.LUMEN_MOTE.get(), p.position(), 2.2, 24);
        return p;
    }

    /** A wayshrine was just kindled or warmed at. */
    public static void atWayshrine(ServerLevel level, BlockPos shrine, ServerPlayer by) {
        if (level.dimension() != Level.OVERWORLD || onePresent(level, shrine, 96)) return;
        if (level.getRandom().nextFloat() > 0.35f) return;
        if (arrive(level, shrine, 10, 20) != null) {
            by.sendSystemMessage(Component.translatable("message.oathbound.pilgrim.coming").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
        }
    }

    /** Every few minutes: a small chance that a pilgrim is on the road near each player. */
    public static void tick(ServerLevel level) {
        if (level.dimension() != Level.OVERWORLD || level.getGameTime() % 3600 != 0 || !level.isBrightOutside()) return;
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator() || level.getRandom().nextFloat() > 0.12f || onePresent(level, p.blockPosition(), 96)) continue;
            arrive(level, p.blockPosition(), 20, 32);
        }
    }
}
