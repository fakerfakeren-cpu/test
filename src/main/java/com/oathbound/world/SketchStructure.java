package com.oathbound.world;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.oathbound.registry.ModWorldgen;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * A data-driven structure whose layout comes from {@link Sketches}. The {@code sketch} field chooses the
 * design; each design also knows how it wants to sit in the terrain (see {@link Sketches.Type#siting}).
 * Spacing and biomes are ordinary structure-set / tag data, so modpacks can retune them with a datapack.
 */
public class SketchStructure extends Structure {
    public static final MapCodec<SketchStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
        settingsCodec(i),
        Codec.STRING.fieldOf("sketch").forGetter(s -> s.sketch)
    ).apply(i, SketchStructure::new));

    private final String sketch;

    public SketchStructure(StructureSettings settings, String sketch) {
        super(settings);
        this.sketch = sketch;
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        Sketches.Type type = Sketches.Type.named(sketch);
        int cx = ctx.chunkPos().getMiddleBlockX(), cz = ctx.chunkPos().getMiddleBlockZ();
        int r = type.footprint;
        int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE;
        for (int[] o : new int[][]{{0, 0}, {r, r}, {-r, r}, {r, -r}, {-r, -r}, {r, 0}, {-r, 0}, {0, r}, {0, -r}}) {
            int h = ctx.chunkGenerator().getFirstOccupiedHeight(cx + o[0], cz + o[1], Heightmap.Types.WORLD_SURFACE_WG, ctx.heightAccessor(), ctx.randomState());
            lo = Math.min(lo, h);
            hi = Math.max(hi, h);
        }
        int sea = ctx.chunkGenerator().getSeaLevel();
        int y;
        switch (type.siting) {
            case SHORE -> {
                // The Drowned Chapel wants low, wet ground at the waterline.
                if (lo > sea + 4 || hi - lo > 8) return Optional.empty();
                y = sea - 1;
            }
            case UNDERGROUND -> {
                // The Lumenite Delve: galleries thirty blocks down, a headframe on the surface above the shaft.
                if (hi - lo > type.tolerance || lo <= sea) return Optional.empty();
                y = lo - 30;
                if (y < ctx.heightAccessor().getMinY() + 8) return Optional.empty();
            }
            default -> {
                if (hi - lo > type.tolerance || lo <= sea) return Optional.empty();
                y = lo;
            }
        }
        BlockPos origin = new BlockPos(cx, y, cz);
        long seed = ctx.seed() ^ (ctx.chunkPos().pack() * 0x5DEECE66DL);
        return Optional.of(new GenerationStub(origin, b -> b.addPiece(new SketchPiece(type, seed, origin))));
    }

    @Override
    public StructureType<?> type() {
        return ModWorldgen.SKETCH_STRUCTURE.get();
    }
}
