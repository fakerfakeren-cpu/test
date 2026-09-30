package com.oathbound.world;

import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.world.Sketch.Mix;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CandleBlock;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.LayeredCauldronBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RailBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.RailShape;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraftforge.registries.RegistryObject;

/**
 * The places off the Path: seven sites in seven kinds of country, none of them like another. Three hold the wild
 * keepers (the Elderhorn, the Bog Mother and the Cinder Colossus); the rest hold what the old kingdom left behind.
 */
final class WildSketches {
    private WildSketches() {}

    // ------------------------------------------------------------------ palette helpers
    private static BlockState st(Block b) {
        return b.defaultBlockState();
    }

    private static BlockState st(RegistryObject<Block> b) {
        return b.get().defaultBlockState();
    }

    private static BlockState stairs(Block b, Direction facing) {
        return b.defaultBlockState().setValue(StairBlock.FACING, facing);
    }

    private static BlockState stairs(RegistryObject<Block> b, Direction facing) {
        return stairs(b.get(), facing);
    }

    private static BlockState slab(Block b, SlabType t) {
        return b.defaultBlockState().setValue(SlabBlock.TYPE, t);
    }

    private static BlockState slab(RegistryObject<Block> b, SlabType t) {
        return slab(b.get(), t);
    }

    private static BlockState log(Block b, Direction.Axis axis) {
        return b.defaultBlockState().setValue(RotatedPillarBlock.AXIS, axis);
    }

    private static BlockState leaves(Block b) {
        return b.defaultBlockState().setValue(LeavesBlock.PERSISTENT, true);
    }

    private static BlockState hanging(Block b) {
        return b.defaultBlockState().setValue(LanternBlock.HANGING, true);
    }

    private static BlockState ladder(Direction facing) {
        return Blocks.LADDER.defaultBlockState().setValue(LadderBlock.FACING, facing);
    }

    private static BlockState candles(int n) {
        return Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.CANDLES, n).setValue(CandleBlock.LIT, true);
    }

    private static final Mix AIR = Mix.of(Blocks.AIR.defaultBlockState());

    /** Clears a cylinder of air above a site so hillsides do not bury it. */
    private static void clearAbove(Sketch s, double r, int from, int to) {
        for (int y = from; y <= to; y++) s.disc(0, y, 0, r, AIR);
    }

    // ================================================================== The Stag's Ring (Elderhorn)
    /**
     * A ring of leaning runestones in a flowering glade, around a mossy dais where the Grove King sleeps. A great
     * hollow oak stands inside the ring; an arch of bleached antlers marks the way in.
     */
    static void groveShrine(Sketch s) {
        Mix floor = Mix.of(st(Blocks.GRASS_BLOCK)).and(st(Blocks.GRASS_BLOCK), 6).and(st(Blocks.MOSS_BLOCK), 4).and(st(Blocks.PODZOL), 2)
            .and(st(Blocks.ROOTED_DIRT), 1);
        Mix rune = Mix.of(st(ModBlocks.RUNESTONE)).and(st(ModBlocks.RUNESTONE), 3).and(st(ModBlocks.RUNESTONE_BRICKS), 1)
            .and(st(Blocks.MOSSY_COBBLESTONE), 1);
        s.footingState(st(Blocks.DIRT));
        s.disc(0, 0, 0, 12.5, floor);
        for (int x = -12; x <= 12; x++)
            for (int z = -12; z <= 12; z++)
                if (x * x + z * z <= 12.5 * 12.5) s.footing(x, z);
        clearAbove(s, 12.5, 1, 9);
        // meadow cover
        BlockState[] blooms = {st(ModBlocks.MOONPETAL), st(ModBlocks.DUSK_LILY), st(Blocks.CORNFLOWER), st(Blocks.OXEYE_DAISY),
            st(Blocks.AZURE_BLUET), st(Blocks.LILY_OF_THE_VALLEY), st(Blocks.ALLIUM)};
        for (int x = -12; x <= 12; x++)
            for (int z = -12; z <= 12; z++) {
                double d = Math.sqrt(x * x + z * z);
                if (d > 12.2) continue;
                if (s.at(x, 0, z) == null || !s.at(x, 0, z).is(Blocks.GRASS_BLOCK) && !s.at(x, 0, z).is(Blocks.MOSS_BLOCK)) continue;
                float r = s.rng.nextFloat();
                boolean flowerRing = d > 5.5 && d < 7.8;
                if (flowerRing && r < 0.55f) s.put(x, 1, z, blooms[s.rng.nextInt(blooms.length)]);
                else if (r < 0.28f) s.put(x, 1, z, st(Blocks.SHORT_GRASS));
                else if (r < 0.33f) s.put(x, 1, z, st(Blocks.FERN));
                else if (r < 0.37f) s.put(x, 1, z, st(ModBlocks.GLIMMER_MOSS));
                else if (r < 0.40f) s.put(x, 1, z, st(Blocks.MOSS_CARPET));
            }
        // nine standing stones, a few leaning, a few fallen
        for (int i = 0; i < 9; i++) {
            if (i == 0) continue;   // the gap faces the antler arch
            double a = i * Math.PI * 2 / 9 + Math.PI / 2 + (s.rng.nextDouble() - 0.5) * 0.12;
            int x = (int) Math.round(Math.cos(a) * 9.5), z = (int) Math.round(Math.sin(a) * 9.5);
            if (s.rng.nextFloat() < 0.15f) {
                // fallen: lying along the ring
                int dx = Math.abs(Math.cos(a)) > 0.7 ? 0 : 1, dz = 1 - dx;
                for (int k = 0; k < 4; k++) s.put(x + dx * k, 1, z + dz * k, rune);
                s.put(x + dx * 2, 2, z + dz * 2, st(Blocks.MOSS_CARPET));
                continue;
            }
            int h = 3 + s.rng.nextInt(3);
            s.box(x, 1, z, x, h, z, rune);
            if (s.rng.nextBoolean()) s.box(x + (x > 0 ? -1 : 1), 1, z, x + (x > 0 ? -1 : 1), h - 1, z, rune);
            // leaning: the top steps outward
            int lx = s.rng.nextFloat() < 0.35f ? (x > 0 ? 1 : -1) : 0;
            s.put(x + lx, h + 1, z, st(ModBlocks.GLYPHED_RUNESTONE));
            if (s.rng.nextBoolean()) s.put(x + lx, h + 2, z, st(Blocks.MOSS_CARPET));
            s.put(x + (x > 0 ? -1 : 1), 1, z + (z > 0 ? -1 : 1), st(ModBlocks.GLIMMER_MOSS));
        }
        // the dais
        s.disc(0, 0, 0, 4.2, Mix.of(st(ModBlocks.RUNESTONE_BRICKS)).and(st(Blocks.MOSSY_STONE_BRICKS), 1));
        s.annulus(0, 1, 0, 2.9, 4.2, Mix.of(slab(ModBlocks.RUNESTONE_BRICK_SLAB, SlabType.BOTTOM)));
        s.disc(0, 1, 0, 2.9, Mix.of(st(ModBlocks.RUNESTONE_BRICKS)).and(st(Blocks.MOSS_BLOCK), 1));
        s.put(0, 1, 0, st(ModBlocks.GLYPHED_RUNESTONE));
        for (int[] c : new int[][]{{-2, -2}, {2, -2}, {-2, 2}, {2, 2}}) s.put(c[0], 2, c[1], candles(1 + s.rng.nextInt(3)));
        s.resident(0, 2, 0, ModEntities.ELDERHORN, 0f);
        // the great hollow oak, north-east inside the ring
        int tx = 5, tz = -6;
        s.box(tx - 1, 1, tz - 1, tx + 1, 10, tz + 1, log(Blocks.OAK_LOG, Direction.Axis.Y));
        s.hollow(tx, 1, tz, tx, 3, tz);
        s.hollow(tx, 1, tz + 1, tx, 2, tz + 1);
        s.chest(tx, 1, tz, Direction.SOUTH, Sketches.loot("grove_offering"));
        s.put(tx, 3, tz, st(Blocks.SHROOMLIGHT));
        for (int[] r : new int[][]{{-2, 0, 0}, {2, 0, 0}, {0, 0, -2}, {0, 0, 2}}) {
            // flaring roots
            s.put(tx + r[0], 1, tz + r[2], log(Blocks.OAK_LOG, r[0] != 0 ? Direction.Axis.X : Direction.Axis.Z));
            s.put(tx + r[0] * 3 / 2, 0, tz + r[2] * 3 / 2, st(Blocks.ROOTED_DIRT));
        }
        s.put(tx, 1, tz + 2, st(Blocks.AIR));
        for (int[] b : new int[][]{{0, 11, 0, 5}, {-3, 9, 2, 3}, {3, 10, -2, 3}, {1, 13, -1, 3}}) {
            int bx = tx + b[0], by = b[1], bz = tz + b[2], r = b[3];
            for (int dx = -r; dx <= r; dx++)
                for (int dy = -r + 1; dy <= r - 1; dy++)
                    for (int dz = -r; dz <= r; dz++) {
                        double d = dx * dx / (double) (r * r) + dy * dy / (double) ((r - 1) * (r - 1)) + dz * dz / (double) (r * r);
                        if (d <= 1.0 && s.rng.nextFloat() < (d > 0.7 ? 0.75f : 1f) && s.at(bx + dx, by + dy, bz + dz) == null)
                            s.put(bx + dx, by + dy, bz + dz, leaves(Blocks.OAK_LEAVES));
                    }
        }
        s.box(tx - 3, 10, tz, tx + 3, 10, tz, log(Blocks.OAK_LOG, Direction.Axis.X));
        s.box(tx, 10, tz - 3, tx, 10, tz + 3, log(Blocks.OAK_LOG, Direction.Axis.Z));
        // the antler arch at the gap in the ring (south)
        int az = 10;
        for (int side = -1; side <= 1; side += 2) {
            int x = 2 * side;
            s.box(x, 1, az, x, 4, az, st(Blocks.BONE_BLOCK));
            s.put(x, 5, az, st(Blocks.BONE_BLOCK));
            s.put(side, 6, az, st(Blocks.BONE_BLOCK));
            s.put(3 * side, 5, az, st(Blocks.BONE_BLOCK));
            s.put(3 * side, 6, az, st(Blocks.BONE_BLOCK));
            s.put(4 * side, 6, az, st(Blocks.BONE_BLOCK));
            s.put(2 * side, 7, az, st(Blocks.BONE_BLOCK));
            s.put(3 * side, 3, az, st(Blocks.BONE_BLOCK));
            s.put(x, 1, az + 1, st(ModBlocks.GLIMMER_MOSS));
        }
        s.put(0, 6, az, st(ModBlocks.GLYPHED_RUNESTONE));
        s.put(0, 5, az, hanging(Blocks.LANTERN));
    }

    // ================================================================== The Bog Mother's stilt-house
    /**
     * A crooked house on mangrove stilts over the black water, its roof furred with moss and hung with roots. Two
     * green lamps burn on the deck; a boardwalk runs down to the shallows.
     */
    static void bogHut(Sketch s) {
        Mix planks = Mix.of(st(Blocks.MANGROVE_PLANKS)).and(st(Blocks.MANGROVE_PLANKS), 5).and(st(Blocks.MUD_BRICKS), 1);
        Mix wall = Mix.of(st(Blocks.MUD_BRICKS)).and(st(Blocks.MUD_BRICKS), 3).and(st(Blocks.MANGROVE_PLANKS), 2).and(st(Blocks.PACKED_MUD), 1);
        s.footingState(st(Blocks.MANGROVE_ROOTS));
        s.footingDepth(12);
        // stilts
        for (int[] p : new int[][]{{-5, -5}, {5, -5}, {-5, 5}, {5, 5}, {0, -5}, {0, 5}, {-5, 0}, {5, 0}}) {
            s.box(p[0], -5, p[1], p[0], 3, p[1], log(Blocks.MANGROVE_LOG, Direction.Axis.Y));
            s.footing(p[0], p[1]);
            s.put(p[0] + (p[0] > 0 ? 1 : p[0] < 0 ? -1 : 0), 0, p[1] + (p[1] > 0 ? 1 : p[1] < 0 ? -1 : 0), st(Blocks.MANGROVE_ROOTS));
        }
        // deck and railing
        s.box(-6, 4, -6, 6, 4, 6, planks);
        for (int x = -6; x <= 6; x++)
            for (int z = -6; z <= 6; z++) {
                boolean edge = Math.abs(x) == 6 || Math.abs(z) == 6;
                if (edge && !(z == 6 && Math.abs(x) <= 1)) s.put(x, 5, z, st(Blocks.MANGROVE_FENCE));
                if (edge && s.rng.nextFloat() < 0.4f) s.put(x, 3, z, st(Blocks.HANGING_ROOTS));
            }
        // the house
        s.box(-3, 5, -3, 3, 9, 3, wall);
        for (int[] c : new int[][]{{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) s.box(c[0], 5, c[1], c[0], 9, c[1], log(Blocks.STRIPPED_MANGROVE_LOG, Direction.Axis.Y));
        s.hollow(-2, 5, -2, 2, 12, 2);
        s.hollow(0, 5, 3, 0, 6, 3);
        s.put(-3, 7, 0, st(Blocks.STAINED_GLASS.green()));
        s.put(3, 7, 0, st(Blocks.STAINED_GLASS.green()));
        s.put(0, 7, -3, st(Blocks.STAINED_GLASS.lime()));
        // roof: a steep gable along x, mossed and hung with roots
        for (int k = 0; k <= 3; k++) {
            s.box(-4, 10 + k, -4 + k, 4, 10 + k, -4 + k, stairs(Blocks.DARK_OAK_STAIRS, Direction.SOUTH));
            s.box(-4, 10 + k, 4 - k, 4, 10 + k, 4 - k, stairs(Blocks.DARK_OAK_STAIRS, Direction.NORTH));
            s.box(-3, 10 + k, -3 + k, -3, 10 + k, 3 - k, wall);
            s.box(3, 10 + k, -3 + k, 3, 10 + k, 3 - k, wall);
        }
        s.box(-4, 13, 0, 4, 13, 0, st(Blocks.DARK_OAK_PLANKS));
        s.box(-4, 14, 0, 4, 14, 0, slab(Blocks.DARK_OAK_SLAB, SlabType.BOTTOM));
        for (int x = -4; x <= 4; x++)
            for (int z = -4; z <= 4; z++) {
                if (s.rng.nextFloat() < 0.3f) {
                    int top = 14;
                    while (top > 9 && s.at(x, top, z) == null) top--;
                    if (top > 9 && s.at(x, top + 1, z) == null) s.put(x, top + 1, z, st(Blocks.MOSS_CARPET));
                }
            }
        for (int x = -4; x <= 4; x += 2) {
            s.put(x, 9, -4, st(Blocks.HANGING_ROOTS));
            s.put(x, 9, 4, st(Blocks.HANGING_ROOTS));
        }
        // her two green lamps
        for (int side = -1; side <= 1; side += 2) {
            s.box(4 * side, 5, 5, 4 * side, 7, 5, st(Blocks.MANGROVE_FENCE));
            s.put(4 * side, 8, 5, st(Blocks.VERDANT_FROGLIGHT));
        }
        // inside: the cauldron, the brewing, the larder
        s.put(-2, 5, -2, Blocks.WATER_CAULDRON.defaultBlockState().setValue(LayeredCauldronBlock.LEVEL, 3));
        s.put(-1, 5, -2, st(Blocks.BREWING_STAND));
        s.put(2, 5, 1, st(Blocks.BARREL));
        s.put(2, 6, 1, st(Blocks.SKELETON_SKULL));
        s.chest(2, 5, -1, Direction.WEST, Sketches.loot("bog_hut_larder"));
        s.put(-2, 5, 1, st(Blocks.BONE_BLOCK));
        s.put(-2, 6, 1, candles(3));
        s.put(1, 5, -2, candles(2));
        s.put(0, 9, 0, st(Blocks.VERDANT_FROGLIGHT));
        s.put(-1, 9, 1, st(Blocks.HANGING_ROOTS));
        s.put(1, 9, -1, st(Blocks.HANGING_ROOTS));
        s.resident(0, 5, 0, ModEntities.BOG_MOTHER, 0f);
        // the boardwalk down to the shallows
        s.put(0, 4, 7, st(Blocks.MANGROVE_PLANKS));
        for (int k = 0; k < 3; k++) {
            s.box(-1, 3 - k, 8 + k, 1, 3 - k, 8 + k, stairs(Blocks.MANGROVE_STAIRS, Direction.NORTH));
            s.box(-1, 4 - k, 8 + k, 1, 6 - k, 8 + k, AIR);
        }
        s.box(-1, 1, 11, 1, 1, 15, slab(Blocks.MANGROVE_SLAB, SlabType.TOP));
        for (int z = 11; z <= 15; z += 2) {
            s.box(-2, -4, z, -2, 1, z, log(Blocks.MANGROVE_LOG, Direction.Axis.Y));
            s.box(2, -4, z, 2, 1, z, log(Blocks.MANGROVE_LOG, Direction.Axis.Y));
            s.footing(-2, z);
            s.footing(2, z);
        }
        s.put(-2, 2, 15, st(Blocks.MANGROVE_FENCE));
        s.put(-2, 3, 15, st(Blocks.VERDANT_FROGLIGHT));
        s.put(2, 2, 13, st(Blocks.SKELETON_SKULL));
        // lily pads and floating moss around the stilts
        for (int i = 0; i < 18; i++) {
            int x = s.rng.nextInt(17) - 8, z = s.rng.nextInt(17) - 8;
            if (Math.abs(x) <= 6 && Math.abs(z) <= 6 && s.rng.nextBoolean()) continue;
            if (s.at(x, 1, z) == null) s.put(x, 1, z, st(Blocks.LILY_PAD));
        }
    }

    // ================================================================== The Sun-Cult's sanctum (Cinder Colossus)
    /**
     * A stepped sandstone pyramid with a fire burning on its crown, and under it a hall of black stone and magma
     * where the Colossus still stokes itself. A long stair runs down from the desert floor.
     */
    static void cinderSanctum(Sketch s) {
        Mix sand = Mix.of(st(Blocks.SANDSTONE)).and(st(Blocks.SANDSTONE), 5).and(st(Blocks.CUT_SANDSTONE), 3).and(st(Blocks.SMOOTH_SANDSTONE), 2);
        Mix red = Mix.of(st(Blocks.RED_SANDSTONE)).and(st(Blocks.CUT_RED_SANDSTONE), 1);
        Mix black = Mix.of(st(Blocks.POLISHED_BLACKSTONE_BRICKS)).and(st(Blocks.POLISHED_BLACKSTONE_BRICKS), 6)
            .and(st(Blocks.CRACKED_POLISHED_BLACKSTONE_BRICKS), 3).and(st(Blocks.GILDED_BLACKSTONE), 1).and(st(Blocks.BLACKSTONE), 2);
        s.footingState(st(Blocks.SANDSTONE));
        int cz = -4;
        // the pyramid: four tiers, the lowest half-buried
        int[][] tiers = {{0, 11}, {2, 9}, {4, 7}, {6, 5}};
        for (int[] t : tiers) {
            int y = t[0], r = t[1];
            s.box(-r, y, cz - r, r, y + 1, cz + r, t[0] == 6 ? Mix.of(st(Blocks.CUT_SANDSTONE)) : sand);
            // a red band on each tier's lip
            for (int x = -r; x <= r; x++) {
                s.put(x, y + 1, cz - r, red);
                s.put(x, y + 1, cz + r, red);
            }
            for (int z = cz - r; z <= cz + r; z++) {
                s.put(-r, y + 1, z, red);
                s.put(r, y + 1, z, red);
            }
        }
        s.footingUnder(-11, cz - 11, 11, cz + 11);
        // the crown: a sun disc and a fire that is never allowed to go out
        s.disc(0, 7, cz, 3.2, Mix.of(st(Blocks.GLAZED_TERRACOTTA.orange())).and(st(Blocks.GLAZED_TERRACOTTA.yellow()), 1));
        s.put(0, 7, cz, st(Blocks.GOLD_BLOCK));
        s.put(0, 8, cz, st(Blocks.CAMPFIRE));
        for (int[] c : new int[][]{{-4, -4}, {4, -4}, {-4, 4}, {4, 4}}) {
            s.box(c[0], 8, cz + c[1], c[0], 10, cz + c[1], st(Blocks.CUT_RED_SANDSTONE));
            s.put(c[0], 11, cz + c[1], st(Blocks.CHISELED_RED_SANDSTONE));
            s.put(c[0], 12, cz + c[1], st(Blocks.CAMPFIRE));
        }
        // obelisks at the corners of the base
        for (int[] c : new int[][]{{-13, -13}, {13, -13}, {-13, 13}, {13, 13}}) {
            s.box(c[0], 0, cz + c[1], c[0], 6, cz + c[1], sand);
            s.put(c[0], 7, cz + c[1], st(Blocks.CHISELED_SANDSTONE));
            s.put(c[0], 8, cz + c[1], slab(Blocks.SANDSTONE_SLAB, SlabType.BOTTOM));
            s.footing(c[0], cz + c[1]);
        }
        // the buried hall
        int floor = -12;
        s.box(-10, floor, cz - 10, 10, -1, cz + 9, black);
        s.hollow(-9, floor + 1, cz - 9, 9, -3, cz + 8);
        // magma channels either side, lava sealed below a curb
        for (int side = -1; side <= 1; side += 2) {
            s.box(7 * side, floor, cz - 8, 8 * side, floor, cz + 6, st(Blocks.MAGMA_BLOCK));
            s.box(7 * side, floor + 1, cz - 8, 8 * side, floor + 1, cz + 6, st(Blocks.LAVA));
            s.box(6 * side, floor + 1, cz - 8, 6 * side, floor + 1, cz + 6, st(Blocks.POLISHED_BLACKSTONE_BRICK_WALL));
            s.box(7 * side, floor + 1, cz + 7, 8 * side, floor + 1, cz + 7, black);
            s.box(7 * side, floor + 1, cz - 9, 8 * side, floor + 1, cz - 9, black);
            s.box(9 * side, floor + 1, cz - 9, 9 * side, floor + 1, cz + 8, black);
        }
        // basalt pillars with braziers
        for (int side = -1; side <= 1; side += 2)
            for (int z : new int[]{cz - 6, cz - 1, cz + 4}) {
                s.box(4 * side, floor + 1, z, 4 * side, -3, z, log(Blocks.POLISHED_BASALT, Direction.Axis.Y));
                s.put(4 * side, floor + 5, z + 1, st(Blocks.LANTERN));
                s.put(4 * side, floor + 4, z + 1, st(Blocks.POLISHED_BLACKSTONE_BRICK_WALL));
                s.put(4 * side, floor + 3, z + 1, st(Blocks.POLISHED_BLACKSTONE_BRICK_WALL));
                s.put(4 * side, floor + 2, z + 1, st(Blocks.POLISHED_BLACKSTONE_BRICK_WALL));
                s.put(4 * side, floor + 1, z + 1, st(Blocks.POLISHED_BLACKSTONE_BRICKS));
            }
        // the sun altar at the north end
        s.box(-3, floor + 1, cz - 9, 3, floor + 1, cz - 7, st(Blocks.GILDED_BLACKSTONE));
        s.box(-3, floor + 2, cz - 6, 3, floor + 2, cz - 6, stairs(Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS, Direction.NORTH));
        s.box(-3, floor + 1, cz - 6, 3, floor + 1, cz - 6, black);
        s.put(0, floor + 2, cz - 8, st(Blocks.GOLD_BLOCK));
        s.put(0, floor + 3, cz - 8, st(Blocks.CAMPFIRE));
        s.disc(0, floor + 1, cz - 1, 2.5, Mix.of(st(Blocks.GLAZED_TERRACOTTA.orange())));
        s.box(-1, floor + 3, cz - 10, 1, floor + 7, cz - 10, st(Blocks.CHISELED_RED_SANDSTONE));
        s.chest(0, floor + 2, cz - 9, Direction.SOUTH, Sketches.loot("cinder_sanctum_vault"));
        s.chest(-3, floor + 2, cz - 8, Direction.EAST, Sketches.loot("cinder_sanctum_offerings"));
        s.chest(3, floor + 2, cz - 8, Direction.WEST, Sketches.loot("cinder_sanctum_offerings"));
        s.resident(0, floor + 1, cz - 1, ModEntities.CINDER_COLOSSUS, 0f);
        // ash drifts
        for (int i = 0; i < 20; i++) {
            int x = s.rng.nextInt(11) - 5, z = cz + s.rng.nextInt(15) - 6;
            if (s.at(x, floor + 1, z) == null) s.put(x, floor + 1, z, st(Blocks.SOUL_SAND));
        }
        // the long stair down from the south, roofed
        for (int k = 0; k <= 10; k++) {
            int z = cz + 19 - k, y = -k;
            s.box(-2, y - 1, z, 2, y + 4, z, sand);
            s.box(-1, y, z, 1, y, z, stairs(Blocks.SANDSTONE_STAIRS, Direction.NORTH));
            s.box(-1, y + 1, z, 1, y + 3, z, AIR);
            if (k % 3 == 1) s.put(2, y + 2, z, st(Blocks.LANTERN));
        }
        s.hollow(-1, floor + 1, cz + 8, 1, floor + 4, cz + 9);
        s.hollow(-1, -10, cz + 9, 1, -8, cz + 9);
        // the door-frame at the top of the stair
        s.box(-3, 0, cz + 19, 3, 5, cz + 19, Mix.of(st(Blocks.CHISELED_SANDSTONE)).and(st(Blocks.CUT_SANDSTONE), 2));
        s.hollow(-1, 1, cz + 19, 1, 3, cz + 19);
        s.put(0, 5, cz + 19, st(Blocks.GLAZED_TERRACOTTA.orange()));
        s.footingUnder(-3, cz + 12, 3, cz + 19);
        s.resident(-2, 1, cz + 21, () -> EntityTypes.HUSK, 180f);
        s.resident(3, 1, cz + 22, () -> EntityTypes.HUSK, 200f);
    }

    // ================================================================== The Last Watch
    /**
     * A square Lanternguard watchtower on a windy height, still with its signal fire. A stonewarden keeps the door.
     */
    static void watchtower(Sketch s) {
        Mix stone = Mix.of(st(ModBlocks.BARROWSTONE_BRICKS)).and(st(ModBlocks.BARROWSTONE_BRICKS), 6).and(st(ModBlocks.BARROWSTONE), 2)
            .and(st(Blocks.COBBLESTONE), 2).and(st(Blocks.MOSSY_COBBLESTONE), 2);
        s.footingState(st(Blocks.COBBLESTONE));
        s.box(-5, 0, -5, 5, 0, 5, Mix.of(st(Blocks.COBBLESTONE)).and(st(Blocks.GRAVEL), 1).and(st(Blocks.MOSSY_COBBLESTONE), 1));
        s.footingUnder(-5, -5, 5, 5);
        s.box(-6, 1, -6, 6, 8, 6, AIR);
        // the tower
        s.box(-3, 1, -3, 3, 20, 3, stone);
        s.hollow(-2, 1, -2, 2, 22, 2);
        for (int[] c : new int[][]{{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) s.box(c[0], 1, c[1], c[0], 21, c[1], st(ModBlocks.BARROWSTONE));
        // floors, with the ladder hole
        for (int y : new int[]{7, 14, 20}) {
            s.box(-2, y, -2, 2, y, 2, st(Blocks.SPRUCE_PLANKS));
            s.put(2, y, 0, st(Blocks.AIR));
        }
        for (int y = 1; y <= 20; y++) s.put(2, y, 0, ladder(Direction.WEST));
        // door and arrow slits
        s.hollow(0, 1, 3, 0, 2, 3);
        s.put(0, 3, 3, st(ModBlocks.BARROWSTONE_BRICK_STAIRS.get()).setValue(StairBlock.FACING, Direction.NORTH).setValue(StairBlock.HALF, Half.TOP));
        for (int y : new int[]{10, 17})
            for (int[] w : new int[][]{{0, -3}, {-3, 0}, {3, 0}, {0, 3}}) s.hollow(w[0], y, w[1], w[0], y + 1, w[1]);
        // the crenellated top and the signal fire
        for (int x = -3; x <= 3; x++)
            for (int z = -3; z <= 3; z++) {
                if (Math.abs(x) != 3 && Math.abs(z) != 3) continue;
                s.put(x, 21, z, (x + z) % 2 == 0 ? st(ModBlocks.BARROWSTONE_BRICK_WALL) : st(Blocks.AIR));
            }
        s.crumble(21, 0.3f);
        s.put(0, 21, 0, st(Blocks.CAMPFIRE));
        s.put(-2, 21, -2, st(ModBlocks.OATHSTEEL_LANTERN));
        s.chest(-2, 21, 2, Direction.EAST, Sketches.loot("watchtower_lookout"));
        // inside
        s.put(-2, 1, -2, st(Blocks.BARREL));
        s.put(-1, 1, -2, st(Blocks.CRAFTING_TABLE));
        s.put(-2, 1, 1, st(Blocks.HAY_BLOCK));
        s.put(-2, 2, 1, st(Blocks.HAY_BLOCK));
        s.put(1, 1, -2, st(Blocks.SMOKER));
        s.put(0, 6, 0, hanging(Blocks.LANTERN));
        s.chest(-2, 8, -2, Direction.SOUTH, Sketches.loot("watchtower_armory"));
        s.put(-1, 8, -2, st(Blocks.BARREL));
        s.put(-2, 8, 0, slab(Blocks.SPRUCE_SLAB, SlabType.BOTTOM));
        s.put(-2, 8, 1, slab(Blocks.SPRUCE_SLAB, SlabType.BOTTOM));
        s.put(0, 13, 0, hanging(Blocks.LANTERN));
        s.put(-2, 15, -2, st(Blocks.CARTOGRAPHY_TABLE));
        s.put(-2, 15, 2, st(Blocks.BARREL));
        s.put(0, 19, 0, hanging(Blocks.LANTERN));
        // the yard: a palisade, a woodpile and a cold campfire
        for (int x = 4; x <= 10; x++) {
            s.put(x, 1, -4, st(Blocks.SPRUCE_FENCE));
            s.put(x, 1, 4, st(Blocks.SPRUCE_FENCE));
        }
        for (int z = -4; z <= 4; z++) if (z != 0) s.put(10, 1, z, st(Blocks.SPRUCE_FENCE));
        s.box(4, 0, -4, 10, 0, 4, Mix.of(st(Blocks.COARSE_DIRT)).and(st(Blocks.GRASS_BLOCK), 2).and(st(Blocks.GRAVEL), 1));
        s.footingUnder(4, -4, 10, 4);
        s.box(7, 1, -3, 9, 1, -3, log(Blocks.SPRUCE_LOG, Direction.Axis.X));
        s.box(7, 2, -3, 8, 2, -3, log(Blocks.SPRUCE_LOG, Direction.Axis.X));
        s.put(7, 1, 1, Blocks.CAMPFIRE.defaultBlockState().setValue(net.minecraft.world.level.block.CampfireBlock.LIT, false));
        for (int[] l : new int[][]{{6, 1}, {8, 1}, {7, 2}}) s.put(l[0], 1, l[1], stairs(Blocks.SPRUCE_STAIRS, Direction.NORTH));
        // a collapsed wall section to the west
        for (int i = 0; i < 12; i++) s.put(-4 - s.rng.nextInt(3), 1, -3 + s.rng.nextInt(7), stone);
        s.weather(b -> b.is(ModBlocks.BARROWSTONE_BRICKS.get()), Mix.of(st(Blocks.MOSSY_STONE_BRICKS)).and(st(Blocks.CRACKED_STONE_BRICKS), 1), 0.08f);
        s.resident(0, 1, 6, ModEntities.STONEWARDEN, 0f);
    }

    // ================================================================== The Tideglass Grotto
    /**
     * A sea-cave in the rocks above the tideline, lit by blue-green crystal and sea lanterns, where the drowned choir
     * still keeps a shrine. A wrecked rowboat lies where the sea threw it.
     */
    static void tideglassGrotto(Sketch s) {
        Mix rock = Mix.of(st(ModBlocks.TIDESTONE)).and(st(ModBlocks.TIDESTONE), 5).and(st(Blocks.STONE), 3).and(st(Blocks.ANDESITE), 2)
            .and(st(ModBlocks.BARNACLED_TIDESTONE_BRICKS), 2).and(st(Blocks.TUFF), 1).and(st(Blocks.PRISMARINE), 1);
        s.footingState(st(Blocks.STONE));
        s.mound(0, 0, 0, 12, 10, rock, rock);
        // the cave inside
        for (int y = 1; y <= 8; y++) {
            double r = Math.sqrt(Math.max(0, 1 - Math.pow(y / 9.0, 2))) * 9.2;
            s.disc(0, y, 0, r, AIR);
        }
        // the mouth, open to the sea (south)
        for (int z = 5; z <= 13; z++)
            for (int x = -3; x <= 3; x++)
                for (int y = 1; y <= 5; y++) {
                    if (x * x / 9.0 + (y - 1) * (y - 1) / 20.0 <= 1.0) s.put(x, y, z, st(Blocks.AIR));
                }
        // floor: sand, and a tidal pool
        s.disc(0, 0, 0, 8.5, Mix.of(st(Blocks.SAND)).and(st(Blocks.GRAVEL), 1).and(st(ModBlocks.TIDESTONE), 1));
        s.disc(-1, 0, -2, 3.6, Mix.of(st(Blocks.WATER)));
        s.disc(-1, -1, -2, 3.6, Mix.of(st(Blocks.SAND)).and(st(Blocks.PRISMARINE), 1).and(st(Blocks.TUBE_CORAL_BLOCK), 1).and(st(Blocks.BRAIN_CORAL_BLOCK), 1));
        s.put(-1, -1, -2, st(Blocks.SEA_LANTERN));
        // tideglass: crystal spurs from floor and roof
        int[][] spurs = {{-6, 1, -3, 3}, {5, 1, -5, 2}, {6, 1, 2, 3}, {-5, 1, 4, 2}, {-3, 8, 1, -3}, {3, 8, 3, -2}, {1, 8, -4, -3}};
        for (int[] c : spurs) {
            int dir = c[3] > 0 ? 1 : -1;
            for (int k = 0; k < Math.abs(c[3]); k++) {
                BlockState g = k == 0 ? st(Blocks.SEA_LANTERN) : (k % 2 == 0 ? st(Blocks.STAINED_GLASS.lightBlue()) : st(Blocks.STAINED_GLASS.cyan()));
                s.put(c[0], c[1] + k * dir, c[2], g);
            }
        }
        // the choir's shrine (north)
        s.put(0, 1, -7, st(ModBlocks.CHISELED_TIDESTONE));
        s.put(0, 2, -7, candles(4));
        s.put(-1, 1, -7, stairs(ModBlocks.TIDESTONE_BRICK_STAIRS, Direction.EAST));
        s.put(1, 1, -7, stairs(ModBlocks.TIDESTONE_BRICK_STAIRS, Direction.WEST));
        for (int side = -1; side <= 1; side += 2) {
            s.box(3 * side, 1, -7, 3 * side, 3, -7, st(ModBlocks.TIDESTONE_BRICK_WALL));
            s.put(3 * side, 4, -7, st(Blocks.SEA_LANTERN));
        }
        s.chest(0, 1, -8, Direction.SOUTH, Sketches.loot("tideglass_hoard"));
        s.spawner(4, 1, -4, ModEntities.DROWNED_CHOIRMONK);
        // the wrecked rowboat
        int bx = -5, bz = 4;
        s.put(bx, 1, bz - 1, stairs(Blocks.SPRUCE_STAIRS, Direction.SOUTH));
        s.put(bx, 1, bz + 2, stairs(Blocks.SPRUCE_STAIRS, Direction.NORTH));
        s.box(bx, 1, bz, bx, 1, bz + 1, slab(Blocks.SPRUCE_SLAB, SlabType.BOTTOM));
        s.put(bx - 1, 1, bz, stairs(Blocks.SPRUCE_STAIRS, Direction.EAST));
        s.put(bx + 1, 1, bz + 1, stairs(Blocks.SPRUCE_STAIRS, Direction.WEST));
        s.chest(bx, 2, bz, Direction.EAST, Sketches.loot("grotto_wreck"));
        s.put(bx + 1, 1, bz - 1, st(Blocks.SPRUCE_FENCE));
    }

    // ================================================================== The Lumenite Delve
    /**
     * An abandoned lumenite mine: a headframe on the surface over a thirty-block shaft, and below it two long timbered
     * galleries, a foreman's store, a flooded sump and the glittering vein-chamber where the mites came up.
     */
    static void lumeniteMine(Sketch s) {
        int top = 30;
        BlockState post = log(Blocks.SPRUCE_LOG, Direction.Axis.Y);
        BlockState beamX = log(Blocks.SPRUCE_LOG, Direction.Axis.X), beamZ = log(Blocks.SPRUCE_LOG, Direction.Axis.Z);
        Mix wallRock = Mix.of(st(Blocks.STONE)).and(st(Blocks.STONE), 8).and(st(Blocks.ANDESITE), 2).and(st(ModBlocks.LUMENITE_ORE), 1)
            .and(st(Blocks.COBBLESTONE), 1);
        // the galleries: along x and along z, four high
        for (int axis = 0; axis < 2; axis++) {
            int len = axis == 0 ? 22 : 16;
            for (int a = -len; a <= len; a++) {
                for (int b = -2; b <= 2; b++)
                    for (int y = 0; y <= 5; y++) {
                        int x = axis == 0 ? a : b, z = axis == 0 ? b : a;
                        boolean inside = Math.abs(b) <= 1 && y >= 1 && y <= 4;
                        if (inside) s.put(x, y, z, st(Blocks.AIR));
                        else if (s.at(x, y, z) == null) s.put(x, y, z, wallRock);
                    }
                int x = axis == 0 ? a : 0, z = axis == 0 ? 0 : a;
                s.put(x, 1, z, st(Blocks.RAIL).setValue(RailBlock.SHAPE, axis == 0 ? RailShape.EAST_WEST : RailShape.NORTH_SOUTH));
                if (Math.abs(a) > 2 && a % 4 == 0) {
                    // a timber frame
                    int px = axis == 0 ? a : -1, pz = axis == 0 ? -1 : a, qx = axis == 0 ? a : 1, qz = axis == 0 ? 1 : a;
                    s.box(px, 1, pz, px, 3, pz, post);
                    s.box(qx, 1, qz, qx, 3, qz, post);
                    s.box(px, 4, pz, qx, 4, qz, axis == 0 ? beamZ : beamX);
                    if (a % 8 == 0) s.put(x, 3, z, hanging(Blocks.LANTERN));
                    else if (s.rng.nextFloat() < 0.4f) s.put(px, 3, pz, st(Blocks.COBWEB));
                }
            }
        }
        s.put(0, 1, 0, st(Blocks.AIR));
        // the shaft to the surface, with its ladder
        s.box(-2, 5, -2, 2, top - 1, 2, Mix.of(st(Blocks.SPRUCE_PLANKS)).and(st(Blocks.STONE), 2));
        s.box(-1, 1, -1, 1, top + 6, 1, AIR);
        for (int y = 6; y < top; y += 6) {
            s.put(1, y, -1, st(Blocks.SPRUCE_PLANKS));
            s.put(1, y + 1, -1, st(Blocks.LANTERN));
        }
        for (int y = 1; y <= top; y++) {
            s.put(-1, y, -2, st(Blocks.SPRUCE_PLANKS));
            s.put(-1, y, -1, ladder(Direction.SOUTH));
        }
        // the headframe
        s.box(-4, top, -4, 4, top, 4, st(Blocks.SPRUCE_PLANKS));
        s.box(-1, top, -1, 1, top, 1, AIR);
        s.put(-1, top, -1, ladder(Direction.SOUTH));
        s.footingUnder(-4, -4, 4, 4);
        s.box(-5, top + 1, -5, 5, top + 8, 5, AIR);
        for (int side = -1; side <= 1; side += 2) {
            s.box(3 * side, top + 1, 0, 3 * side, top + 5, 0, post);
            s.put(2 * side, top + 6, 0, beamX);
        }
        s.box(-1, top + 6, 0, 1, top + 6, 0, beamX);
        s.put(0, top + 5, 0, hanging(Blocks.LANTERN));
        s.put(0, top + 7, 0, st(Blocks.SPRUCE_TRAPDOOR));
        for (int x = -4; x <= 4; x++)
            for (int z = -4; z <= 4; z++)
                if ((Math.abs(x) == 4 || Math.abs(z) == 4) && !(z == 4 && x == 0)) s.put(x, top + 1, z, st(Blocks.SPRUCE_FENCE));
        s.put(-3, top + 1, 3, st(Blocks.BARREL));
        s.put(-3, top + 2, 3, st(Blocks.LANTERN));
        s.chest(3, top + 1, -3, Direction.WEST, Sketches.loot("mine_cache"));
        // east end: the foreman's store
        s.box(20, 0, -4, 26, 5, 4, wallRock);
        s.hollow(21, 1, -3, 25, 4, 3);
        s.put(23, 4, 0, hanging(Blocks.LANTERN));
        s.chest(25, 1, -3, Direction.WEST, Sketches.loot("mine_cache"));
        s.chest(25, 1, 3, Direction.WEST, Sketches.loot("mine_foreman"));
        s.put(24, 1, -3, st(Blocks.BARREL));
        s.put(25, 1, 0, st(Blocks.CRAFTING_TABLE));
        s.put(22, 1, 3, st(Blocks.TNT));
        s.put(21, 1, 3, st(Blocks.BARREL));
        // west end: the fall of rock
        for (int x = -22; x >= -24; x--)
            for (int z = -1; z <= 1; z++)
                for (int y = 1; y <= 4 - (x + 24); y++) s.put(x, y, z, st(Blocks.GRAVEL));
        // south end: the flooded sump
        s.box(-3, -2, 14, 3, 0, 20, wallRock);
        s.box(-2, -1, 15, 2, 0, 19, st(Blocks.WATER));
        s.hollow(-2, 1, 15, 2, 4, 19);
        // north end: the vein-chamber
        s.box(-6, 0, -24, 6, 8, -14, Mix.of(st(Blocks.DEEPSLATE)).and(st(ModBlocks.DEEPSLATE_LUMENITE_ORE), 2).and(st(ModBlocks.LUMENITE_ORE), 2)
            .and(st(Blocks.TUFF), 1));
        for (int y = 1; y <= 7; y++) {
            double r = 5.2 - Math.abs(y - 3.5) * 0.45;
            for (int x = -5; x <= 5; x++)
                for (int z = -23; z <= -15; z++) {
                    double dx = x / r, dz = (z + 19) / r;
                    if (dx * dx + dz * dz <= 1.0) s.put(x, y, z, st(Blocks.AIR));
                }
        }
        s.hollow(-1, 1, -16, 1, 4, -14);
        s.spawner(0, 1, -20, ModEntities.LUMENITE_MITE);
        s.put(-3, 1, -21, st(ModBlocks.LUMENITE_BLOCK));
        s.put(3, 1, -18, st(Blocks.AMETHYST_CLUSTER));
        s.put(-4, 1, -17, st(Blocks.COBWEB));
        s.put(4, 1, -22, st(Blocks.COBWEB));
        s.put(0, 7, -19, st(ModBlocks.LUMENITE_BLOCK));
    }

    // ================================================================== The Shattered Observatory
    /**
     * A star-readers' tower on a Gloaming island, its glass dome broken open to a sky with no stars left in it. The
     * great telescope still points at the breach, and shards of the dome hang in the air where they were thrown.
     */
    static void observatory(Sketch s) {
        Mix bricks = Mix.of(st(ModBlocks.GLOAMSTONE_BRICKS)).and(st(ModBlocks.GLOAMSTONE_BRICKS), 5).and(st(ModBlocks.CRACKED_GLOAMSTONE_BRICKS), 2)
            .and(st(ModBlocks.POLISHED_GLOAMSTONE), 1);
        s.footingState(st(ModBlocks.GLOAMSTONE));
        s.footingDepth(12);
        s.disc(0, 0, 0, 7.5, Mix.of(st(ModBlocks.POLISHED_GLOAMSTONE)).and(st(ModBlocks.GLOAMSTONE_TILES), 2));
        for (int x = -7; x <= 7; x++)
            for (int z = -7; z <= 7; z++) if (x * x + z * z <= 56) s.footing(x, z);
        clearAbove(s, 8.5, 1, 9);
        // a star map in the floor
        s.annulus(0, 0, 0, 4.5, 5.2, Mix.of(st(ModBlocks.CHISELED_GLOAMSTONE)));
        for (int i = 0; i < 9; i++) {
            double a = s.rng.nextDouble() * Math.PI * 2, r = 1.5 + s.rng.nextDouble() * 2.8;
            s.put((int) Math.round(Math.cos(a) * r), 0, (int) Math.round(Math.sin(a) * r), st(ModBlocks.LANTERNGLASS));
        }
        // the walls
        for (int y = 1; y <= 10; y++) s.annulus(0, y, 0, 6.0, 7.3, bricks);
        for (int k = 0; k < 8; k++) {
            double a = k * Math.PI / 4;
            int x = (int) Math.round(Math.cos(a) * 6.7), z = (int) Math.round(Math.sin(a) * 6.7);
            s.box(x, 3, z, x, 6, z, st(ModBlocks.GLOAMGLASS));
        }
        s.hollow(-1, 1, 6, 1, 3, 8);
        s.put(0, 4, 7, st(ModBlocks.CHISELED_GLOAMSTONE));
        // the dome, broken open to the north-east
        for (int dx = -8; dx <= 8; dx++)
            for (int dy = 0; dy <= 8; dy++)
                for (int dz = -8; dz <= 8; dz++) {
                    double d = Math.sqrt(dx * dx + dy * dy + dz * dz);
                    if (d > 7.6 || d <= 6.4) continue;
                    double ang = Math.toDegrees(Math.atan2(dz, dx));
                    boolean breach = dy > 1 && ang > -110 && ang < -20;
                    if (breach || s.rng.nextFloat() < 0.12f) continue;
                    boolean rib = Math.abs(((ang + 360) % 45) - 22.5) > 19 || dy <= 1;
                    s.put(dx, 11 + dy, dz, rib ? st(ModBlocks.CHISELED_GLOAMSTONE) : st(ModBlocks.GLOAMGLASS));
                }
        // the balcony ring and its stair
        s.annulus(0, 6, 0, 4.2, 6.0, Mix.of(slab(ModBlocks.POLISHED_GLOAMSTONE_SLAB, SlabType.TOP)));
        for (int k = 0; k < 6; k++) {
            double a = Math.PI * 0.75 + k * 0.28;
            int x = (int) Math.round(Math.cos(a) * 5.1), z = (int) Math.round(Math.sin(a) * 5.1);
            s.put(x, k, z, st(ModBlocks.POLISHED_GLOAMSTONE));
            s.put(x, k + 1, z, slab(ModBlocks.POLISHED_GLOAMSTONE_SLAB, SlabType.BOTTOM));
        }
        s.spawner(4, 7, 2, ModEntities.SHADE_WRAITH);
        s.chest(-4, 7, -2, Direction.EAST, Sketches.loot("observatory_charts"));
        s.put(-4, 7, 2, st(Blocks.BOOKSHELF));
        s.put(-3, 7, 3, st(Blocks.LECTERN));
        s.put(0, 7, -5, st(ModBlocks.GLOAM_LANTERN));
        s.put(0, 7, 5, st(ModBlocks.GLOAM_LANTERN));
        // the great telescope, aimed at the breach
        s.put(0, 1, 0, st(ModBlocks.CHISELED_GLOAMSTONE));
        s.put(0, 2, 0, st(ModBlocks.DUSKIRON_BLOCK));
        for (int k = 0; k <= 9; k++) {
            int x = (int) Math.round(k * 0.55), y = 3 + k, z = -(int) Math.round(k * 0.55);
            s.put(x, y, z, st(Blocks.COPPER_BLOCK));
            if (k > 4) s.put(x + 1, y, z, st(Blocks.COPPER_BLOCK));
        }
        s.put(6, 13, -5, st(ModBlocks.LANTERNGLASS));
        s.put(0, 3, 1, st(Blocks.END_ROD));
        // the orrery
        s.put(-3, 1, -3, st(ModBlocks.RUNESILVER_BLOCK));
        s.put(-3, 2, -3, st(Blocks.END_ROD));
        s.put(-2, 3, -3, st(ModBlocks.LANTERNGLASS));
        s.put(-4, 3, -4, st(ModBlocks.GLOAMGLASS));
        s.put(-3, 4, -2, st(ModBlocks.GLOAM_LANTERN));
        // shards of the dome, still hanging where the blast threw them
        for (int i = 0; i < 14; i++) {
            double a = Math.toRadians(-110 + s.rng.nextDouble() * 90), r = 9 + s.rng.nextDouble() * 5;
            int x = (int) Math.round(Math.cos(a) * r), z = (int) Math.round(Math.sin(a) * r), y = 13 + s.rng.nextInt(9);
            s.put(x, y, z, s.rng.nextFloat() < 0.3f ? st(ModBlocks.CHISELED_GLOAMSTONE) : st(ModBlocks.GLOAMGLASS));
            if (s.rng.nextBoolean()) s.put(x + 1, y, z, st(ModBlocks.GLOAMGLASS));
            if (s.rng.nextFloat() < 0.3f) s.put(x, y + 1, z, st(ModBlocks.GLOAMGLASS));
        }
        s.crumble(10, 0.15f);
    }
}
