package com.rimeheart.world;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.RandomizableContainer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.SpawnerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** Writes a {@link Blueprint} into the world, optionally clipped to a chunk's bounding box. */
public final class BlueprintPlacer {
    private BlueprintPlacer() {}

    public static void place(ServerLevelAccessor level, Blueprint bp, BlockPos origin, BoundingBox clip, RandomSource random, int flags) {
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (var e : bp.blocks.long2ObjectEntrySet()) {
            long k = e.getLongKey();
            p.set(origin.getX() + BlockPos.getX(k), origin.getY() + BlockPos.getY(k), origin.getZ() + BlockPos.getZ(k));
            if (clip != null && !clip.isInside(p)) continue;
            if (!level.isInsideBuildHeight(p.getY())) continue;
            level.setBlock(p, e.getValue(), flags);
        }
        for (long k : bp.foundation) {
            int x = BlockPos.getX(k), z = BlockPos.getZ(k);
            for (int y = -2; y >= -28; y--) {
                if (bp.has(x, y, z)) break;
                p.set(origin.getX() + x, origin.getY() + y, origin.getZ() + z);
                if (clip != null && !clip.isInside(p)) break;
                if (!level.isInsideBuildHeight(p.getY())) break;
                BlockState cur = level.getBlockState(p);
                if (!cur.isAir() && !cur.canBeReplaced() && cur.getFluidState().isEmpty()) break;
                level.setBlock(p, bp.foundationState, flags);
            }
        }
        for (Blueprint.Chest c : bp.chests) {
            BlockPos at = origin.offset(c.pos());
            if (clip != null && !clip.isInside(at)) continue;
            Direction facing = c.facing();
            level.setBlock(at, Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING, facing), flags);
            RandomizableContainer.setBlockEntityLootTable(level, random, at, c.loot());
        }
        for (Blueprint.Spawner s : bp.spawners) {
            BlockPos at = origin.offset(s.pos());
            if (clip != null && !clip.isInside(at)) continue;
            level.setBlock(at, Blocks.SPAWNER.defaultBlockState(), flags);
            if (level.getBlockEntity(at) instanceof SpawnerBlockEntity spawner) {
                spawner.setEntityId(s.type().get(), random);
            }
        }
        for (Blueprint.Mob m : bp.mobs) {
            BlockPos at = origin.offset(m.pos());
            if (clip != null && !clip.isInside(at)) continue;
            EntityType<?> type = m.type().get();
            Entity entity = type.create(level.getLevel(), EntitySpawnReason.STRUCTURE);
            if (entity == null) continue;
            entity.snapTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, random.nextFloat() * 360f, 0f);
            if (entity instanceof Mob mob) mob.setPersistenceRequired();
            level.addFreshEntityWithPassengers(entity);
        }
    }

    /** Places a blueprint immediately (used by commands). */
    public static void placeNow(ServerLevel level, Blueprint bp, BlockPos origin) {
        place(level, bp, origin, null, level.getRandom(), 2 | 16);
    }
}
