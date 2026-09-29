package com.rimeheart.entity.boss;

import com.rimeheart.registry.ModEntities;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.util.FX;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;

/**
 * The Winter Horn ritual: the horn's note calls a blizzard that spirals into the altar, the ground
 * cracks with frost, and the Frost Sovereign rises out of the ice.
 */
public final class SovereignRitual {
    private static final int DURATION = 120;
    private static final Map<ResourceKey<Level>, Ritual> RITUALS = new HashMap<>();

    private record Ritual(BlockPos pos, int[] ticks) {}

    private SovereignRitual() {}

    public static boolean isActive(ServerLevel level) {
        return RITUALS.containsKey(level.dimension());
    }

    public static void title(ServerPlayer p, Component title, Component subtitle) {
        p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 60, 20));
        p.connection.send(new ClientboundSetSubtitleTextPacket(subtitle));
        p.connection.send(new ClientboundSetTitleTextPacket(title));
    }

    public static void begin(ServerLevel level, BlockPos pos) {
        if (isActive(level)) return;
        RITUALS.put(level.dimension(), new Ritual(pos, new int[]{0}));
        level.playSound(null, pos, ModSounds.WINTER_HORN.get(), SoundSource.HOSTILE, 6.0f, 0.8f);
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(128))) {
            p.sendSystemMessage(Component.translatable("message.rimeheart.ritual.begin").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
            title(p, Component.translatable("title.rimeheart.ritual").withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD),
                Component.translatable("title.rimeheart.ritual.sub").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        }
    }

    public static void tick(ServerLevel level) {
        Ritual r = RITUALS.get(level.dimension());
        if (r == null) return;
        int t = ++r.ticks()[0];
        BlockPos pos = r.pos();
        Vec3 c = Vec3.atCenterOf(pos).add(0, 1, 0);
        FX.spiralIn(level, ParticleTypes.SNOWFLAKE, c, 10 - t * 0.05, 10, t);
        if (t % 2 == 0) FX.spiralIn(level, ModParticles.SNOW_PUFF.get(), c, 14, 6, -t);
        if (t % 4 == 0) FX.ring(level, ModParticles.FROST_GLINT.get(), c.add(0, -0.9, 0), 1 + (t % 40) * 0.2, 24, 0.02);
        if (t % 30 == 0) level.playSound(null, pos, ModSounds.BLIZZARD.get(), SoundSource.HOSTILE, 3.0f, 0.6f + t / 300f);
        if (t == 50) {
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(48))) {
                p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 0));
            }
        }
        if (t == 90) {
            FrostSovereignEntity boss = ModEntities.FROST_SOVEREIGN.get().create(level, EntitySpawnReason.EVENT);
            if (boss != null) {
                boss.snapTo(c.x + 4, c.y - 5.5, c.z, level.getRandom().nextFloat() * 360f, 0f);
                boss.beginEmerging(pos);
                level.addFreshEntity(boss);
            }
        }
        if (t >= DURATION) RITUALS.remove(level.dimension());
    }
}
