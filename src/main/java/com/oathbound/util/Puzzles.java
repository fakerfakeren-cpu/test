package com.oathbound.util;

import com.oathbound.item.WardensLanternItem;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Shared helpers for the structure puzzles. */
public final class Puzzles {
    private Puzzles() {}

    /** Stable per-structure number derived from a block position (used to vary each puzzle's answer). */
    public static int key(BlockPos pos) {
        long h = pos.asLong() * 0x9E3779B97F4A7C15L;
        h ^= (h >>> 29);
        h *= 0xBF58476D1CE4E5B9L;
        h ^= (h >>> 32);
        return (int) (h & 0x7fffffff);
    }

    public static boolean has(Player player, Item item) {
        if (player.hasInfiniteMaterials()) return true;
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            if (inv.getItem(i).is(item)) return true;
        }
        return false;
    }

    /** True if the player carries a Warden's (or Everflame) Lantern that still has fuel. */
    public static boolean hasLitLantern(Player player) {
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.getItem() instanceof WardensLanternItem lantern && lantern.isLit(s)) return true;
        }
        return player.hasInfiniteMaterials();
    }

    /** Finds blocks of a type within a cube, nearest first. */
    public static List<BlockPos> find(ServerLevel level, BlockPos center, int radius, Block block) {
        List<BlockPos> out = new ArrayList<>();
        for (BlockPos p : BlockPos.betweenClosed(center.offset(-radius, -radius, -radius), center.offset(radius, radius, radius))) {
            if (level.getBlockState(p).is(block)) out.add(p.immutable());
        }
        out.sort(Comparator.comparingDouble(p -> p.distSqr(center)));
        return out;
    }

    /**
     * Removes every block of {@code block} near {@code center}, a layer at a time from the top down, with particles
     * and a sound, so seals visibly dissolve rather than vanish.
     */
    public static int unseal(ServerLevel level, BlockPos center, int radius, Block block, ParticleOptions particle, SoundEvent sound) {
        List<BlockPos> found = find(level, center, radius, block);
        if (found.isEmpty()) return 0;
        found.sort((a, b) -> Integer.compare(b.getY(), a.getY()));
        int maxY = found.get(0).getY();
        level.playSound(null, center, sound, SoundSource.BLOCKS, 2.0f, 1.0f);
        for (BlockPos p : found) {
            int delay = 2 + (maxY - p.getY()) * 5 + level.getRandom().nextInt(3);
            Scheduler.later(level, delay, l -> {
                if (!l.getBlockState(p).is(block)) return;
                l.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
                Vfx.burst(l, particle, Vec3.atCenterOf(p), 8, 0.3, 0.05);
                Vfx.burst(l, ModParticles.LUMEN_MOTE.get(), Vec3.atCenterOf(p), 3, 0.3, 0.02);
            });
        }
        return found.size();
    }

    /** Removes the blocks right now (self-test / commands). */
    public static int unsealNow(ServerLevel level, BlockPos center, int radius, Block block) {
        List<BlockPos> found = find(level, center, radius, block);
        for (BlockPos p : found) level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
        return found.size();
    }
}
