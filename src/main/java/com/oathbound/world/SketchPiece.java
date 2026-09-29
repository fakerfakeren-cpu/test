package com.oathbound.world;

import com.oathbound.registry.ModWorldgen;
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

/** A whole sketch as one structure piece; it is redrawn from (type, seed) for every chunk it touches. */
public class SketchPiece extends StructurePiece {
    private final Sketches.Type type;
    private final long seed;
    private final BlockPos origin;

    public SketchPiece(Sketches.Type type, long seed, BlockPos origin) {
        super(ModWorldgen.SKETCH_PIECE.get(), 0, worldBox(type, seed, origin));
        this.type = type;
        this.seed = seed;
        this.origin = origin;
    }

    public SketchPiece(StructurePieceSerializationContext ctx, CompoundTag tag) {
        super(ModWorldgen.SKETCH_PIECE.get(), tag);
        this.type = Sketches.Type.named(tag.getStringOr("Sketch", "wayshrine"));
        this.seed = tag.getLongOr("Seed", 0L);
        int[] o = tag.getIntArray("Origin").orElse(new int[]{0, 64, 0});
        this.origin = new BlockPos(o[0], o[1], o[2]);
    }

    private static BoundingBox worldBox(Sketches.Type type, long seed, BlockPos o) {
        BoundingBox b = Sketches.cached(type, seed).bounds();
        return b.moved(o.getX(), o.getY(), o.getZ());
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext ctx, CompoundTag tag) {
        tag.putString("Sketch", type.id());
        tag.putLong("Seed", seed);
        tag.putIntArray("Origin", new int[]{origin.getX(), origin.getY(), origin.getZ()});
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structures, ChunkGenerator generator, RandomSource random, BoundingBox chunkBox, ChunkPos chunkPos, BlockPos pivot) {
        SketchPlacer.place(level, Sketches.cached(type, seed), origin, chunkBox, random, 2);
    }
}
