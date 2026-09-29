package com.oathbound.registry;

import com.oathbound.Oathbound;
import com.oathbound.block.*;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Function;
import java.util.function.Supplier;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Oathbound.MODID);

    // --- ores & metals
    public static final RegistryObject<Block> LUMENITE_ORE = reg("lumenite_ore", p -> new DropExperienceBlock(UniformInt.of(2, 5), p),
        () -> props(MapColor.STONE, 3.0f, 3.0f, SoundType.STONE).lightLevel(s -> 4).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> DEEPSLATE_LUMENITE_ORE = reg("deepslate_lumenite_ore", p -> new DropExperienceBlock(UniformInt.of(2, 5), p),
        () -> props(MapColor.DEEPSLATE, 4.5f, 3.0f, SoundType.DEEPSLATE).lightLevel(s -> 4).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> LUMENITE_BLOCK = reg("lumenite_block", Block::new,
        () -> props(MapColor.GOLD, 3.0f, 6.0f, SoundType.AMETHYST).lightLevel(s -> 15).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> OATHSTEEL_BLOCK = reg("oathsteel_block", Block::new,
        () -> props(MapColor.METAL, 5.0f, 8.0f, SoundType.METAL).requiresCorrectToolForDrops());

    // --- Lanternguard masonry
    public static final RegistryObject<Block> WARDSTONE = reg("wardstone", Block::new, ModBlocks::wardstone);
    public static final RegistryObject<Block> WARDSTONE_BRICKS = reg("wardstone_bricks", Block::new, ModBlocks::wardstone);
    public static final RegistryObject<Block> CRACKED_WARDSTONE_BRICKS = reg("cracked_wardstone_bricks", Block::new,
        () -> props(MapColor.SAND, 1.2f, 4.0f, SoundType.STONE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> MOSSY_WARDSTONE_BRICKS = reg("mossy_wardstone_bricks", Block::new, ModBlocks::wardstone);
    public static final RegistryObject<Block> CHISELED_WARDSTONE = reg("chiseled_wardstone", Block::new, () -> wardstone().lightLevel(s -> 6));
    public static final RegistryObject<Block> WARDSTONE_BRICK_STAIRS = reg("wardstone_brick_stairs",
        p -> new StairBlock(WARDSTONE_BRICKS.get().defaultBlockState(), p), ModBlocks::wardstone);
    public static final RegistryObject<Block> WARDSTONE_BRICK_SLAB = reg("wardstone_brick_slab", SlabBlock::new, ModBlocks::wardstone);
    public static final RegistryObject<Block> WARDSTONE_PILLAR = reg("wardstone_pillar", RotatedPillarBlock::new, ModBlocks::wardstone);

    // --- the Gloam
    public static final RegistryObject<Block> GLOAMSTONE = reg("gloamstone", Block::new,
        () -> props(MapColor.COLOR_PURPLE, 2.0f, 6.0f, SoundType.DEEPSLATE).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> GLOAM_MOSS = reg("gloam_moss", Block::new,
        () -> props(MapColor.COLOR_PURPLE, 2.0f, 6.0f, SoundType.MOSS).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> GLOAMSTONE_BRICKS = reg("gloamstone_bricks", Block::new,
        () -> props(MapColor.COLOR_PURPLE, 2.5f, 6.0f, SoundType.DEEPSLATE_BRICKS).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> GLOAMWOOD_LOG = reg("gloamwood_log", RotatedPillarBlock::new,
        () -> props(MapColor.COLOR_BLACK, 2.0f, 2.0f, SoundType.WOOD));
    public static final RegistryObject<Block> GLOAMWOOD_PLANKS = reg("gloamwood_planks", Block::new,
        () -> props(MapColor.COLOR_BLACK, 2.0f, 3.0f, SoundType.WOOD));
    public static final RegistryObject<Block> VEILBLOOM = reg("veilbloom", VeilbloomBlock::new,
        () -> props(MapColor.COLOR_PURPLE, 0.0f, 0.0f, SoundType.GRASS).noCollision().instabreak().lightLevel(s -> 7).noOcclusion()
            .offsetType(BlockBehaviour.OffsetType.XZ).pushReaction(PushReaction.DESTROY));

    // --- puzzles, relics and rites
    public static final RegistryObject<Block> LORE_TABLET = reg("lore_tablet", LoreTabletBlock::new,
        () -> props(MapColor.SAND, -1.0f, 3600000.0f, SoundType.STONE).noLootTable().lightLevel(s -> 3));
    public static final RegistryObject<Block> WAYSHRINE_BRAZIER = reg("wayshrine_brazier", WayshrineBrazierBlock::new,
        () -> props(MapColor.GOLD, 3.5f, 1200.0f, SoundType.METAL).noOcclusion().lightLevel(s -> s.getValue(WayshrineBrazierBlock.LIT) ? 15 : 2).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> CHAPEL_BELL = reg("chapel_bell", ChapelBellBlock::new,
        () -> props(MapColor.GOLD, -1.0f, 3600000.0f, SoundType.ANVIL).noOcclusion().noLootTable());
    public static final RegistryObject<Block> HYMN_STONE = reg("hymn_stone", HymnStoneBlock::new,
        () -> props(MapColor.WARPED_WART_BLOCK, -1.0f, 3600000.0f, SoundType.STONE).noLootTable().lightLevel(s -> s.getValue(HymnStoneBlock.SOLVED) ? 12 : 5));
    public static final RegistryObject<Block> RUNE_DIAL = reg("rune_dial", RuneDialBlock::new,
        () -> props(MapColor.COLOR_BLUE, -1.0f, 3600000.0f, SoundType.STONE).noLootTable().lightLevel(s -> 7));
    public static final RegistryObject<Block> CIPHER_LECTERN = reg("cipher_lectern", CipherLecternBlock::new,
        () -> props(MapColor.COLOR_BLUE, -1.0f, 3600000.0f, SoundType.STONE).noOcclusion().noLootTable().lightLevel(s -> s.getValue(CipherLecternBlock.SOLVED) ? 12 : 6));
    public static final RegistryObject<Block> ARCANE_WARD = reg("arcane_ward", ArcaneWardBlock::new,
        () -> props(MapColor.COLOR_LIGHT_BLUE, -1.0f, 3600000.0f, SoundType.AMETHYST).noLootTable().noOcclusion().lightLevel(s -> 10)
            .isViewBlocking((s, l, p) -> false).isRedstoneConductor((s, l, p) -> false).isSuffocating((s, l, p) -> false));
    public static final RegistryObject<Block> SEALED_GRATE = reg("sealed_grate", SealedBlock::new,
        () -> props(MapColor.COLOR_GRAY, -1.0f, 3600000.0f, SoundType.CHAIN).noLootTable().noOcclusion()
            .isViewBlocking((s, l, p) -> false).isSuffocating((s, l, p) -> false));
    public static final RegistryObject<Block> BARROW_SEAL = reg("barrow_seal", SealedBlock::new,
        () -> props(MapColor.STONE, -1.0f, 3600000.0f, SoundType.STONE).noLootTable());
    public static final RegistryObject<Block> SARCOPHAGUS = reg("sarcophagus", SarcophagusBlock::new,
        () -> props(MapColor.STONE, -1.0f, 3600000.0f, SoundType.STONE).noLootTable().noOcclusion());
    public static final RegistryObject<Block> WARD_LANTERN = reg("ward_lantern", WardLanternBlock::new,
        () -> props(MapColor.GOLD, -1.0f, 3600000.0f, SoundType.LANTERN).noLootTable().noOcclusion().lightLevel(s -> s.getValue(WardLanternBlock.LIT) ? 15 : 0));
    public static final RegistryObject<Block> SUNDERED_KEYSTONE = reg("sundered_keystone", SunderedKeystoneBlock::new,
        () -> props(MapColor.COLOR_PURPLE, -1.0f, 3600000.0f, SoundType.STONE).noLootTable().lightLevel(s -> s.getValue(SunderedKeystoneBlock.ACTIVE) ? 15 : 4));
    public static final RegistryObject<Block> GLOAM_VEIL = reg("gloam_veil", GloamVeilBlock::new,
        () -> props(MapColor.COLOR_PURPLE, -1.0f, 3600000.0f, SoundType.GLASS).noLootTable().noCollision().noOcclusion().lightLevel(s -> 11)
            .pushReaction(PushReaction.BLOCK));
    public static final RegistryObject<Block> WISPLIGHT = reg("wisplight", WisplightBlock::new,
        () -> BlockBehaviour.Properties.of().replaceable().noCollision().noLootTable().air().instabreak().lightLevel(s -> 14).noOcclusion());

    private static BlockBehaviour.Properties wardstone() {
        return props(MapColor.SAND, 2.0f, 7.0f, SoundType.STONE).requiresCorrectToolForDrops();
    }

    private static BlockBehaviour.Properties props(MapColor color, float hardness, float resistance, SoundType sound) {
        return BlockBehaviour.Properties.of().mapColor(color).strength(hardness, resistance).sound(sound);
    }

    private static <B extends Block> RegistryObject<Block> reg(String name, Function<BlockBehaviour.Properties, B> factory, Supplier<BlockBehaviour.Properties> props) {
        return BLOCKS.register(name, () -> factory.apply(props.get().setId(BLOCKS.key(name))));
    }

    private ModBlocks() {}
}
