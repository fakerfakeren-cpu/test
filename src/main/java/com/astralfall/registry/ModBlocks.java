package com.astralfall.registry;

import com.astralfall.Astralfall;
import com.astralfall.block.*;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TransparentBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Function;
import java.util.function.Supplier;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Astralfall.MODID);

    // --- meteorite & ores
    public static final RegistryObject<Block> METEORITE_ROCK = reg("meteorite_rock", GlowingMeteoriteBlock::new,
        () -> props(MapColor.COLOR_BLACK, 3.0f, 9.0f, SoundType.STONE).lightLevel(s -> 4).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> COOLED_METEORITE = reg("cooled_meteorite", Block::new,
        () -> props(MapColor.COLOR_BLACK, 2.5f, 9.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> METEORITE_BRICKS = reg("meteorite_bricks", Block::new,
        () -> props(MapColor.COLOR_BLACK, 3.0f, 9.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> STARMETAL_ORE = reg("starmetal_ore", GlowingMeteoriteBlock::new,
        () -> props(MapColor.COLOR_BLACK, 4.0f, 9.0f, SoundType.STONE).lightLevel(s -> 5).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> RAW_STARMETAL_BLOCK = reg("raw_starmetal_block", Block::new,
        () -> props(MapColor.COLOR_LIGHT_BLUE, 5.0f, 6.0f, SoundType.METAL).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> STARMETAL_BLOCK = reg("starmetal_block", Block::new,
        () -> props(MapColor.COLOR_LIGHT_BLUE, 5.0f, 6.0f, SoundType.METAL).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> SKYSHARD_BLOCK = reg("skyshard_block", Block::new,
        () -> props(MapColor.COLOR_CYAN, 1.5f, 1.5f, SoundType.AMETHYST).lightLevel(s -> 10));
    public static final RegistryObject<Block> SKYSHARD_CLUSTER = reg("skyshard_cluster", SkyshardClusterBlock::new,
        () -> props(MapColor.COLOR_CYAN, 1.5f, 1.5f, SoundType.AMETHYST_CLUSTER).lightLevel(s -> 8).noOcclusion().pushReaction(PushReaction.DESTROY));
    public static final RegistryObject<Block> VOID_STONE = reg("void_stone", Block::new,
        () -> props(MapColor.COLOR_PURPLE, 3.0f, 9.0f, SoundType.STONE).requiresCorrectToolForDrops());

    // --- observatory building set
    public static final RegistryObject<Block> ASTRAL_BRICKS = reg("astral_bricks", Block::new,
        () -> props(MapColor.COLOR_BLUE, 2.0f, 8.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> CRACKED_ASTRAL_BRICKS = reg("cracked_astral_bricks", Block::new,
        () -> props(MapColor.COLOR_BLUE, 2.0f, 8.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> OVERGROWN_ASTRAL_BRICKS = reg("overgrown_astral_bricks", Block::new,
        () -> props(MapColor.COLOR_BLUE, 2.0f, 8.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> CHISELED_ASTRAL_BRICKS = reg("chiseled_astral_bricks", Block::new,
        () -> props(MapColor.COLOR_BLUE, 2.0f, 8.0f, SoundType.STONE).lightLevel(s -> 3).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> ASTRAL_BRICK_STAIRS = reg("astral_brick_stairs",
        p -> new StairBlock(ASTRAL_BRICKS.get().defaultBlockState(), p),
        () -> props(MapColor.COLOR_BLUE, 2.0f, 8.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> ASTRAL_BRICK_SLAB = reg("astral_brick_slab", SlabBlock::new,
        () -> props(MapColor.COLOR_BLUE, 2.0f, 8.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> SEALED_ASTRAL_BRICKS = reg("sealed_astral_bricks", Block::new,
        () -> props(MapColor.COLOR_BLUE, -1.0f, 3600000.0f, SoundType.STONE).noLootTable());
    public static final RegistryObject<Block> ASTRAL_GLASS = reg("astral_glass", TransparentBlock::new,
        () -> props(MapColor.COLOR_BLUE, 0.5f, 1.0f, SoundType.GLASS).lightLevel(s -> 2).noOcclusion()
            .isViewBlocking((s, l, p) -> false).isRedstoneConductor((s, l, p) -> false));

    // --- functional
    public static final RegistryObject<Block> STAR_LOCK = reg("star_lock", StarLockBlock::new,
        () -> props(MapColor.GOLD, -1.0f, 3600000.0f, SoundType.STONE).lightLevel(s -> s.getValue(StarLockBlock.OPEN) ? 12 : 4).noLootTable());
    public static final RegistryObject<Block> ASTRAL_ALTAR = reg("astral_altar", AstralAltarBlock::new,
        () -> props(MapColor.COLOR_BLUE, 5.0f, 1200.0f, SoundType.STONE).lightLevel(s -> 9).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> STAR_JAR = reg("star_jar", StarJarBlock::new,
        () -> props(MapColor.GOLD, 0.3f, 0.3f, SoundType.GLASS).lightLevel(s -> 15).noOcclusion());
    public static final RegistryObject<Block> FALLEN_STAR = reg("fallen_star_block", FallenStarBlock::new,
        () -> props(MapColor.GOLD, 0.6f, 1200.0f, SoundType.AMETHYST).lightLevel(s -> 15).noOcclusion().pushReaction(PushReaction.BLOCK));
    public static final RegistryObject<Block> GRAVITY_RUNE = reg("gravity_rune", GravityRuneBlock::new,
        () -> props(MapColor.COLOR_PURPLE, 3.0f, 8.0f, SoundType.STONE).lightLevel(s -> s.getValue(GravityRuneBlock.ACTIVE) ? 10 : 3).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> STARFIRE_VENT = reg("starfire_vent", StarfireVentBlock::new,
        () -> props(MapColor.COLOR_ORANGE, 3.0f, 8.0f, SoundType.STONE).lightLevel(s -> s.getValue(StarfireVentBlock.ACTIVE) ? 13 : 5).randomTicks().requiresCorrectToolForDrops());
    public static final RegistryObject<Block> TELESCOPE_EYEPIECE = reg("telescope_eyepiece", TelescopeEyepieceBlock::new,
        () -> props(MapColor.GOLD, 4.0f, 1200.0f, SoundType.METAL).lightLevel(s -> 6).requiresCorrectToolForDrops());

    private static BlockBehaviour.Properties props(MapColor color, float hardness, float resistance, SoundType sound) {
        return BlockBehaviour.Properties.of().mapColor(color).strength(hardness, resistance).sound(sound);
    }

    private static <B extends Block> RegistryObject<Block> reg(String name, Function<BlockBehaviour.Properties, B> factory, Supplier<BlockBehaviour.Properties> props) {
        return BLOCKS.register(name, () -> factory.apply(props.get().setId(BLOCKS.key(name))));
    }

    private ModBlocks() {}
}
