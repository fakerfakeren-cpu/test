package com.rimeheart.world;

import com.rimeheart.registry.ModWorldgen;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** One structure piece covering an entire blueprint. Rebuilt from (type, seed) for every chunk. */
public class BlueprintPiece extends StructurePiece {
    private final Blueprints.Type type;
    private final long seed;
    private final BlockPos origin;

    public BlueprintPiece(Blueprints.Type type, long seed, BlockPos origin) {
        super(ModWorldgen.BLUEPRINT_PIECE.get(), 0, box(type, seed, origin));
        this.type = type;
        this.seed = seed;
        this.origin = origin;
    }

    public BlueprintPiece(StructurePieceSerializationContext ctx, CompoundTag tag) {
        super(ModWorldgen.BLUEPRINT_PIECE.get(), tag);
        this.type = Blueprints.Type.byName(tag.getStringOr("Blueprint", "frozen_sanctum"));
        this.seed = tag.getLongOr("Seed", 0L);
        this.origin = new BlockPos(tag.getIntOr("OX", 0), tag.getIntOr("OY", 64), tag.getIntOr("OZ", 0));
    }

    private static BoundingBox box(Blueprints.Type type, long seed, BlockPos origin) {
        BoundingBox b = Blueprints.get(type, seed).bounds();
        return new BoundingBox(b.minX() + origin.getX(), b.minY() + origin.getY(), b.minZ() + origin.getZ(),
            b.maxX() + origin.getX(), b.maxY() + origin.getY(), b.maxZ() + origin.getZ());
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext ctx, CompoundTag tag) {
        tag.putString("Blueprint", type.id());
        tag.putLong("Seed", seed);
        tag.putInt("OX", origin.getX());
        tag.putInt("OY", origin.getY());
        tag.putInt("OZ", origin.getZ());
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structures, ChunkGenerator generator, RandomSource random, BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        BlueprintPlacer.place(level, Blueprints.get(type, seed), origin, chunkBox, random, 2);
    }
}
