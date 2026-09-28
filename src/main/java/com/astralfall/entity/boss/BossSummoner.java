package com.astralfall.entity.boss;

import com.astralfall.event.Starfall;
import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;

/**
 * The Eclipse ritual. Night falls instantly, starlight is drawn into the altar, the sky cracks with
 * lightning and a colossal meteor crashes down. Astraeus rises from the impact.
 */
public final class BossSummoner {
    private static final int DURATION = 150;
    private static final Map<ResourceKey<Level>, Ritual> RITUALS = new HashMap<>();

    private record Ritual(BlockPos pos, int[] ticks) {}

    private BossSummoner() {}

    public static boolean isRitualActive(ServerLevel level) {
        return RITUALS.containsKey(level.dimension());
    }

    public static void begin(ServerLevel level, BlockPos pos) {
        if (isRitualActive(level)) return;
        RITUALS.put(level.dimension(), new Ritual(pos, new int[]{0}));
        if (!level.isDarkOutside()) {
            level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withSuppressedOutput(), "time set minecraft:midnight");
        }
        level.playSound(null, pos, ModSounds.BOSS_SUMMON.get(), SoundSource.HOSTILE, 6.0f, 1.0f);
        for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(pos).inflate(128))) {
            p.sendSystemMessage(Component.translatable("message.astralfall.ritual.begin").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
            Starfall.title(p, Component.translatable("title.astralfall.eclipse").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD),
                Component.translatable("title.astralfall.eclipse.sub").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        }
    }

    public static void tick(ServerLevel level) {
        Ritual r = RITUALS.get(level.dimension());
        if (r == null) return;
        int t = ++r.ticks()[0];
        BlockPos pos = r.pos();
        Vec3 c = Vec3.atCenterOf(pos).add(0, 1, 0);

        FX.spiralIn(level, ModParticles.STAR_SPARKLE.get(), c, 8 - t * 0.03, 6, t);
        if (t % 3 == 0) FX.spiralIn(level, ModParticles.VOID_MOTE.get(), c, 12, 6, -t);
        if (t % 20 == 0 && t < 110) {
            double a = level.getRandom().nextDouble() * Math.PI * 2;
            double d = 10 + level.getRandom().nextDouble() * 14;
            LightningBolt bolt = net.minecraft.world.entity.EntityTypes.LIGHTNING_BOLT.create(level, EntitySpawnReason.EVENT);
            if (bolt != null) {
                bolt.snapTo(c.x + Math.cos(a) * d, c.y - 1, c.z + Math.sin(a) * d);
                bolt.setVisualOnly(true);
                level.addFreshEntity(bolt);
            }
            level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.HOSTILE, 3.0f, 0.5f + t / 200f);
        }
        if (t == 40) {
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(pos).inflate(64))) {
                p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 100, 0));
            }
        }
        if (t == 80) {
            FX.burst(level, ParticleTypes.END_ROD, c, 80, 0.2, 0.6);
            Starfall.spawnMeteor(level, pos, Starfall.Variant.BOSS, 4.0f);
        }
        if (t == 118) {
            AstraeusEntity boss = ModEntities.ASTRAEUS.get().create(level, EntitySpawnReason.EVENT);
            if (boss != null) {
                boss.snapTo(c.x, c.y - 4.5, c.z, level.getRandom().nextFloat() * 360f, 0f);
                boss.beginEmerging(pos);
                level.addFreshEntity(boss);
            }
        }
        if (t >= DURATION) RITUALS.remove(level.dimension());
    }
}
