package com.rimeheart.world;

import it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2ObjectMap;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * A procedurally built set of block placements in local coordinates (origin = structure anchor).
 * Blueprints are deterministic for a given seed, so world generation can rebuild them per chunk.
 */
public final class Blueprint {
    public record Chest(BlockPos pos, Direction facing, ResourceKey<LootTable> loot) {}
    public record Spawner(BlockPos pos, Supplier<? extends EntityType<?>> type) {}
    public record Mob(BlockPos pos, Supplier<? extends EntityType<?>> type) {}

    public final Long2ObjectMap<BlockState> blocks = new Long2ObjectLinkedOpenHashMap<>();
    public final LongSet foundation = new LongOpenHashSet();
    public BlockState foundationState = Blocks.STONE_BRICKS.defaultBlockState();
    public final List<Chest> chests = new ArrayList<>();
    public final List<Spawner> spawners = new ArrayList<>();
    public final List<Mob> mobs = new ArrayList<>();
    public final RandomSource random;
    private int minX = Integer.MAX_VALUE, minY = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE;
    private int maxX = Integer.MIN_VALUE, maxY = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;

    public Blueprint(RandomSource random) {
        this.random = random;
    }

    private void grow(int x, int y, int z) {
        minX = Math.min(minX, x); minY = Math.min(minY, y); minZ = Math.min(minZ, z);
        maxX = Math.max(maxX, x); maxY = Math.max(maxY, y); maxZ = Math.max(maxZ, z);
    }

    public BoundingBox bounds() {
        return new BoundingBox(minX, minY - 16, minZ, maxX, maxY, maxZ);
    }

    public void set(int x, int y, int z, BlockState s) {
        blocks.put(BlockPos.asLong(x, y, z), s);
        grow(x, y, z);
    }

    public BlockState get(int x, int y, int z) {
        return blocks.get(BlockPos.asLong(x, y, z));
    }

    public boolean has(int x, int y, int z) {
        return blocks.containsKey(BlockPos.asLong(x, y, z));
    }

    public void setIfAbsent(int x, int y, int z, BlockState s) {
        if (!has(x, y, z)) set(x, y, z, s);
    }

    public void air(int x, int y, int z) {
        set(x, y, z, Blocks.AIR.defaultBlockState());
    }

    public void foundation(int x, int z) {
        foundation.add(BlockPos.asLong(x, 0, z));
    }

    public void fill(int x1, int y1, int z1, int x2, int y2, int z2, BlockState s) {
        for (int x = Math.min(x1, x2); x <= Math.max(x1, x2); x++)
            for (int y = Math.min(y1, y2); y <= Math.max(y1, y2); y++)
                for (int z = Math.min(z1, z2); z <= Math.max(z1, z2); z++)
                    set(x, y, z, s);
    }

    public void fillAir(int x1, int y1, int z1, int x2, int y2, int z2) {
        fill(x1, y1, z1, x2, y2, z2, Blocks.AIR.defaultBlockState());
    }

    /** Filled disk in the XZ plane. */
    public void disk(int cx, int y, int cz, double r, Palette p) {
        int ri = (int) Math.ceil(r);
        for (int x = -ri; x <= ri; x++)
            for (int z = -ri; z <= ri; z++)
                if (x * x + z * z <= r * r) set(cx + x, y, cz + z, p.pick(random));
    }

    /** Ring (hollow cylinder wall) between inner and outer radius. */
    public void ring(int cx, int y, int cz, double inner, double outer, Palette p) {
        int ri = (int) Math.ceil(outer);
        for (int x = -ri; x <= ri; x++)
            for (int z = -ri; z <= ri; z++) {
                double d2 = x * x + z * z;
                if (d2 <= outer * outer && d2 >= inner * inner) set(cx + x, y, cz + z, p.pick(random));
            }
    }

    /** Hemisphere shell. */
    public void dome(int cx, int cy, int cz, double r, double thickness, Palette p) {
        int ri = (int) Math.ceil(r);
        for (int x = -ri; x <= ri; x++)
            for (int y = 0; y <= ri; y++)
                for (int z = -ri; z <= ri; z++) {
                    double d = Math.sqrt(x * x + y * y + z * z);
                    if (d <= r && d >= r - thickness) set(cx + x, cy + y, cz + z, p.pick(random));
                }
    }

    /** Thick line (capsule) between two points. */
    public void line(double x1, double y1, double z1, double x2, double y2, double z2, double radius, Palette p) {
        double len = Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1) + (z2 - z1) * (z2 - z1));
        int steps = Math.max(1, (int) (len * 3));
        int ri = (int) Math.ceil(radius);
        for (int i = 0; i <= steps; i++) {
            double t = i / (double) steps;
            double px = x1 + (x2 - x1) * t, py = y1 + (y2 - y1) * t, pz = z1 + (z2 - z1) * t;
            for (int dx = -ri; dx <= ri; dx++)
                for (int dy = -ri; dy <= ri; dy++)
                    for (int dz = -ri; dz <= ri; dz++)
                        if (dx * dx + dy * dy + dz * dz <= radius * radius + 0.01)
                            set((int) Math.round(px + dx), (int) Math.round(py + dy), (int) Math.round(pz + dz), p.pick(random));
        }
    }

    public void chest(int x, int y, int z, Direction facing, ResourceKey<LootTable> loot) {
        chests.add(new Chest(new BlockPos(x, y, z), facing, loot));
        grow(x, y, z);
    }

    public void spawner(int x, int y, int z, Supplier<? extends EntityType<?>> type) {
        spawners.add(new Spawner(new BlockPos(x, y, z), type));
        grow(x, y, z);
    }

    public void mob(int x, int y, int z, Supplier<? extends EntityType<?>> type) {
        mobs.add(new Mob(new BlockPos(x, y, z), type));
    }

    public static BlockState stairs(BlockState base, Direction facing) {
        return base.setValue(StairBlock.FACING, facing);
    }

    /** Horizontal direction pointing from the centre towards (x, z). */
    public static Direction outward(double x, double z) {
        if (Math.abs(x) > Math.abs(z)) return x > 0 ? Direction.EAST : Direction.WEST;
        return z > 0 ? Direction.SOUTH : Direction.NORTH;
    }

    /** Weighted random block palette. */
    public static final class Palette {
        private final List<BlockState> states = new ArrayList<>();
        private final List<Integer> weights = new ArrayList<>();
        private int total;

        public static Palette of(BlockState s) {
            return new Palette().add(s, 1);
        }

        public Palette add(BlockState s, int weight) {
            states.add(s);
            weights.add(weight);
            total += weight;
            return this;
        }

        public BlockState pick(RandomSource random) {
            if (states.size() == 1) return states.get(0);
            int r = random.nextInt(total);
            for (int i = 0; i < states.size(); i++) {
                r -= weights.get(i);
                if (r < 0) return states.get(i);
            }
            return states.get(0);
        }
    }
}
