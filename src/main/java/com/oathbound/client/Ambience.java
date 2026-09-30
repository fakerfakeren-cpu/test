package com.oathbound.client;

import com.oathbound.Config;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ParticleStatus;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BiomeTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.TickEvent;

/**
 * The world's own life, drawn around the player: fireflies over grass on warm nights, blossoms on the wind in the
 * cherry groves, plankton glowing where the sea meets the dark, spores and wisp-lights over the swamps, gloam-mist
 * in the dark forests, ash on the badlands wind, motes rising from lumenite in the caves; and its voice: birdsong
 * by day, crickets, owls and frogs by night, wind on the heights. Client-only, cheap, and scaled by the particle
 * setting.
 */
public final class Ambience {
    private static final RandomSource R = RandomSource.create();
    private static int soundIn = 80;

    private Ambience() {}

    private enum Land { MEADOW, FOREST, DARK_FOREST, CHERRY, FLOWERS, SWAMP, WATER, BADLANDS, HEIGHTS, COLD, DRY, OTHER }

    private static Land land(Holder<Biome> b) {
        if (b.is(Biomes.CHERRY_GROVE)) return Land.CHERRY;
        if (b.is(Biomes.FLOWER_FOREST) || b.is(Biomes.MEADOW) || b.is(Biomes.SUNFLOWER_PLAINS)) return Land.FLOWERS;
        if (b.is(Biomes.SWAMP) || b.is(Biomes.MANGROVE_SWAMP)) return Land.SWAMP;
        if (b.is(Biomes.DARK_FOREST)) return Land.DARK_FOREST;
        if (b.is(BiomeTags.IS_BADLANDS)) return Land.BADLANDS;
        if (b.is(BiomeTags.IS_OCEAN) || b.is(BiomeTags.IS_BEACH) || b.is(BiomeTags.IS_RIVER)) return Land.WATER;
        if (b.is(BiomeTags.IS_MOUNTAIN)) return Land.HEIGHTS;
        if (b.is(BiomeTags.SPAWNS_COLD_VARIANT_FROGS)) return Land.COLD;
        if (b.is(BiomeTags.IS_FOREST) || b.is(BiomeTags.IS_TAIGA) || b.is(BiomeTags.IS_JUNGLE)) return Land.FOREST;
        if (b.is(BiomeTags.IS_SAVANNA) || b.is(Biomes.DESERT)) return Land.DRY;
        if (b.is(Biomes.PLAINS) || b.is(BiomeTags.IS_HILL)) return Land.MEADOW;
        return Land.OTHER;
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        ClientLevel level = mc.level;
        if (level == null || mc.player == null || mc.isPaused() || !Config.ambientLife()) return;
        if (level.dimension() != Level.OVERWORLD) return;
        int budget = switch (mc.options.particles().get()) {
            case ALL -> 10;
            case DECREASED -> 4;
            default -> 0;
        };
        boolean night = level.isDarkOutside();
        boolean rain = level.getRainLevel(1f) > 0.2f;
        BlockPos me = mc.player.blockPosition();
        boolean underground = me.getY() < level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, me.getX(), me.getZ()) - 8;
        for (int i = 0; i < budget; i++) {
            if (underground) cave(level, me);
            else surface(level, me, night, rain);
        }
        if (--soundIn <= 0) {
            soundIn = 60 + R.nextInt(160);
            if (!underground) voice(mc, level, me, night, rain);
        }
    }

    private static void add(ClientLevel level, ParticleOptions p, double x, double y, double z, double dx, double dy, double dz) {
        level.addParticle(p, x, y, z, dx, dy, dz);
    }

    private static void surface(ClientLevel level, BlockPos me, boolean night, boolean rain) {
        int x = me.getX() + R.nextInt(49) - 24, z = me.getZ() + R.nextInt(49) - 24;
        if (!level.isLoaded(new BlockPos(x, me.getY(), z))) return;
        int ground = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        if (Math.abs(ground - me.getY()) > 24) return;
        BlockPos at = new BlockPos(x, ground, z);
        Land land = land(level.getBiome(at));
        double px = x + R.nextDouble(), pz = z + R.nextDouble();
        switch (land) {
            case MEADOW, FOREST, FLOWERS, SWAMP, CHERRY -> {
                if (night && !rain && R.nextFloat() < (land == Land.SWAMP ? 0.5f : 0.35f)) {
                    add(level, ModParticles.FIREFLY.get(), px, ground + 0.4 + R.nextDouble() * 2.6, pz,
                        (R.nextDouble() - 0.5) * 0.02, (R.nextDouble() - 0.5) * 0.01, (R.nextDouble() - 0.5) * 0.02);
                }
                if (land == Land.CHERRY && R.nextFloat() < 0.35f) {
                    add(level, ModParticles.BLOSSOM.get(), px, ground + 4 + R.nextDouble() * 6, pz, 0.03 + R.nextDouble() * 0.02, -0.01, 0.01);
                } else if (land == Land.FLOWERS && !night && R.nextFloat() < 0.12f) {
                    add(level, ModParticles.PETAL.get(), px, ground + 1 + R.nextDouble() * 3, pz, 0.02, 0.0, 0.01);
                } else if (land == Land.SWAMP && R.nextFloat() < 0.25f) {
                    add(level, ModParticles.SPORE.get(), px, ground + 0.3 + R.nextDouble() * 3, pz, 0.005, 0.004, 0.0);
                    if (night && R.nextFloat() < 0.08f) add(level, ModParticles.SPIRIT.get(), px, ground + 0.6, pz, 0, 0.005, 0);
                }
            }
            case DARK_FOREST -> {
                if (night && R.nextFloat() < 0.35f) add(level, ModParticles.GLOAM_WISP.get(), px, ground + 0.2 + R.nextDouble() * 1.4, pz, 0.006, 0.0, 0.004);
                else if (!night && R.nextFloat() < 0.1f) add(level, ModParticles.SPORE.get(), px, ground + 1 + R.nextDouble() * 4, pz, 0.0, -0.002, 0.0);
            }
            case WATER -> {
                // plankton glowing on the night water
                BlockState top = level.getBlockState(at.below());
                if (night && top.getFluidState().isSource() && R.nextFloat() < 0.6f) {
                    add(level, ModParticles.TIDE.get(), px, ground + 0.02, pz, (R.nextDouble() - 0.5) * 0.01, 0.0, (R.nextDouble() - 0.5) * 0.01);
                }
            }
            case BADLANDS -> {
                if (R.nextFloat() < 0.3f) add(level, ModParticles.ASH.get(), px, ground + 1 + R.nextDouble() * 8, pz, 0.04 + R.nextDouble() * 0.03, -0.004, 0.01);
            }
            default -> {}
        }
    }

    /** In caves: motes lift from lumenite ore and crystal. */
    private static void cave(ClientLevel level, BlockPos me) {
        BlockPos p = me.offset(R.nextInt(25) - 12, R.nextInt(17) - 8, R.nextInt(25) - 12);
        BlockState s = level.getBlockState(p);
        boolean lumen = s.is(ModBlocks.LUMENITE_CLUSTER.get()) || s.is(ModBlocks.LUMENITE_ORE.get()) || s.is(ModBlocks.DEEPSLATE_LUMENITE_ORE.get());
        if (!lumen) return;
        for (var d : net.minecraft.core.Direction.values()) {
            BlockPos a = p.relative(d);
            if (level.getBlockState(a).isAir()) {
                add(level, ModParticles.LUMEN_MOTE.get(), a.getX() + R.nextDouble(), a.getY() + R.nextDouble(), a.getZ() + R.nextDouble(), 0, 0.012, 0);
                return;
            }
        }
    }

    private static void voice(Minecraft mc, ClientLevel level, BlockPos me, boolean night, boolean rain) {
        Land land = land(level.getBiome(me));
        SoundEvent s = null;
        float vol = 0.45f;
        if (me.getY() > 120 || land == Land.HEIGHTS) {
            s = ModSounds.AMB_WIND.get();
            vol = 0.35f;
        } else if (rain) {
            return;
        } else if (night) {
            s = switch (land) {
                case SWAMP -> ModSounds.AMB_FROGS.get();
                case FOREST, DARK_FOREST -> R.nextInt(3) == 0 ? ModSounds.AMB_OWL.get() : ModSounds.AMB_CRICKETS.get();
                case MEADOW, FLOWERS, CHERRY, DRY -> ModSounds.AMB_CRICKETS.get();
                default -> null;
            };
        } else {
            if (land == Land.FOREST || land == Land.FLOWERS || land == Land.CHERRY || land == Land.MEADOW || land == Land.DARK_FOREST) {
                s = ModSounds.AMB_BIRDSONG.get();
            }
        }
        if (s == null) return;
        double a = R.nextDouble() * Math.PI * 2, d = 6 + R.nextDouble() * 14;
        level.playLocalSound(mc.player.getX() + Math.cos(a) * d, mc.player.getY() + 2 + R.nextDouble() * 4, mc.player.getZ() + Math.sin(a) * d,
            s, SoundSource.AMBIENT, vol, 0.9f + R.nextFloat() * 0.2f, false);
    }
}
