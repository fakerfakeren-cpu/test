package com.astralfall.event;

import com.astralfall.Config;
import com.astralfall.entity.MeteorEntity;
import com.astralfall.entity.mob.AstralWispEntity;
import com.astralfall.entity.mob.MeteoriteCrawlerEntity;
import com.astralfall.registry.ModBlocks;
import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
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
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;

/**
 * The Starfall: meteors rain down near players at night. One night in a while becomes a
 * Starstorm, with meteors every few seconds and the sky full of shooting stars.
 */
public final class Starfall {
    public enum Variant { NORMAL, FALLEN_STAR, CRAWLER, SMALL, SHOOTING_STAR, BOSS }

    private static final class LevelState {
        boolean wasNight;
        boolean storm;
        int stormTicks;
    }

    private static final Map<ResourceKey<Level>, LevelState> STATES = new HashMap<>();

    private Starfall() {}

    public static boolean isStarstorm(ServerLevel level) {
        LevelState st = STATES.get(level.dimension());
        return st != null && st.storm;
    }

    public static void tick(ServerLevel level) {
        if (level.dimension() != Level.OVERWORLD) return;
        LevelState st = STATES.computeIfAbsent(level.dimension(), k -> new LevelState());
        RandomSource rand = level.getRandom();
        boolean night = level.isDarkOutside();
        if (night && !st.wasNight && !st.storm) {
            int chance = Config.starstormChance();
            if (chance > 0 && rand.nextInt(chance) == 0) startStarstorm(level, 0);
        }
        if (!night && st.wasNight && st.storm && st.stormTicks <= 0) endStarstorm(level);
        st.wasNight = night;
        if (st.storm && st.stormTicks > 0 && --st.stormTicks == 0) endStarstorm(level);

        if (!st.storm && (!night || !Config.meteorShowers())) return;
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator()) continue;
            int chance = st.storm ? 70 : Config.meteorChance();
            if (rand.nextInt(chance) == 0) {
                double angle = rand.nextDouble() * Math.PI * 2;
                double dist = 20 + rand.nextDouble() * 52;
                BlockPos target = BlockPos.containing(p.getX() + Math.cos(angle) * dist, p.getY(), p.getZ() + Math.sin(angle) * dist);
                if (!level.isLoaded(target)) continue;
                int roll = rand.nextInt(100);
                Variant v = roll < (st.storm ? 6 : 8) ? Variant.FALLEN_STAR : roll < 22 ? Variant.CRAWLER : Variant.NORMAL;
                spawnMeteor(level, target, v, 1.2f + rand.nextFloat() * 1.3f);
            }
            if (rand.nextInt(st.storm ? 10 : 240) == 0) spawnShootingStar(level, p);
        }
    }

    public static void startStarstorm(ServerLevel level, int durationTicks) {
        LevelState st = STATES.computeIfAbsent(level.dimension(), k -> new LevelState());
        st.storm = true;
        st.stormTicks = durationTicks;
        for (ServerPlayer p : level.players()) {
            title(p, Component.translatable("title.astralfall.starstorm").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD),
                Component.translatable("title.astralfall.starstorm.sub").withStyle(ChatFormatting.AQUA));
            p.sendSystemMessage(Component.translatable("message.astralfall.starstorm.begin").withStyle(ChatFormatting.LIGHT_PURPLE));
            level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.STARSTORM.get(), SoundSource.AMBIENT, 1.5f, 1.0f);
        }
    }

    public static void endStarstorm(ServerLevel level) {
        LevelState st = STATES.get(level.dimension());
        if (st == null || !st.storm) return;
        st.storm = false;
        st.stormTicks = 0;
        for (ServerPlayer p : level.players()) {
            p.sendSystemMessage(Component.translatable("message.astralfall.starstorm.end").withStyle(ChatFormatting.GRAY));
        }
    }

    public static void title(ServerPlayer p, Component title, Component subtitle) {
        p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 60, 20));
        p.connection.send(new ClientboundSetSubtitleTextPacket(subtitle));
        p.connection.send(new ClientboundSetTitleTextPacket(title));
    }

    public static MeteorEntity spawnMeteor(ServerLevel level, BlockPos target, Variant variant, float size) {
        RandomSource rand = level.getRandom();
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, target.getX(), target.getZ());
        Vec3 impact = new Vec3(target.getX() + 0.5, y, target.getZ() + 0.5);
        double angle = rand.nextDouble() * Math.PI * 2;
        boolean steep = variant == Variant.BOSS || variant == Variant.SMALL;
        if (!steep) {
            // Launch from the nearest player's side of the sky so the meteor streaks overhead towards its
            // impact instead of starting beyond the client's entity-tracking range and popping in late.
            ServerPlayer nearest = null;
            double best = 220 * 220;
            for (ServerPlayer p : level.players()) {
                double d = p.distanceToSqr(impact.x, p.getY(), impact.z);
                if (d < best) {
                    best = d;
                    nearest = p;
                }
            }
            if (nearest != null) angle = Math.atan2(nearest.getZ() - impact.z, nearest.getX() - impact.x) + (rand.nextDouble() - 0.5) * 1.6;
        }
        double horiz = steep ? 18 + rand.nextDouble() * 10 : 60 + rand.nextDouble() * 35;
        double height = steep ? 70 : 95 + rand.nextDouble() * 35;
        double startY = Math.min(level.getMaxY() + 40, impact.y + height);
        Vec3 start = new Vec3(impact.x + Math.cos(angle) * horiz, startY, impact.z + Math.sin(angle) * horiz);
        // A meteor that starts in a chunk that is not entity-ticking would hang frozen in the sky:
        // pull the start point towards the impact until it is somewhere that ticks.
        for (int i = 0; i < 6 && !level.isPositionEntityTicking(BlockPos.containing(start.x, impact.y, start.z)); i++) {
            start = impact.add(start.subtract(impact).scale(0.7));
        }
        double speed = switch (variant) {
            case SMALL -> 2.6;
            case BOSS -> 2.2;
            default -> 1.9;
        };
        MeteorEntity m = new MeteorEntity(ModEntities.METEOR.get(), level);
        m.setPos(start.x, start.y, start.z);
        m.setup(variant, size, impact.subtract(start).normalize().scale(speed));
        level.addFreshEntity(m);
        level.playSound(null, impact.x, impact.y + 24, impact.z, ModSounds.METEOR_INCOMING.get(), SoundSource.WEATHER, 10.0f, 0.85f + rand.nextFloat() * 0.3f);
        return m;
    }

    public static void spawnShootingStar(ServerLevel level, ServerPlayer p) {
        RandomSource rand = level.getRandom();
        double angle = rand.nextDouble() * Math.PI * 2;
        Vec3 start = new Vec3(p.getX() + Math.cos(angle) * 90, Math.min(level.getMaxY() + 30, p.getY() + 90 + rand.nextInt(40)), p.getZ() + Math.sin(angle) * 90);
        double travel = angle + Math.PI + (rand.nextDouble() - 0.5) * 1.4;
        Vec3 vel = new Vec3(Math.cos(travel) * 3.2, -0.5 - rand.nextDouble() * 0.6, Math.sin(travel) * 3.2);
        MeteorEntity m = new MeteorEntity(ModEntities.METEOR.get(), level);
        m.setPos(start.x, start.y, start.z);
        m.setup(Variant.SHOOTING_STAR, 0.4f, vel);
        level.addFreshEntity(m);
    }

    // ------------------------------------------------------------------ impact
    public static void impact(ServerLevel level, MeteorEntity meteor, BlockPos pos) {
        Variant v = meteor.getVariant();
        float size = meteor.getSize();
        RandomSource rand = level.getRandom();
        Vec3 c = Vec3.atCenterOf(pos);
        float power = switch (v) {
            case SMALL -> 2.6f;
            case BOSS -> 4.0f;
            default -> 1.6f + size;
        };
        level.explode(meteor, c.x, c.y, c.z, power, false, Level.ExplosionInteraction.NONE);
        level.playSound(null, c.x, c.y, c.z, ModSounds.METEOR_IMPACT.get(), SoundSource.WEATHER, 10.0f, 0.8f + rand.nextFloat() * 0.2f);
        FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 1, 0, 0);
        FX.burst(level, ParticleTypes.LAVA, c, 30, 1.0, 0.5);
        FX.burst(level, ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, c.x, c.y + 1, c.z, 20, 1.2, 0.5, 1.2, 0.02);
        FX.ring(level, ParticleTypes.FLAME, c.add(0, 0.3, 0), 1.0, 40, 0.05);
        FX.ring(level, ModParticles.COMET_TRAIL.get(), c.add(0, 0.5, 0), 0.6, 30, 0.1);

        if (v == Variant.SMALL || v == Variant.BOSS) return;

        int radius = Math.round(2.5f + size * 1.5f);
        BlockPos floor = Config.meteorCraters() ? carveCrater(level, pos, radius, rand) : pos;
        placeCore(level, floor, v, rand);
        scatterEjecta(level, pos, radius, rand);

        if (v == Variant.CRAWLER) {
            int n = 1 + rand.nextInt(2);
            for (int i = 0; i < n; i++) {
                MeteoriteCrawlerEntity crawler = ModEntities.METEORITE_CRAWLER.get().create(level, EntitySpawnReason.EVENT);
                if (crawler == null) continue;
                crawler.snapTo(floor.getX() + 0.5 + rand.nextGaussian(), floor.getY() + 2, floor.getZ() + 0.5 + rand.nextGaussian(), rand.nextFloat() * 360f, 0f);
                level.addFreshEntity(crawler);
            }
            FX.burst(level, ModParticles.VOID_MOTE.get(), Vec3.atCenterOf(floor.above(2)), 40, 1.0, 0.2);
        }
        if (v == Variant.FALLEN_STAR) {
            for (int i = 0; i < 3; i++) {
                AstralWispEntity wisp = ModEntities.ASTRAL_WISP.get().create(level, EntitySpawnReason.EVENT);
                if (wisp == null) continue;
                wisp.snapTo(floor.getX() + 0.5 + rand.nextGaussian() * 3, floor.getY() + 4 + rand.nextInt(3), floor.getZ() + 0.5 + rand.nextGaussian() * 3, rand.nextFloat() * 360f, 0f);
                level.addFreshEntity(wisp);
            }
            for (ServerPlayer p : level.players()) {
                if (p.distanceToSqr(c) < 256 * 256) {
                    p.sendSystemMessage(Component.translatable("message.astralfall.fallen_star", floor.getX(), floor.getZ()).withStyle(ChatFormatting.GOLD));
                }
            }
        }
    }

    private static boolean carvable(ServerLevel level, BlockPos p, BlockState s) {
        if (s.isAir() || s.hasBlockEntity() || !s.getFluidState().isEmpty()) return false;
        float hardness = s.getDestroySpeed(level, p);
        return hardness >= 0 && hardness < 30 && !s.is(ModBlocks.FALLEN_STAR.get());
    }

    /** Carves a bowl-shaped crater; returns the position at the bottom centre of the bowl. */
    private static BlockPos carveCrater(ServerLevel level, BlockPos center, int r, RandomSource rand) {
        BlockPos bottom = center;
        for (int dx = -r; dx <= r; dx++) {
            for (int dz = -r; dz <= r; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d > r + 0.3) continue;
                int depth = (int) Math.round(Math.sqrt(Math.max(0, r * r - d * d)) * 0.55);
                int x = center.getX() + dx, z = center.getZ() + dz;
                int floorY = center.getY() - depth + 1;
                int top = Math.min(level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z) - 1, center.getY() + 5);
                for (int y = top; y >= floorY; y--) {
                    BlockPos p = new BlockPos(x, y, z);
                    BlockState s = level.getBlockState(p);
                    if (carvable(level, p, s)) level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
                }
                BlockPos lining = new BlockPos(x, floorY - 1, z);
                BlockState ls = level.getBlockState(lining);
                if (carvable(level, lining, ls) || ls.isAir()) {
                    double hot = 1.0 - d / r;
                    BlockState put;
                    float roll = rand.nextFloat();
                    if (hot > 0.55 && roll < 0.45) put = ModBlocks.METEORITE_ROCK.get().defaultBlockState();
                    else if (hot > 0.4 && roll < 0.6) put = Blocks.MAGMA_BLOCK.defaultBlockState();
                    else if (roll < 0.65) put = ModBlocks.COOLED_METEORITE.get().defaultBlockState();
                    else put = rand.nextBoolean() ? Blocks.COARSE_DIRT.defaultBlockState() : Blocks.BLACKSTONE.defaultBlockState();
                    level.setBlock(lining, put, 2);
                    if (hot > 0.3 && rand.nextInt(9) == 0 && level.getBlockState(lining.above()).isAir()) {
                        level.setBlock(lining.above(), Blocks.FIRE.defaultBlockState(), 3);
                    }
                }
                if (dx == 0 && dz == 0) bottom = new BlockPos(x, floorY, z);
            }
        }
        return bottom;
    }

    private static void placeCore(ServerLevel level, BlockPos floor, Variant v, RandomSource rand) {
        BlockState rock = ModBlocks.METEORITE_ROCK.get().defaultBlockState();
        BlockState ore = ModBlocks.STARMETAL_ORE.get().defaultBlockState();
        int ores = 0;
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                for (int dy = 0; dy <= 1; dy++) {
                    boolean corner = Math.abs(dx) + Math.abs(dz) == 2;
                    if (dy == 1 && (corner || rand.nextInt(3) == 0)) continue;
                    if (corner && rand.nextBoolean()) continue;
                    BlockPos p = floor.offset(dx, dy, dz);
                    BlockState cur = level.getBlockState(p);
                    if (!cur.isAir() && !carvable(level, p, cur)) continue;
                    boolean isOre = (ores < 4 && rand.nextInt(3) == 0) || (dx == 0 && dz == 0 && dy == 0);
                    if (isOre) ores++;
                    level.setBlock(p, isOre ? ore : rock, 3);
                }
            }
        }
        BlockPos top = floor.above(2);
        if (v == Variant.FALLEN_STAR) {
            level.setBlock(top, ModBlocks.FALLEN_STAR.get().defaultBlockState(), 3);
        } else {
            placeIfAir(level, top, ModBlocks.SKYSHARD_CLUSTER.get().defaultBlockState());
        }
        for (int i = 0; i < 2; i++) {
            BlockPos p = floor.offset(rand.nextInt(3) - 1, 1, rand.nextInt(3) - 1);
            if (level.getBlockState(p).isAir() && level.getBlockState(p.below()).isSolid()) {
                level.setBlock(p, ModBlocks.SKYSHARD_CLUSTER.get().defaultBlockState(), 3);
            }
        }
    }

    private static void placeIfAir(ServerLevel level, BlockPos p, BlockState s) {
        if (level.getBlockState(p).isAir()) level.setBlock(p, s, 3);
    }

    private static void scatterEjecta(ServerLevel level, BlockPos center, int r, RandomSource rand) {
        int n = 4 + rand.nextInt(5);
        for (int i = 0; i < n; i++) {
            double a = rand.nextDouble() * Math.PI * 2;
            double d = r + 1 + rand.nextDouble() * 4;
            int x = (int) Math.floor(center.getX() + Math.cos(a) * d), z = (int) Math.floor(center.getZ() + Math.sin(a) * d);
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            BlockPos p = new BlockPos(x, y, z);
            if (Math.abs(y - center.getY()) > 8 || !level.getBlockState(p).canBeReplaced()) continue;
            level.setBlock(p, rand.nextInt(3) == 0 ? ModBlocks.METEORITE_ROCK.get().defaultBlockState() : ModBlocks.COOLED_METEORITE.get().defaultBlockState(), 3);
        }
    }
}
