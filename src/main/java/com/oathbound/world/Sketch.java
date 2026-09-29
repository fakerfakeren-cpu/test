package com.oathbound.world;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * A structure drawn in local coordinates before it touches the world: a sparse map of block states plus
 * markers for loot chests, spawners and resident creatures. Sketches are pure functions of their seed, so
 * world generation can redraw them for each chunk it decorates.
 */
public final class Sketch {
    public record Loot(BlockPos pos, Direction facing, ResourceKey<LootTable> table) {}

    public record Spawner(BlockPos pos, Supplier<? extends EntityType<?>> type) {}

    public record Resident(BlockPos pos, Supplier<? extends EntityType<?>> type, float yaw) {}

    final Map<BlockPos, BlockState> blocks = new HashMap<>();
    /** Columns (x, z at local y = 0) under which a footing is poured down to the ground. */
    final Set<Long> footings = new HashSet<>();
    BlockState footing = Blocks.COBBLESTONE.defaultBlockState();
    /** How far below the build a footing may reach for ground before the column is left unsupported. */
    int footingDepth = 24;
    final List<Loot> loot = new ArrayList<>();
    final List<Spawner> spawners = new ArrayList<>();
    final List<Resident> residents = new ArrayList<>();
    public final RandomSource rng;
    private int x0 = Integer.MAX_VALUE, y0 = Integer.MAX_VALUE, z0 = Integer.MAX_VALUE;
    private int x1 = Integer.MIN_VALUE, y1 = Integer.MIN_VALUE, z1 = Integer.MIN_VALUE;

    public Sketch(long seed) {
        this.rng = RandomSource.create(seed);
    }

    private void include(int x, int y, int z) {
        if (x < x0) x0 = x;
        if (y < y0) y0 = y;
        if (z < z0) z0 = z;
        if (x > x1) x1 = x;
        if (y > y1) y1 = y;
        if (z > z1) z1 = z;
    }

    /** Local bounds, extended downward to leave room for footings. */
    public BoundingBox bounds() {
        return new BoundingBox(x0, y0 - (footings.isEmpty() ? 0 : 24), z0, x1, y1, z1);
    }

    // ------------------------------------------------------------------ primitives
    public Sketch put(int x, int y, int z, BlockState s) {
        blocks.put(new BlockPos(x, y, z), s);
        include(x, y, z);
        return this;
    }

    public Sketch put(int x, int y, int z, Mix mix) {
        return put(x, y, z, mix.pick(rng));
    }

    public BlockState at(int x, int y, int z) {
        return blocks.get(new BlockPos(x, y, z));
    }

    public Sketch clear(int x, int y, int z) {
        return put(x, y, z, Blocks.AIR.defaultBlockState());
    }

    public Sketch box(int ax, int ay, int az, int bx, int by, int bz, Mix mix) {
        for (int x = Math.min(ax, bx); x <= Math.max(ax, bx); x++)
            for (int y = Math.min(ay, by); y <= Math.max(ay, by); y++)
                for (int z = Math.min(az, bz); z <= Math.max(az, bz); z++)
                    put(x, y, z, mix);
        return this;
    }

    public Sketch box(int ax, int ay, int az, int bx, int by, int bz, BlockState s) {
        return box(ax, ay, az, bx, by, bz, Mix.of(s));
    }

    public Sketch hollow(int ax, int ay, int az, int bx, int by, int bz) {
        return box(ax, ay, az, bx, by, bz, Blocks.AIR.defaultBlockState());
    }

    /** Four walls of a box (no floor or ceiling). */
    public Sketch walls(int ax, int ay, int az, int bx, int by, int bz, Mix mix) {
        box(ax, ay, az, bx, by, az, mix);
        box(ax, ay, bz, bx, by, bz, mix);
        box(ax, ay, az, ax, by, bz, mix);
        box(bx, ay, az, bx, by, bz, mix);
        return this;
    }

    /** Filled disc (y constant). */
    public Sketch disc(int cx, int y, int cz, double r, Mix mix) {
        int ri = (int) Math.ceil(r);
        for (int dx = -ri; dx <= ri; dx++)
            for (int dz = -ri; dz <= ri; dz++)
                if (dx * dx + dz * dz <= r * r + 0.3) put(cx + dx, y, cz + dz, mix);
        return this;
    }

    /** Annulus between two radii (y constant). */
    public Sketch annulus(int cx, int y, int cz, double inner, double outer, Mix mix) {
        int ri = (int) Math.ceil(outer);
        for (int dx = -ri; dx <= ri; dx++)
            for (int dz = -ri; dz <= ri; dz++) {
                double d = dx * dx + dz * dz;
                if (d <= outer * outer + 0.3 && d >= inner * inner - 0.3) put(cx + dx, y, cz + dz, mix);
            }
        return this;
    }

    /** Upper hemisphere shell (radius r, wall thickness t). */
    public Sketch dome(int cx, int cy, int cz, double r, double t, Mix mix) {
        int ri = (int) Math.ceil(r);
        for (int dx = -ri; dx <= ri; dx++)
            for (int dy = 0; dy <= ri; dy++)
                for (int dz = -ri; dz <= ri; dz++) {
                    double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
                    if (d <= r && d > r - t) put(cx + dx, cy + dy, cz + dz, mix);
                }
        return this;
    }

    /** Solid squashed half-ellipsoid (burial mounds). */
    public Sketch mound(int cx, int cy, int cz, double rx, double ry, Mix shell, Mix fill) {
        int ri = (int) Math.ceil(rx);
        for (int dx = -ri; dx <= ri; dx++)
            for (int dz = -ri; dz <= ri; dz++) {
                double h = 1 - (dx * dx + dz * dz) / (rx * rx);
                if (h <= 0) continue;
                int top = (int) Math.round(Math.sqrt(h) * ry);
                for (int y = 0; y <= top; y++) put(cx + dx, cy + y, cz + dz, y == top ? shell : fill);
                footing(cx + dx, cz + dz);
            }
        return this;
    }

    public Sketch footing(int x, int z) {
        footings.add(BlockPos.asLong(x, 0, z));
        return this;
    }

    public Sketch footingUnder(int ax, int az, int bx, int bz) {
        for (int x = Math.min(ax, bx); x <= Math.max(ax, bx); x++)
            for (int z = Math.min(az, bz); z <= Math.max(az, bz); z++) footing(x, z);
        return this;
    }

    public Sketch footingState(BlockState s) {
        this.footing = s;
        return this;
    }

    public Sketch footingDepth(int depth) {
        this.footingDepth = depth;
        return this;
    }

    /**
     * The rocky underside of a floating island: an inverted, ragged cone hanging below a disc of radius
     * {@code r} centred at (cx, y, cz).
     */
    public Sketch underside(int cx, int y, int cz, double r, int depth, Mix rock) {
        for (int d = 1; d <= depth; d++) {
            double t = d / (double) (depth + 1);
            double rr = r * Math.pow(1 - t, 0.7);
            int ri = (int) Math.ceil(rr + 1);
            for (int dx = -ri; dx <= ri; dx++)
                for (int dz = -ri; dz <= ri; dz++) {
                    double jag = (rng.nextDouble() - 0.5) * 1.6;
                    if (dx * dx + dz * dz <= (rr + jag) * (rr + jag)) put(cx + dx, y - d, cz + dz, rock);
                }
        }
        return this;
    }

    // ------------------------------------------------------------------ markers
    public Sketch chest(int x, int y, int z, Direction facing, ResourceKey<LootTable> table) {
        loot.add(new Loot(new BlockPos(x, y, z), facing, table));
        blocks.remove(new BlockPos(x, y, z));
        include(x, y, z);
        return this;
    }

    public Sketch spawner(int x, int y, int z, Supplier<? extends EntityType<?>> type) {
        spawners.add(new Spawner(new BlockPos(x, y, z), type));
        blocks.remove(new BlockPos(x, y, z));
        include(x, y, z);
        return this;
    }

    public Sketch resident(int x, int y, int z, Supplier<? extends EntityType<?>> type, float yaw) {
        residents.add(new Resident(new BlockPos(x, y, z), type, yaw));
        return this;
    }

    // ------------------------------------------------------------------ weathering
    /** Randomly swaps matching blocks, e.g. to crack and moss a ruin. */
    public Sketch weather(Predicate<BlockState> match, Mix into, float chance) {
        for (var e : blocks.entrySet()) {
            if (match.test(e.getValue()) && rng.nextFloat() < chance) e.setValue(into.pick(rng));
        }
        return this;
    }

    /** Knocks holes into the top of walls above {@code minY} for a ruined silhouette. */
    public Sketch crumble(int minY, float chance) {
        List<BlockPos> tops = new ArrayList<>();
        for (var e : blocks.entrySet()) {
            BlockPos p = e.getKey();
            if (p.getY() >= minY && !e.getValue().isAir() && !blocks.containsKey(p.above())) tops.add(p);
        }
        for (BlockPos p : tops) {
            if (rng.nextFloat() >= chance) continue;
            int depth = 1 + rng.nextInt(3);
            for (int i = 0; i < depth && p.getY() - i >= minY; i++) blocks.put(p.below(i), Blocks.AIR.defaultBlockState());
        }
        return this;
    }

    /** A weighted palette of block states. */
    public static final class Mix {
        private final List<BlockState> states = new ArrayList<>();
        private final List<Integer> weights = new ArrayList<>();
        private int total;

        public static Mix of(BlockState s) {
            return new Mix().and(s, 1);
        }

        public Mix and(BlockState s, int weight) {
            states.add(s);
            weights.add(weight);
            total += weight;
            return this;
        }

        public BlockState pick(RandomSource r) {
            if (states.size() == 1) return states.get(0);
            int n = r.nextInt(total);
            for (int i = 0; i < states.size(); i++) {
                n -= weights.get(i);
                if (n < 0) return states.get(i);
            }
            return states.get(states.size() - 1);
        }
    }
}
