package com.oathbound.world;

import com.oathbound.Oathbound;
import com.oathbound.block.*;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.world.Sketch.Mix;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CandleBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Every Oathbound structure, drawn procedurally. Puzzle geometry here is load-bearing: the Hymn Stone, Cipher
 * Lectern, tombs and Sundered Gate find their parts by searching around themselves, and the Gate rite assumes
 * the frame layout documented on {@link com.oathbound.event.GateRite}.
 */
public final class Sketches {
    public enum Siting { SURFACE, SHORE }

    public enum Type {
        WAYSHRINE(6, 4, Siting.SURFACE),
        DROWNED_CHAPEL(12, 8, Siting.SHORE),
        ARCANIST_SPIRE(7, 5, Siting.SURFACE),
        BARROW_OF_KINGS(10, 6, Siting.SURFACE),
        SUNDERED_CITADEL(18, 7, Siting.SURFACE),
        THRONE(16, 99, Siting.SURFACE);

        public final int footprint;
        public final int tolerance;
        public final Siting siting;

        Type(int footprint, int tolerance, Siting siting) {
            this.footprint = footprint;
            this.tolerance = tolerance;
            this.siting = siting;
        }

        public static Type named(String name) {
            return valueOf(name.toUpperCase(Locale.ROOT));
        }

        public String id() {
            return name().toLowerCase(Locale.ROOT);
        }
    }

    private static final Map<String, Sketch> CACHE = Collections.synchronizedMap(new LinkedHashMap<>(16, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, Sketch> eldest) {
            return size() > 16;
        }
    });

    private Sketches() {}

    public static ResourceKey<LootTable> loot(String path) {
        return ResourceKey.create(Registries.LOOT_TABLE, Identifier.fromNamespaceAndPath(Oathbound.MODID, "chests/" + path));
    }

    public static Sketch cached(Type type, long seed) {
        return CACHE.computeIfAbsent(type + "@" + seed, k -> draw(type, seed));
    }

    public static Sketch draw(Type type, long seed) {
        Sketch s = new Sketch(seed);
        switch (type) {
            case WAYSHRINE -> wayshrine(s);
            case DROWNED_CHAPEL -> chapel(s);
            case ARCANIST_SPIRE -> spire(s);
            case BARROW_OF_KINGS -> barrow(s);
            case SUNDERED_CITADEL -> citadel(s);
            case THRONE -> throne(s);
        }
        return s;
    }

    // ------------------------------------------------------------------ palette helpers
    private static BlockState st(Block b) {
        return b.defaultBlockState();
    }

    private static BlockState st(net.minecraftforge.registries.RegistryObject<Block> b) {
        return b.get().defaultBlockState();
    }

    private static BlockState stairs(net.minecraftforge.registries.RegistryObject<Block> b, Direction facing) {
        return b.get().defaultBlockState().setValue(StairBlock.FACING, facing);
    }

    private static BlockState stairs(Block b, Direction facing) {
        return b.defaultBlockState().setValue(StairBlock.FACING, facing);
    }

    private static BlockState slab(net.minecraftforge.registries.RegistryObject<Block> b, SlabType type) {
        return b.get().defaultBlockState().setValue(SlabBlock.TYPE, type);
    }

    private static BlockState facing(net.minecraftforge.registries.RegistryObject<Block> b, Direction d) {
        return b.get().defaultBlockState().setValue(HorizontalDirectionalBlock.FACING, d);
    }

    private static BlockState tablet(int index, Direction d) {
        return facing(ModBlocks.LORE_TABLET, d).setValue(LoreTabletBlock.TABLET, index);
    }

    private static BlockState candles(int n) {
        return Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.CANDLES, n).setValue(CandleBlock.LIT, true);
    }

    private static BlockState pillar() {
        return st(ModBlocks.WARDSTONE_PILLAR).setValue(RotatedPillarBlock.AXIS, Direction.Axis.Y);
    }

    private static Mix wardstoneRuin() {
        return Mix.of(st(ModBlocks.WARDSTONE_BRICKS)).and(st(ModBlocks.WARDSTONE_BRICKS), 5)
            .and(st(ModBlocks.CRACKED_WARDSTONE_BRICKS), 2).and(st(ModBlocks.MOSSY_WARDSTONE_BRICKS), 3);
    }

    private static Mix drownedStone() {
        return Mix.of(st(ModBlocks.MOSSY_WARDSTONE_BRICKS)).and(st(ModBlocks.MOSSY_WARDSTONE_BRICKS), 3)
            .and(st(ModBlocks.WARDSTONE_BRICKS), 3).and(st(ModBlocks.CRACKED_WARDSTONE_BRICKS), 2)
            .and(st(Blocks.PRISMARINE_BRICKS), 1).and(st(Blocks.MUD_BRICKS), 1);
    }

    private static Mix barrowStone() {
        return Mix.of(st(Blocks.STONE_BRICKS)).and(st(Blocks.MOSSY_STONE_BRICKS), 2).and(st(Blocks.CRACKED_STONE_BRICKS), 1)
            .and(st(Blocks.TUFF_BRICKS), 2).and(st(Blocks.COBBLED_DEEPSLATE), 1);
    }

    private static Mix gloamBricks() {
        return Mix.of(st(ModBlocks.GLOAMSTONE_BRICKS)).and(st(ModBlocks.GLOAMSTONE_BRICKS), 4).and(st(ModBlocks.GLOAMSTONE), 1)
            .and(st(ModBlocks.WARDSTONE_BRICKS), 1);
    }

    private static final Mix AIR = Mix.of(Blocks.AIR.defaultBlockState());

    // ------------------------------------------------------------------ Wayshrine
    /** A small open shrine: four pillars, a bronze brazier, an engraved stone, and a cache beneath cracked bricks. */
    private static void wayshrine(Sketch s) {
        s.footingState(st(ModBlocks.WARDSTONE));
        s.disc(0, 0, 0, 5.5, wardstoneRuin());
        s.footingUnder(-5, -5, 5, 5);
        for (int y = 1; y <= 7; y++) s.disc(0, y, 0, 6.5, AIR);
        s.disc(0, 0, 0, 2.2, Mix.of(st(ModBlocks.WARDSTONE)));
        s.put(0, 0, 0, st(ModBlocks.CHISELED_WARDSTONE));
        s.put(0, 1, 0, st(ModBlocks.WAYSHRINE_BRAZIER));
        for (int[] c : new int[][]{{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) {
            s.box(c[0], 1, c[1], c[0], 4, c[1], pillar());
            s.put(c[0], 5, c[1], st(ModBlocks.CHISELED_WARDSTONE));
            s.put(c[0], 6, c[1], st(Blocks.LANTERN));
        }
        Mix lintel = Mix.of(st(ModBlocks.WARDSTONE_BRICKS)).and(slab(ModBlocks.WARDSTONE_BRICK_SLAB, SlabType.BOTTOM), 1);
        s.box(-2, 5, -3, 2, 5, -3, lintel);
        s.box(-2, 5, 3, 2, 5, 3, lintel);
        s.box(-3, 5, -2, -3, 5, 2, lintel);
        s.box(3, 5, -2, 3, 5, 2, lintel);
        // the engraved stone
        s.box(-1, 1, -5, 1, 2, -5, st(ModBlocks.WARDSTONE_BRICKS));
        s.put(0, 3, -5, slab(ModBlocks.WARDSTONE_BRICK_SLAB, SlabType.BOTTOM));
        s.put(0, 1, -4, tablet(0, Direction.SOUTH));
        s.put(-1, 1, -4, candles(3));
        s.put(1, 1, -4, candles(2));
        // steps on each side
        s.put(0, 0, 6, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
        s.put(0, 0, -6, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.SOUTH));
        s.put(6, 0, 0, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.WEST));
        s.put(-6, 0, 0, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.EAST));
        s.crumble(5, 0.25f);
        // the cache beneath the cracked bricks
        s.box(-2, -5, 1, 2, -1, 5, st(ModBlocks.WARDSTONE));
        s.hollow(-1, -4, 2, 1, -2, 4);
        s.put(0, 0, 3, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.put(0, -1, 3, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.chest(0, -4, 4, Direction.NORTH, loot("wayshrine_cache"));
        s.put(-1, -4, 2, candles(4));
        s.put(1, -4, 4, st(Blocks.COBWEB));
    }

    // ------------------------------------------------------------------ Drowned Chapel
    /**
     * A flooded Lanternguard chapel at the water's edge. Four tuned bells stand in its alcoves under windows of
     * matching glass; the Hymn Stone waits on the altar. A grate before the altar seals the stair to the crypt,
     * where Sir Caldris keeps his vigil in the dark water.
     */
    private static void chapel(Sketch s) {
        Mix stone = drownedStone();
        s.footingState(st(Blocks.MUD_BRICKS));
        // floor and hull
        s.box(-6, 0, -12, 6, 0, 12, stone);
        s.footingUnder(-6, -12, 6, 12);
        s.walls(-6, 1, -12, 6, 7, 12, stone);
        s.hollow(-5, 1, -11, 5, 13, 11);
        // gabled roof (ruined)
        for (int k = 0; k <= 5; k++) {
            s.box(-6 + k, 8 + k, -12, -6 + k, 8 + k, 12, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.EAST));
            s.box(6 - k, 8 + k, -12, 6 - k, 8 + k, 12, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.WEST));
        }
        s.box(0, 14, -12, 0, 14, 12, st(ModBlocks.WARDSTONE_BRICKS));
        for (int k = 0; k <= 5; k++) {
            s.box(-5 + k, 8 + k, -12, 5 - k, 8 + k, -12, stone);
            s.box(-5 + k, 8 + k, 12, 5 - k, 8 + k, 12, stone);
        }
        s.crumble(9, 0.3f);
        // entrance
        s.hollow(-1, 1, 12, 1, 4, 12);
        s.box(-1, 0, 13, 1, 0, 13, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
        // plain windows
        for (int z : new int[]{-8, 9}) {
            s.box(-6, 3, z, -6, 5, z, st(Blocks.STAINED_GLASS.get(DyeColor.LIGHT_GRAY)));
            s.box(6, 3, z, 6, 5, z, st(Blocks.STAINED_GLASS.get(DyeColor.LIGHT_GRAY)));
        }
        // the four bells, their glass and their floor tiles
        Block[] glass = {Blocks.STAINED_GLASS.get(DyeColor.BLUE), Blocks.STAINED_GLASS.get(DyeColor.LIME), Blocks.STAINED_GLASS.get(DyeColor.YELLOW), Blocks.STAINED_GLASS.get(DyeColor.RED)};
        Block[] tiles = {Blocks.GLAZED_TERRACOTTA.get(DyeColor.BLUE), Blocks.GLAZED_TERRACOTTA.get(DyeColor.LIME), Blocks.GLAZED_TERRACOTTA.get(DyeColor.YELLOW), Blocks.GLAZED_TERRACOTTA.get(DyeColor.RED)};
        int[][] bells = {{-4, -2}, {4, -2}, {-4, 4}, {4, 4}};
        for (int i = 0; i < 4; i++) {
            int x = bells[i][0], z = bells[i][1];
            int wall = x < 0 ? -6 : 6;
            s.box(wall, 2, z, wall, 6, z, st(glass[i]));
            s.put(x, 0, z, st(tiles[i]));
            s.put(x, 1, z, st(ModBlocks.CHAPEL_BELL).setValue(ChapelBellBlock.TONE, i));
            s.put(x + (x < 0 ? -1 : 1), 1, z - 1, candles(2));
        }
        // pews
        for (int z = 6; z <= 10; z += 2) {
            for (int x : new int[]{-3, -2, 2, 3}) s.put(x, 1, z, stairs(Blocks.DARK_OAK_STAIRS, Direction.SOUTH));
        }
        // flooded nave (south half)
        for (int x = -5; x <= 5; x++)
            for (int z = 1; z <= 11; z++)
                if (s.at(x, 1, z) == null && s.rng.nextFloat() < 0.35f) s.put(x, 1, z, st(Blocks.WATER));
        // altar
        s.box(-3, 1, -11, 3, 1, -8, st(ModBlocks.WARDSTONE_BRICKS));
        s.box(-3, 1, -7, 3, 1, -7, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
        s.put(0, 2, -9, st(ModBlocks.HYMN_STONE));
        s.put(-2, 2, -10, candles(4));
        s.put(2, 2, -10, candles(3));
        s.put(-2, 2, -8, st(Blocks.LANTERN));
        s.put(2, 2, -8, st(Blocks.LANTERN));
        s.box(-1, 2, -11, 1, 5, -11, st(ModBlocks.CHISELED_WARDSTONE));
        s.put(0, 6, -11, st(Blocks.LANTERN));
        // lore
        s.put(-5, 1, 10, tablet(1, Direction.EAST));
        s.put(5, 2, -10, tablet(2, Direction.WEST));
        // the crypt shell and chamber
        Mix crypt = Mix.of(st(ModBlocks.MOSSY_WARDSTONE_BRICKS)).and(st(ModBlocks.WARDSTONE_BRICKS), 2).and(st(Blocks.DARK_PRISMARINE), 1)
            .and(st(ModBlocks.CRACKED_WARDSTONE_BRICKS), 1);
        s.box(-8, -10, -1, 8, -1, 16, crypt);
        s.hollow(-7, -9, 0, 7, -3, 15);
        // stair shaft down from the altar grate
        s.box(-2, -9, -7, 2, -1, 1, crypt);
        for (int i = 0; i <= 7; i++) {
            int z = -6 + i, y = -1 - i;
            s.box(-1, y, z, 1, y, z, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
            s.box(-1, y + 1, z, 1, Math.min(-1, y + 4), z, AIR);
        }
        s.box(-1, 0, -6, 1, 0, -4, st(ModBlocks.SEALED_GRATE));
        // crypt decor: shallow black water, soul lanterns, chains
        for (int x = -7; x <= 7; x++)
            for (int z = 6; z <= 15; z++)
                if (s.rng.nextFloat() < 0.3f) s.put(x, -9, z, st(Blocks.WATER));
        for (int[] c : new int[][]{{-6, 2}, {6, 2}, {-6, 13}, {6, 13}}) {
            s.box(c[0], -9, c[1], c[0], -4, c[1], pillar());
            s.put(c[0], -3, c[1], st(Blocks.IRON_BARS));
        }
        s.put(-5, -9, 4, st(Blocks.SOUL_LANTERN));
        s.put(5, -9, 4, st(Blocks.SOUL_LANTERN));
        s.chest(0, -9, 15, Direction.NORTH, loot("chapel_reliquary"));
        s.resident(0, -9, 10, ModEntities.SIR_CALDRIS, 180f);
        // the Order's secret niche behind the east wall
        s.box(9, -10, 4, 11, -6, 8, crypt);
        s.hollow(9, -9, 5, 10, -8, 7);
        s.put(8, -9, 6, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.put(8, -8, 6, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.chest(10, -9, 6, Direction.WEST, loot("chapel_secret"));
        s.chest(4, 1, -10, Direction.WEST, loot("chapel_nave"));
        s.resident(-3, 1, 8, () -> EntityTypes.DROWNED, 0f);
        s.resident(3, 1, 3, () -> EntityTypes.DROWNED, 90f);
    }

    // ------------------------------------------------------------------ Arcanist's Spire
    private static final int[] FLOORS = {0, 8, 16, 24, 32};
    private static final int SPIRE_TOP = 40;

    /** Stair step k of the spire's spiral (two blocks wide): {x1, z1, x2, z2, y}. */
    private static int[] step(int k) {
        double a = k * Math.PI / 8;
        int y = 1 + k;
        return new int[]{(int) Math.round(Math.cos(a) * 3.5), (int) Math.round(Math.sin(a) * 3.5),
            (int) Math.round(Math.cos(a) * 4.5), (int) Math.round(Math.sin(a) * 4.5), y};
    }

    private static Direction tangent(int k) {
        double a = k * Math.PI / 8 + Math.PI / 16;
        double dx = -Math.sin(a), dz = Math.cos(a);
        if (Math.abs(dx) > Math.abs(dz)) return dx > 0 ? Direction.EAST : Direction.WEST;
        return dz > 0 ? Direction.SOUTH : Direction.NORTH;
    }

    /**
     * A five-storey tower of pale wardstone and blue glass. A spiral stair climbs past the library and the
     * alchemy floor to the antechamber, where the four Rune Dials face the Cipher. Veyl's ward seals the last
     * turn of the stair to the sanctum.
     */
    private static void spire(Sketch s) {
        s.footingState(st(ModBlocks.WARDSTONE));
        Mix wall = Mix.of(st(ModBlocks.WARDSTONE_BRICKS)).and(st(ModBlocks.WARDSTONE_BRICKS), 8).and(st(ModBlocks.CRACKED_WARDSTONE_BRICKS), 1)
            .and(st(ModBlocks.MOSSY_WARDSTONE_BRICKS), 1);
        s.disc(0, 0, 0, 6.5, Mix.of(st(ModBlocks.WARDSTONE)));
        s.footingUnder(-6, -6, 6, 6);
        for (int y = 1; y <= SPIRE_TOP; y++) {
            s.annulus(0, y, 0, 5.05, 6.5, wall);
            s.disc(0, y, 0, 5.0, AIR);
        }
        for (int f : FLOORS) {
            if (f > 0) s.disc(0, f, 0, 5.0, Mix.of(st(ModBlocks.WARDSTONE_BRICKS)).and(st(ModBlocks.WARDSTONE), 1));
            s.annulus(0, f + 7, 0, 5.05, 6.5, Mix.of(st(ModBlocks.CHISELED_WARDSTONE)));
            // windows on the four sides
            for (int[] w : new int[][]{{0, -6}, {0, 6}, {-6, 0}, {6, 0}}) {
                if (f == 0 && w[1] == 6) continue;
                s.box(w[0], f + 3, w[1], w[0], f + 4, w[1], st(Blocks.STAINED_GLASS.get(DyeColor.BLUE)));
                if (w[0] == 0) {
                    s.box(-1, f + 3, w[1], 1, f + 4, w[1], st(Blocks.STAINED_GLASS.get(DyeColor.BLUE)));
                } else {
                    s.box(w[0], f + 3, -1, w[0], f + 4, 1, st(Blocks.STAINED_GLASS.get(DyeColor.BLUE)));
                }
            }
        }
        s.disc(0, SPIRE_TOP, 0, 5.0, Mix.of(st(ModBlocks.WARDSTONE_BRICKS)));
        // doorway
        s.box(-1, 1, 5, 1, 3, 7, AIR);
        s.box(-1, 0, 7, 1, 0, 7, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
        // roof cone and finial
        Mix slate = Mix.of(st(Blocks.DEEPSLATE_TILES)).and(st(Blocks.DEEPSLATE_TILES), 3).and(st(Blocks.POLISHED_DEEPSLATE), 1);
        for (int i = 0; i <= 9; i++) s.disc(0, SPIRE_TOP + 1 + i, 0, Math.max(0.6, 6.8 - i * 0.7), slate);
        s.put(0, SPIRE_TOP + 11, 0, st(ModBlocks.CHISELED_WARDSTONE));
        s.box(0, SPIRE_TOP + 12, 0, 0, SPIRE_TOP + 14, 0, st(Blocks.END_ROD));
        // spiral stair: 31 steps, then the sanctum floor
        for (int k = 0; k <= 30; k++) {
            int[] p = step(k);
            BlockState stair = stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, tangent(k));
            boolean warded = p[4] >= 26;
            for (int[] c : new int[][]{{p[0], p[1]}, {p[2], p[3]}}) {
                s.put(c[0], p[4], c[1], stair);
                for (int h = 1; h <= 3; h++) {
                    s.put(c[0], p[4] + h, c[1], warded ? st(ModBlocks.ARCANE_WARD) : st(Blocks.AIR));
                }
            }
        }
        // ground floor: an entry hall with a shelf of candles
        s.put(-3, 1, 2, candles(3));
        s.put(-4, 1, -1, st(Blocks.LANTERN));
        // library (floor 8): south-east shelves
        for (int x = -4; x <= 4; x++)
            for (int z = -4; z <= 4; z++) {
                double d = Math.sqrt(x * x + z * z);
                if (d > 3.9 && d <= 5.0 && (x >= 0 || z >= 0) && !(x == 0 && Math.abs(z) > 4) && s.at(x, 9, z) != null && s.at(x, 9, z).isAir()) {
                    s.box(x, 9, z, x, 11, z, st(Blocks.BOOKSHELF));
                }
            }
        s.spawner(0, 9, 0, ModEntities.ANIMATED_TOME);
        s.chest(2, 9, 2, Direction.WEST, loot("spire_library"));
        s.put(0, 9, 3, tablet(3, Direction.NORTH));
        s.put(-1, 9, 2, st(Blocks.LECTERN));
        // alchemy (floor 16): north-west half
        s.put(-2, 17, -2, st(Blocks.BREWING_STAND));
        s.put(-3, 17, 0, st(Blocks.CAULDRON));
        s.put(-1, 17, -3, st(Blocks.CRAFTING_TABLE));
        s.chest(0, 17, -4, Direction.SOUTH, loot("spire_alchemy"));
        s.spawner(-2, 17, 2, ModEntities.ANIMATED_TOME);
        s.put(1, 17, -2, candles(4));
        // antechamber (floor 24): the Cipher and the four numbered dials
        for (int i = 0; i < 4; i++) {
            s.put(-3 + 2 * i, 25, 3, facing(ModBlocks.RUNE_DIAL, Direction.NORTH).setValue(RuneDialBlock.NUMBER, i).setValue(RuneDialBlock.GLYPH, (i * 2 + 1) % 6));
        }
        s.put(0, 25, -1, facing(ModBlocks.CIPHER_LECTERN, Direction.SOUTH));
        s.put(4, 25, 0, tablet(4, Direction.WEST));
        s.put(2, 25, -2, candles(3));
        s.put(-2, 25, -2, candles(2));
        // sanctum (floor 32)
        s.annulus(0, 32, 0, 2.0, 3.0, Mix.of(st(ModBlocks.CHISELED_WARDSTONE)));
        s.put(0, 32, 0, st(ModBlocks.LUMENITE_BLOCK));
        for (int[] c : new int[][]{{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) s.put(c[0], 33, c[1], st(Blocks.AMETHYST_CLUSTER));
        s.chest(0, 33, -4, Direction.SOUTH, loot("spire_sanctum"));
        s.resident(0, 33, 0, ModEntities.ARCHMAGE_VEYL, 180f);
        // the cellar cache
        s.box(1, -4, -5, 5, 0, -1, st(ModBlocks.WARDSTONE));
        s.hollow(2, -3, -4, 4, -1, -2);
        s.put(3, 0, -3, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.chest(3, -3, -4, Direction.SOUTH, loot("spire_secret"));
        s.put(2, -3, -2, candles(1));
    }

    // ------------------------------------------------------------------ Barrow of Kings
    /**
     * A grass-grown burial mound ringed with standing stones. A stair descends to the Hall of Three Kings, where
     * the tombs of Aldric, Beornhelm and Cyneric carry their epitaphs; beyond the sealed door lies Hrodgar's hall.
     */
    private static void barrow(Sketch s) {
        Mix stone = barrowStone();
        s.footingState(st(Blocks.DIRT));
        s.mound(0, 0, 0, 10.5, 6, Mix.of(st(Blocks.GRASS_BLOCK)).and(st(Blocks.GRASS_BLOCK), 5).and(st(Blocks.MOSS_BLOCK), 1),
            Mix.of(st(Blocks.DIRT)).and(st(Blocks.COARSE_DIRT), 1).and(st(Blocks.ROOTED_DIRT), 1));
        for (int i = 0; i < 9; i++) {
            double a = i * Math.PI * 2 / 9 + 0.3;
            int x = (int) Math.round(Math.cos(a) * 13.5), z = (int) Math.round(Math.sin(a) * 13.5);
            if (z > 10 && Math.abs(x) < 4) continue;
            int h = 2 + s.rng.nextInt(3);
            s.box(x, 0, z, x, h, z, Mix.of(st(Blocks.STONE)).and(st(Blocks.MOSSY_COBBLESTONE), 1).and(st(Blocks.ANDESITE), 1));
            s.footing(x, z);
        }
        // doorway into the mound
        s.box(-2, 0, 8, 2, 4, 11, stone);
        s.box(-1, 1, 8, 1, 3, 12, AIR);
        s.box(-2, 4, 11, 2, 4, 11, st(Blocks.CHISELED_STONE_BRICKS));
        s.put(-2, 5, 11, st(Blocks.SOUL_LANTERN));
        s.put(2, 5, 11, st(Blocks.SOUL_LANTERN));
        // the descent
        s.box(-2, -12, -4, 2, 4, 8, stone);
        for (int i = 0; i <= 10; i++) {
            int z = 7 - i, y = -i;
            s.box(-1, y, z, 1, y, z, stairs(Blocks.STONE_BRICK_STAIRS, Direction.SOUTH));
            s.box(-1, y + 1, z, 1, y + 4, z, AIR);
        }
        // hall of three kings
        s.box(-8, -12, -14, 8, -4, -2, stone);
        s.hollow(-7, -10, -13, 7, -5, -3);
        s.box(-1, -10, -3, 1, -7, -3, AIR);
        int[][] tombs = {{-4, -9}, {0, -10}, {4, -9}};
        for (int k = 0; k < 3; k++) {
            int x = tombs[k][0], z = tombs[k][1];
            s.put(x, -11, z, st(Blocks.CHISELED_STONE_BRICKS));
            s.put(x, -10, z, facing(ModBlocks.SARCOPHAGUS, Direction.SOUTH).setValue(SarcophagusBlock.KING, k));
            s.put(x - 1, -10, z, candles(2));
            s.put(x + 1, -10, z, candles(3));
            s.put(x, -6, z, st(Blocks.IRON_BARS));
            s.put(x, -7, z, st(Blocks.SOUL_LANTERN));
        }
        s.put(2, -10, -4, tablet(5, Direction.SOUTH));
        s.box(-1, -10, -14, 1, -8, -14, st(ModBlocks.BARROW_SEAL));
        s.resident(-5, -10, -5, ModEntities.BARROW_WIGHT, 0f);
        s.resident(5, -10, -12, ModEntities.BARROW_WIGHT, 180f);
        // corridor and Hrodgar's hall
        s.box(-2, -11, -18, 2, -7, -15, stone);
        s.box(-1, -10, -18, 1, -8, -15, AIR);
        s.box(-11, -12, -41, 11, -1, -18, stone);
        s.hollow(-10, -10, -40, 10, -2, -19);
        s.box(-1, -10, -19, 1, -8, -19, AIR);
        for (int[] c : new int[][]{{-7, -22}, {7, -22}, {-7, -30}, {7, -30}, {-7, -37}, {7, -37}}) {
            s.box(c[0], -10, c[1], c[0], -3, c[1], stone);
        }
        for (int z : new int[]{-24, -28, -32}) {
            for (int x : new int[]{-5, 5}) {
                s.put(x, -11, z, st(Blocks.COARSE_DIRT));
                s.put(x, -11, z + 1, st(Blocks.COARSE_DIRT));
                s.put(x, -10, z - 1, st(Blocks.CHISELED_STONE_BRICKS));
            }
        }
        s.put(-9, -10, -20, st(Blocks.SOUL_CAMPFIRE));
        s.put(9, -10, -20, st(Blocks.SOUL_CAMPFIRE));
        s.put(-9, -10, -39, st(Blocks.SOUL_CAMPFIRE));
        s.put(9, -10, -39, st(Blocks.SOUL_CAMPFIRE));
        // throne of the Barrow-King
        s.box(-3, -10, -39, 3, -10, -36, st(Blocks.POLISHED_TUFF));
        s.put(0, -9, -38, stairs(Blocks.TUFF_BRICK_STAIRS, Direction.NORTH));
        s.box(-1, -9, -39, 1, -6, -39, st(Blocks.CHISELED_TUFF_BRICKS));
        s.put(-1, -9, -38, st(Blocks.TUFF_BRICK_WALL));
        s.put(1, -9, -38, st(Blocks.TUFF_BRICK_WALL));
        s.resident(0, -10, -34, ModEntities.HRODGAR, 0f);
        s.chest(3, -9, -39, Direction.SOUTH, loot("barrow_hoard"));
        s.chest(-3, -9, -39, Direction.SOUTH, loot("barrow_tomb"));
        s.put(-3, -10, -21, tablet(6, Direction.SOUTH));
        // secret niche east of the tombs
        s.box(9, -11, -8, 11, -8, -4, stone);
        s.hollow(9, -10, -7, 10, -9, -5);
        s.put(8, -10, -6, st(Blocks.CRACKED_STONE_BRICKS));
        s.put(8, -9, -6, st(Blocks.CRACKED_STONE_BRICKS));
        s.chest(10, -10, -6, Direction.WEST, loot("barrow_secret"));
    }

    // ------------------------------------------------------------------ Sundered Citadel
    /**
     * The broken fortress where the Order made its last stand. Its courtyard holds the Sundered Gate: a frame of
     * wardstone pillars around nothing, with the keystone set into its threshold.
     */
    private static void citadel(Sketch s) {
        Mix wall = Mix.of(st(ModBlocks.WARDSTONE_BRICKS)).and(st(ModBlocks.WARDSTONE_BRICKS), 4).and(st(ModBlocks.CRACKED_WARDSTONE_BRICKS), 2)
            .and(st(ModBlocks.MOSSY_WARDSTONE_BRICKS), 2).and(st(Blocks.COBBLESTONE), 1);
        Mix ground = Mix.of(st(Blocks.COARSE_DIRT)).and(st(Blocks.GRAVEL), 1).and(st(ModBlocks.WARDSTONE), 2).and(st(Blocks.GRASS_BLOCK), 2)
            .and(st(Blocks.MOSSY_COBBLESTONE), 1);
        s.footingState(st(ModBlocks.WARDSTONE));
        s.box(-18, 0, -18, 18, 0, 18, ground);
        s.box(-18, 1, -18, 18, 12, 18, AIR);
        s.walls(-18, 1, -18, 18, 8, 18, wall);
        s.footingUnder(-18, -18, 18, -18);
        s.footingUnder(-18, 18, 18, 18);
        s.footingUnder(-18, -18, -18, 18);
        s.footingUnder(18, -18, 18, 18);
        s.box(-2, 1, 18, 2, 5, 18, AIR);
        // corner towers
        for (int[] c : new int[][]{{-15, -15}, {15, -15}, {-15, 15}, {15, 15}}) {
            for (int y = 1; y <= 13; y++) {
                s.annulus(c[0], y, c[1], 2.5, 3.6, wall);
                s.disc(c[0], y, c[1], 2.4, AIR);
            }
            s.disc(c[0], 0, c[1], 2.4, Mix.of(st(ModBlocks.WARDSTONE)));
            s.footingUnder(c[0] - 3, c[1] - 3, c[0] + 3, c[1] + 3);
            int dx = c[0] > 0 ? -1 : 1, dz = c[1] > 0 ? -1 : 1;
            s.box(c[0] + dx * 2, 1, c[1] + dz * 2, c[0] + dx * 3, 3, c[1] + dz * 3, AIR);
        }
        // the ruined hall
        s.walls(8, 1, -6, 16, 6, 6, wall);
        s.box(9, 1, -5, 15, 7, 5, AIR);
        s.box(8, 1, -1, 8, 3, 1, AIR);
        s.crumble(3, 0.4f);
        // the Gate and its dais
        s.box(-6, 0, -14, 6, 0, -7, Mix.of(st(ModBlocks.WARDSTONE_BRICKS)).and(st(ModBlocks.CHISELED_WARDSTONE), 1));
        s.box(-3, 0, -10, 3, 0, -10, st(ModBlocks.WARDSTONE_BRICKS));
        s.put(0, 0, -10, st(ModBlocks.SUNDERED_KEYSTONE));
        s.box(-3, 1, -10, -3, 8, -10, pillar());
        s.box(3, 1, -10, 3, 8, -10, pillar());
        s.box(-2, 8, -10, 2, 8, -10, st(ModBlocks.CHISELED_WARDSTONE));
        s.put(-3, 9, -10, st(ModBlocks.CHISELED_WARDSTONE));
        s.put(3, 9, -10, st(ModBlocks.CHISELED_WARDSTONE));
        s.box(0, 9, -10, 0, 10, -10, st(ModBlocks.CHISELED_WARDSTONE));
        s.box(-2, 1, -10, 2, 7, -10, AIR);
        for (int x : new int[]{-6, 6}) {
            s.box(x, 1, -12, x, 3, -12, pillar());
            s.put(x, 4, -12, st(Blocks.SOUL_LANTERN));
        }
        s.put(0, 1, -4, st(ModBlocks.WAYSHRINE_BRAZIER));
        s.put(0, 0, -4, st(ModBlocks.CHISELED_WARDSTONE));
        s.put(-5, 1, -9, tablet(9, Direction.SOUTH));
        s.put(6, 1, 4, tablet(7, Direction.WEST));
        s.chest(15, 1, 0, Direction.WEST, loot("citadel_barracks"));
        s.chest(-15, 1, -15, Direction.SOUTH, loot("citadel_armory"));
        s.spawner(-15, 1, 15, ModEntities.FORSWORN_KNIGHT);
        for (int[] r : new int[][]{{-7, 5}, {7, 5}, {-7, -5}, {7, 9}}) s.resident(r[0], 1, r[1], ModEntities.FORSWORN_KNIGHT, 180f);
        // cache under the north-east tower
        s.box(13, -5, -17, 17, -1, -13, st(ModBlocks.WARDSTONE));
        s.hollow(14, -4, -16, 16, -2, -14);
        s.put(15, 0, -15, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.put(15, -1, -15, st(ModBlocks.CRACKED_WARDSTONE_BRICKS));
        s.chest(15, -4, -16, Direction.SOUTH, loot("citadel_secret"));
        s.put(14, -4, -14, candles(3));
        s.put(16, -4, -14, st(Blocks.COBWEB));
    }

    // ------------------------------------------------------------------ the Hollow Throne
    /**
     * Morvane's court on the Gloaming's central island: a ring of gloamstone guarded by four Ward Lanterns,
     * the throne dais to the north and a long causeway south to the arrival stone and the return veil.
     */
    private static void throne(Sketch s) {
        Mix floor = gloamBricks();
        Mix rock = Mix.of(st(ModBlocks.GLOAMSTONE)).and(st(ModBlocks.GLOAMSTONE), 5).and(st(ModBlocks.GLOAM_MOSS), 1).and(st(Blocks.BLACKSTONE), 1);
        s.footingState(st(ModBlocks.GLOAMSTONE)).footingDepth(10);
        // the arena volume and the causeway corridor are cleared of whatever the Gloaming grew there
        s.box(-17, 1, -17, 17, 22, 17, AIR);
        s.box(-3, 1, 16, 3, 9, 53, AIR);
        // the floating court: a disc of gloamstone with a ragged underside
        s.disc(0, 0, 0, 16.5, floor);
        s.underside(0, 0, 0, 16.5, 16, rock);
        s.put(0, -1, 0, st(ModBlocks.CHISELED_WARDSTONE));
        s.annulus(0, 0, 0, 5.0, 6.0, Mix.of(st(ModBlocks.CHISELED_WARDSTONE)));
        s.annulus(0, 0, 0, 10.0, 10.7, Mix.of(st(ModBlocks.WARDSTONE_BRICKS)));
        s.put(0, 0, 0, st(ModBlocks.LUMENITE_BLOCK));
        // rim with broken pillars
        s.annulus(0, 1, 0, 15.6, 16.5, Mix.of(st(ModBlocks.GLOAMSTONE_BRICKS)).and(Blocks.AIR.defaultBlockState(), 1));
        for (int i = 0; i < 12; i++) {
            double a = i * Math.PI / 6 + Math.PI / 12;
            int x = (int) Math.round(Math.cos(a) * 16), z = (int) Math.round(Math.sin(a) * 16);
            int h = 3 + s.rng.nextInt(5);
            s.box(x, 1, z, x, h, z, pillar());
            if (h >= 6) s.put(x, h + 1, z, st(Blocks.SOUL_LANTERN));
        }
        s.box(-2, 1, 15, 2, 6, 17, AIR);
        // the four Ward Lanterns on their plinths
        for (int[] c : new int[][]{{-9, -9}, {9, -9}, {-9, 9}, {9, 9}}) {
            s.put(c[0], 0, c[1], st(ModBlocks.CHISELED_WARDSTONE));
            s.put(c[0], 1, c[1], st(ModBlocks.WARD_LANTERN));
        }
        // throne dais and the throne itself (seat faces south, down the causeway)
        s.box(-4, 1, -14, 4, 1, -8, st(ModBlocks.GLOAMSTONE_BRICKS));
        s.box(-4, 1, -7, 4, 1, -7, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
        s.put(0, 2, -13, stairs(ModBlocks.WARDSTONE_BRICK_STAIRS, Direction.NORTH));
        s.box(-1, 2, -14, 1, 6, -14, st(ModBlocks.GLOAMSTONE_BRICKS));
        s.put(0, 7, -14, st(ModBlocks.CHISELED_WARDSTONE));
        s.put(-2, 7, -14, st(ModBlocks.GLOAMSTONE_BRICKS));
        s.put(2, 7, -14, st(ModBlocks.GLOAMSTONE_BRICKS));
        s.put(0, 8, -14, st(ModBlocks.GLOAMSTONE_BRICKS));
        s.put(-3, 2, -12, st(Blocks.SOUL_LANTERN));
        s.put(3, 2, -12, st(Blocks.SOUL_LANTERN));
        // the causeway south, carried on hanging pylons
        s.box(-2, 0, 17, 2, 0, 50, floor);
        for (int z = 20; z <= 44; z += 6) {
            for (int x : new int[]{-3, 3}) s.box(x, 0, z, x, 2 + s.rng.nextInt(3), z, pillar());
            s.underside(0, 0, z, 3.2, 7, rock);
        }
        s.put(3, 1, 20, tablet(8, Direction.WEST));
        // arrival stone and the return veil
        s.disc(0, 0, 46, 4.2, floor);
        s.underside(0, 0, 46, 4.5, 9, rock);
        s.box(-2, 1, 51, -2, 5, 51, pillar());
        s.box(2, 1, 51, 2, 5, 51, pillar());
        s.box(-2, 6, 51, 2, 6, 51, st(ModBlocks.CHISELED_WARDSTONE));
        s.box(-1, 1, 51, 1, 5, 51, st(ModBlocks.GLOAM_VEIL));
        s.box(-2, 0, 51, 2, 0, 51, floor);
        s.underside(0, 0, 51, 2.5, 4, rock);
        // veilbloom in the cracks of the court
        for (int i = 0; i < 26; i++) {
            double a = s.rng.nextDouble() * Math.PI * 2, r = 6.5 + s.rng.nextDouble() * 8.5;
            int x = (int) Math.round(Math.cos(a) * r), z = (int) Math.round(Math.sin(a) * r);
            if (s.at(x, 1, z) == null || s.at(x, 1, z).isAir()) {
                if (Math.abs(x) <= 2 && z > 5) continue;
                s.put(x, 0, z, st(ModBlocks.GLOAM_MOSS));
                s.put(x, 1, z, st(ModBlocks.VEILBLOOM));
            }
        }
    }

}
