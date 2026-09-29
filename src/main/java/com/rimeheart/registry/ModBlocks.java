package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import com.rimeheart.block.GlacialAltarBlock;
import com.rimeheart.block.RimeCrystalClusterBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Function;
import java.util.function.Supplier;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Rimeheart.MODID);

    // --- natural
    public static final RegistryObject<Block> RIMESTONE = reg("rimestone", Block::new,
        () -> props(MapColor.ICE, 1.5f, 6.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> PERMAFROST = reg("permafrost", Block::new,
        () -> props(MapColor.COLOR_LIGHT_BLUE, 1.2f, 3.0f, SoundType.GRAVEL).friction(0.9f));
    public static final RegistryObject<Block> FROSTIRON_ORE = reg("frostiron_ore", Block::new,
        () -> props(MapColor.STONE, 3.0f, 3.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> RIME_CRYSTAL_ORE = reg("rime_crystal_ore", Block::new,
        () -> props(MapColor.ICE, 3.0f, 3.0f, SoundType.STONE).lightLevel(s -> 4).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> RIME_CRYSTAL_CLUSTER = reg("rime_crystal_cluster", RimeCrystalClusterBlock::new,
        () -> props(MapColor.ICE, 1.5f, 1.5f, SoundType.AMETHYST_CLUSTER).lightLevel(s -> 7).noOcclusion().pushReaction(PushReaction.DESTROY));

    // --- storage
    public static final RegistryObject<Block> FROSTIRON_BLOCK = reg("frostiron_block", Block::new,
        () -> props(MapColor.COLOR_LIGHT_BLUE, 5.0f, 6.0f, SoundType.METAL).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> RIME_CRYSTAL_BLOCK = reg("rime_crystal_block", Block::new,
        () -> props(MapColor.ICE, 1.5f, 1.5f, SoundType.AMETHYST).lightLevel(s -> 9));

    // --- sanctum building set
    public static final RegistryObject<Block> RIMESTONE_BRICKS = reg("rimestone_bricks", Block::new,
        () -> props(MapColor.ICE, 2.0f, 6.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> CRACKED_RIMESTONE_BRICKS = reg("cracked_rimestone_bricks", Block::new,
        () -> props(MapColor.ICE, 2.0f, 6.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> CHISELED_RIMESTONE_BRICKS = reg("chiseled_rimestone_bricks", Block::new,
        () -> props(MapColor.ICE, 2.0f, 6.0f, SoundType.STONE).lightLevel(s -> 3).requiresCorrectToolForDrops());
    /** Secret-passage block: looks exactly like Rimestone Bricks but crumbles at a touch and drops nothing. */
    public static final RegistryObject<Block> HOLLOW_RIMESTONE_BRICKS = reg("hollow_rimestone_bricks", Block::new,
        () -> props(MapColor.ICE, 0.4f, 0.4f, SoundType.STONE).noLootTable());
    public static final RegistryObject<Block> FROST_LAMP = reg("frost_lamp", Block::new,
        () -> props(MapColor.ICE, 0.8f, 0.8f, SoundType.GLASS).lightLevel(s -> 15));
    public static final RegistryObject<Block> GLACIAL_ALTAR = reg("glacial_altar", GlacialAltarBlock::new,
        () -> props(MapColor.ICE, 5.0f, 1200.0f, SoundType.STONE).lightLevel(s -> 9).requiresCorrectToolForDrops());

    private static BlockBehaviour.Properties props(MapColor color, float hardness, float resistance, SoundType sound) {
        return BlockBehaviour.Properties.of().mapColor(color).strength(hardness, resistance).sound(sound);
    }

    private static <B extends Block> RegistryObject<Block> reg(String name, Function<BlockBehaviour.Properties, B> factory, Supplier<BlockBehaviour.Properties> props) {
        return BLOCKS.register(name, () -> factory.apply(props.get().setId(BLOCKS.key(name))));
    }

    private ModBlocks() {}
}
