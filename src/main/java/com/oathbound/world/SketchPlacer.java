package com.oathbound.world;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.RandomizableContainer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.SpawnerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** Transfers a {@link Sketch} into a level, optionally clipped to one chunk's box during world generation. */
public final class SketchPlacer {
    private SketchPlacer() {}

    private static boolean inside(BoundingBox clip, BlockPos p) {
        return clip == null || clip.isInside(p);
    }

    public static void place(ServerLevelAccessor level, Sketch sketch, BlockPos origin, BoundingBox clip, RandomSource random, int flags) {
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (var e : sketch.blocks.entrySet()) {
            m.setWithOffset(origin, e.getKey());
            if (!inside(clip, m) || !level.isInsideBuildHeight(m.getY())) continue;
            level.setBlock(m, e.getValue(), flags);
        }
        // Footings: pour the footing state down to real ground, but only when ground is within reach, so
        // builds overhanging a cliff or floating in the Gloaming do not grow long pillars into the void.
        for (long col : sketch.footings) {
            int x = BlockPos.getX(col), z = BlockPos.getZ(col);
            int top = -1;
            while (sketch.blocks.containsKey(new BlockPos(x, top, z))) top--;
            int depth = 0;
            for (int y = top; y > top - sketch.footingDepth; y--) {
                m.set(origin.getX() + x, origin.getY() + y, origin.getZ() + z);
                if (!level.isInsideBuildHeight(m.getY())) {
                    depth = -1;
                    break;
                }
                BlockState cur = level.getBlockState(m);
                if (!cur.isAir() && !cur.canBeReplaced() && cur.getFluidState().isEmpty()) {
                    depth = top - y;
                    break;
                }
                depth = -1;
            }
            if (depth <= 0) continue;
            for (int y = top; y > top - depth; y--) {
                m.set(origin.getX() + x, origin.getY() + y, origin.getZ() + z);
                if (!inside(clip, m)) continue;
                level.setBlock(m, sketch.footing, flags);
            }
        }
        for (Sketch.Loot l : sketch.loot) {
            BlockPos at = origin.offset(l.pos());
            if (!inside(clip, at)) continue;
            level.setBlock(at, Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING, l.facing()), flags);
            RandomizableContainer.setBlockEntityLootTable(level, random, at, l.table());
        }
        for (Sketch.Spawner s : sketch.spawners) {
            BlockPos at = origin.offset(s.pos());
            if (!inside(clip, at)) continue;
            level.setBlock(at, Blocks.SPAWNER.defaultBlockState(), flags);
            if (level.getBlockEntity(at) instanceof SpawnerBlockEntity spawner) spawner.setEntityId(s.type().get(), random);
        }
        for (Sketch.Resident r : sketch.residents) {
            BlockPos at = origin.offset(r.pos());
            if (!inside(clip, at)) continue;
            Entity e = r.type().get().create(level.getLevel(), EntitySpawnReason.STRUCTURE);
            if (e == null) continue;
            e.snapTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, r.yaw(), 0f);
            if (e instanceof Mob mob) mob.setPersistenceRequired();
            level.addFreshEntityWithPassengers(e);
        }
    }

    /** Builds a sketch right now (commands, the Gloaming throne, tests). */
    public static void placeNow(ServerLevel level, Sketch sketch, BlockPos origin) {
        place(level, sketch, origin, null, level.getRandom(), 2 | 16);
    }
}
