package com.astralfall.world;

import com.astralfall.registry.ModWorldgen;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/** Data-driven structure that places one of the procedural {@link Blueprints}. */
public class BlueprintStructure extends Structure {
    public static final MapCodec<BlueprintStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
        settingsCodec(i),
        Codec.STRING.fieldOf("blueprint").forGetter(s -> s.blueprint),
        Codec.INT.optionalFieldOf("y_offset", 0).forGetter(s -> s.yOffset)
    ).apply(i, BlueprintStructure::new));

    private final String blueprint;
    private final int yOffset;

    public BlueprintStructure(StructureSettings settings, String blueprint, int yOffset) {
        super(settings);
        this.blueprint = blueprint;
        this.yOffset = yOffset;
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        Blueprints.Type type = Blueprints.Type.byName(blueprint);
        int x = ctx.chunkPos().getMiddleBlockX();
        int z = ctx.chunkPos().getMiddleBlockZ();
        int y = Integer.MAX_VALUE;
        int sum = 0, n = 0;
        int spread = type == Blueprints.Type.OBSERVATORY ? 14 : 8;
        for (int[] o : new int[][]{{0, 0}, {spread, 0}, {-spread, 0}, {0, spread}, {0, -spread}}) {
            int h = ctx.chunkGenerator().getFirstOccupiedHeight(x + o[0], z + o[1], Heightmap.Types.WORLD_SURFACE_WG, ctx.heightAccessor(), ctx.randomState());
            y = Math.min(y, h);
            sum += h;
            n++;
        }
        int mean = sum / n;
        if (type != Blueprints.Type.SKY_SHRINE && mean - y > 10) return Optional.empty();
        if (y <= ctx.chunkGenerator().getSeaLevel() - 2 && type != Blueprints.Type.SKY_SHRINE) return Optional.empty();
        int baseY = type == Blueprints.Type.SKY_SHRINE ? Math.max(mean, ctx.chunkGenerator().getSeaLevel()) : y;
        BlockPos origin = new BlockPos(x, baseY + yOffset, z);
        long seed = ctx.seed() ^ ctx.chunkPos().toLong() * 341873128712L;
        return Optional.of(new GenerationStub(origin, builder -> builder.addPiece(new BlueprintPiece(type, seed, origin))));
    }

    @Override
    public StructureType<?> type() {
        return ModWorldgen.BLUEPRINT_STRUCTURE.get();
    }
}
