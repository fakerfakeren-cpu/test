package com.oathbound.registry;

import com.oathbound.Oathbound;
import com.oathbound.block.*;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ButtonBlock;
import net.minecraft.world.level.block.CarpetBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.FlowerPotBlock;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.PressurePlateBlock;
import net.minecraft.world.level.block.RedstoneLampBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TransparentBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.block.state.properties.WoodType;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Function;
import java.util.function.Supplier;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Oathbound.MODID);

    /** Gloamwood doors, trapdoors, buttons and plates: wooden sounds, opened by hand. */
    public static final BlockSetType GLOAMWOOD_SET = BlockSetType.register(new BlockSetType("oathbound:gloamwood"));
    public static final WoodType GLOAMWOOD_TYPE = WoodType.register(new WoodType("oathbound:gloamwood", GLOAMWOOD_SET));

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
    public static final RegistryObject<Block> GLOAMSTONE = reg("gloamstone", Block::new, ModBlocks::gloamstone);
    public static final RegistryObject<Block> GLOAM_MOSS = reg("gloam_moss", Block::new,
        () -> props(MapColor.COLOR_PURPLE, 2.0f, 6.0f, SoundType.MOSS).requiresCorrectToolForDrops());
    public static final RegistryObject<Block> GLOAMSTONE_BRICKS = reg("gloamstone_bricks", Block::new,
        () -> gloamstone().strength(2.5f, 6.0f).sound(SoundType.DEEPSLATE_BRICKS));
    public static final RegistryObject<Block> GLOAMWOOD_LOG = reg("gloamwood_log", p -> new StrippableLogBlock(() -> ModBlocks.STRIPPED_GLOAMWOOD_LOG.get(), p),
        ModBlocks::gloamwood);
    public static final RegistryObject<Block> GLOAMWOOD_PLANKS = reg("gloamwood_planks", Block::new, () -> gloamwood().strength(2.0f, 3.0f));
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

    // ------------------------------------------------------------------ material presets
    // ------------------------------------------------------------------ building families (generated by tools/oath/building.py)
    public static final RegistryObject<Block> WARDSTONE_STAIRS = reg("wardstone_stairs", p -> new StairBlock(ModBlocks.WARDSTONE.get().defaultBlockState(), p), () -> wardstone());
    public static final RegistryObject<Block> WARDSTONE_SLAB = reg("wardstone_slab", SlabBlock::new, () -> wardstone());
    public static final RegistryObject<Block> WARDSTONE_WALL = reg("wardstone_wall", WallBlock::new, () -> wardstone().forceSolidOn());
    public static final RegistryObject<Block> WARDSTONE_BRICK_WALL = reg("wardstone_brick_wall", WallBlock::new, () -> wardstone().forceSolidOn());
    public static final RegistryObject<Block> MOSSY_WARDSTONE_BRICK_STAIRS = reg("mossy_wardstone_brick_stairs", p -> new StairBlock(ModBlocks.MOSSY_WARDSTONE_BRICKS.get().defaultBlockState(), p), () -> wardstone());
    public static final RegistryObject<Block> MOSSY_WARDSTONE_BRICK_SLAB = reg("mossy_wardstone_brick_slab", SlabBlock::new, () -> wardstone());
    public static final RegistryObject<Block> MOSSY_WARDSTONE_BRICK_WALL = reg("mossy_wardstone_brick_wall", WallBlock::new, () -> wardstone().forceSolidOn());
    public static final RegistryObject<Block> POLISHED_WARDSTONE = reg("polished_wardstone", Block::new, () -> wardstone());
    public static final RegistryObject<Block> POLISHED_WARDSTONE_STAIRS = reg("polished_wardstone_stairs", p -> new StairBlock(ModBlocks.POLISHED_WARDSTONE.get().defaultBlockState(), p), () -> wardstone());
    public static final RegistryObject<Block> POLISHED_WARDSTONE_SLAB = reg("polished_wardstone_slab", SlabBlock::new, () -> wardstone());
    public static final RegistryObject<Block> WARDSTONE_TILES = reg("wardstone_tiles", Block::new, () -> wardstone());
    public static final RegistryObject<Block> WARDSTONE_BUTTON = reg("wardstone_button", p -> new ButtonBlock(BlockSetType.STONE, 20, p), () -> button(SoundType.STONE));
    public static final RegistryObject<Block> WARDSTONE_PRESSURE_PLATE = reg("wardstone_pressure_plate", p -> new PressurePlateBlock(BlockSetType.STONE, p), () -> wardstone().forceSolidOn().noCollision().strength(0.5f).pushReaction(PushReaction.DESTROY));
    public static final RegistryObject<Block> GLOAMSTONE_STAIRS = reg("gloamstone_stairs", p -> new StairBlock(ModBlocks.GLOAMSTONE.get().defaultBlockState(), p), () -> gloamstone());
    public static final RegistryObject<Block> GLOAMSTONE_SLAB = reg("gloamstone_slab", SlabBlock::new, () -> gloamstone());
    public static final RegistryObject<Block> GLOAMSTONE_WALL = reg("gloamstone_wall", WallBlock::new, () -> gloamstone().forceSolidOn());
    public static final RegistryObject<Block> GLOAMSTONE_BRICK_STAIRS = reg("gloamstone_brick_stairs", p -> new StairBlock(ModBlocks.GLOAMSTONE_BRICKS.get().defaultBlockState(), p), () -> gloamstone());
    public static final RegistryObject<Block> GLOAMSTONE_BRICK_SLAB = reg("gloamstone_brick_slab", SlabBlock::new, () -> gloamstone());
    public static final RegistryObject<Block> GLOAMSTONE_BRICK_WALL = reg("gloamstone_brick_wall", WallBlock::new, () -> gloamstone().forceSolidOn());
    public static final RegistryObject<Block> CRACKED_GLOAMSTONE_BRICKS = reg("cracked_gloamstone_bricks", Block::new, () -> gloamstone());
    public static final RegistryObject<Block> POLISHED_GLOAMSTONE = reg("polished_gloamstone", Block::new, () -> gloamstone());
    public static final RegistryObject<Block> POLISHED_GLOAMSTONE_STAIRS = reg("polished_gloamstone_stairs", p -> new StairBlock(ModBlocks.POLISHED_GLOAMSTONE.get().defaultBlockState(), p), () -> gloamstone());
    public static final RegistryObject<Block> POLISHED_GLOAMSTONE_SLAB = reg("polished_gloamstone_slab", SlabBlock::new, () -> gloamstone());
    public static final RegistryObject<Block> CHISELED_GLOAMSTONE = reg("chiseled_gloamstone", Block::new, () -> gloamstone().lightLevel(s -> 7));
    public static final RegistryObject<Block> GLOAMSTONE_TILES = reg("gloamstone_tiles", Block::new, () -> gloamstone());
    public static final RegistryObject<Block> GLOAMWOOD = reg("gloamwood", p -> new StrippableLogBlock(() -> ModBlocks.STRIPPED_GLOAMWOOD.get(), p), () -> gloamwood());
    public static final RegistryObject<Block> STRIPPED_GLOAMWOOD_LOG = reg("stripped_gloamwood_log", RotatedPillarBlock::new, () -> gloamwood());
    public static final RegistryObject<Block> STRIPPED_GLOAMWOOD = reg("stripped_gloamwood", RotatedPillarBlock::new, () -> gloamwood());
    public static final RegistryObject<Block> GLOAMWOOD_STAIRS = reg("gloamwood_stairs", p -> new StairBlock(ModBlocks.GLOAMWOOD_PLANKS.get().defaultBlockState(), p), () -> gloamwood());
    public static final RegistryObject<Block> GLOAMWOOD_SLAB = reg("gloamwood_slab", SlabBlock::new, () -> gloamwood());
    public static final RegistryObject<Block> GLOAMWOOD_FENCE = reg("gloamwood_fence", FenceBlock::new, () -> gloamwood().forceSolidOn());
    public static final RegistryObject<Block> GLOAMWOOD_FENCE_GATE = reg("gloamwood_fence_gate", p -> new FenceGateBlock(GLOAMWOOD_TYPE, p), () -> gloamwood().forceSolidOn());
    public static final RegistryObject<Block> GLOAMWOOD_DOOR = reg("gloamwood_door", p -> new DoorBlock(GLOAMWOOD_SET, p), () -> gloamwood().strength(3.0f).noOcclusion().pushReaction(PushReaction.DESTROY));
    public static final RegistryObject<Block> GLOAMWOOD_TRAPDOOR = reg("gloamwood_trapdoor", p -> new TrapDoorBlock(GLOAMWOOD_SET, p), () -> gloamwood().strength(3.0f).noOcclusion().isValidSpawn((s, l, pos, t) -> false));
    public static final RegistryObject<Block> GLOAMWOOD_BUTTON = reg("gloamwood_button", p -> new ButtonBlock(GLOAMWOOD_SET, 30, p), () -> button(SoundType.WOOD));
    public static final RegistryObject<Block> GLOAMWOOD_PRESSURE_PLATE = reg("gloamwood_pressure_plate", p -> new PressurePlateBlock(GLOAMWOOD_SET, p), () -> gloamwood().forceSolidOn().noCollision().strength(0.5f).pushReaction(PushReaction.DESTROY));
    public static final RegistryObject<Block> GLOAMWOOD_LEAVES = reg("gloamwood_leaves", GloamLeavesBlock::new, ModBlocks::leaves);
    public static final RegistryObject<Block> GLOAMWOOD_SAPLING = reg("gloamwood_sapling", GloamSaplingBlock::new, () -> plant(MapColor.COLOR_PURPLE).randomTicks().lightLevel(s -> 2));
    public static final RegistryObject<Block> TIDESTONE = reg("tidestone", Block::new, () -> tidestone());
    public static final RegistryObject<Block> TIDESTONE_BRICKS = reg("tidestone_bricks", Block::new, () -> tidestone());
    public static final RegistryObject<Block> BARNACLED_TIDESTONE_BRICKS = reg("barnacled_tidestone_bricks", Block::new, () -> tidestone());
    public static final RegistryObject<Block> CHISELED_TIDESTONE = reg("chiseled_tidestone", Block::new, () -> tidestone().lightLevel(s -> 6));
    public static final RegistryObject<Block> TIDESTONE_BRICK_STAIRS = reg("tidestone_brick_stairs", p -> new StairBlock(ModBlocks.TIDESTONE_BRICKS.get().defaultBlockState(), p), () -> tidestone());
    public static final RegistryObject<Block> TIDESTONE_BRICK_SLAB = reg("tidestone_brick_slab", SlabBlock::new, () -> tidestone());
    public static final RegistryObject<Block> TIDESTONE_BRICK_WALL = reg("tidestone_brick_wall", WallBlock::new, () -> tidestone().forceSolidOn());
    public static final RegistryObject<Block> BARROWSTONE = reg("barrowstone", Block::new, () -> barrowstone());
    public static final RegistryObject<Block> BARROWSTONE_BRICKS = reg("barrowstone_bricks", Block::new, () -> barrowstone());
    public static final RegistryObject<Block> BONE_INLAID_BARROWSTONE = reg("bone_inlaid_barrowstone", Block::new, () -> barrowstone());
    public static final RegistryObject<Block> BARROWSTONE_BRICK_STAIRS = reg("barrowstone_brick_stairs", p -> new StairBlock(ModBlocks.BARROWSTONE_BRICKS.get().defaultBlockState(), p), () -> barrowstone());
    public static final RegistryObject<Block> BARROWSTONE_BRICK_SLAB = reg("barrowstone_brick_slab", SlabBlock::new, () -> barrowstone());
    public static final RegistryObject<Block> BARROWSTONE_BRICK_WALL = reg("barrowstone_brick_wall", WallBlock::new, () -> barrowstone().forceSolidOn());
    public static final RegistryObject<Block> RUNESTONE = reg("runestone", Block::new, () -> runestone());
    public static final RegistryObject<Block> RUNESTONE_BRICKS = reg("runestone_bricks", Block::new, () -> runestone());
    public static final RegistryObject<Block> GLYPHED_RUNESTONE = reg("glyphed_runestone", Block::new, () -> runestone().lightLevel(s -> 8));
    public static final RegistryObject<Block> RUNESTONE_BRICK_STAIRS = reg("runestone_brick_stairs", p -> new StairBlock(ModBlocks.RUNESTONE_BRICKS.get().defaultBlockState(), p), () -> runestone());
    public static final RegistryObject<Block> RUNESTONE_BRICK_SLAB = reg("runestone_brick_slab", SlabBlock::new, () -> runestone());
    public static final RegistryObject<Block> RUNESTONE_BRICK_WALL = reg("runestone_brick_wall", WallBlock::new, () -> runestone().forceSolidOn());
    public static final RegistryObject<Block> LUMENITE_LAMP = reg("lumenite_lamp", RedstoneLampBlock::new, () -> BlockBehaviour.Properties.of().mapColor(MapColor.GOLD).strength(0.3f).sound(SoundType.GLASS).lightLevel(s -> s.getValue(RedstoneLampBlock.LIT) ? 15 : 0));
    public static final RegistryObject<Block> LANTERNGLASS = reg("lanternglass", TransparentBlock::new, () -> glass(MapColor.COLOR_ORANGE));
    public static final RegistryObject<Block> GLOAMGLASS = reg("gloamglass", TransparentBlock::new, () -> glass(MapColor.COLOR_PURPLE));
    public static final RegistryObject<Block> OATHSTEEL_BARS = reg("oathsteel_bars", IronBarsBlock::new, () -> BlockBehaviour.Properties.of().requiresCorrectToolForDrops().strength(5.0f, 6.0f).sound(SoundType.METAL).noOcclusion());
    public static final RegistryObject<Block> OATHSTEEL_LANTERN = reg("oathsteel_lantern", LanternBlock::new, () -> lantern(15));
    public static final RegistryObject<Block> GLOAM_LANTERN = reg("gloam_lantern", LanternBlock::new, () -> lantern(12));
    public static final RegistryObject<Block> GLIMMER_MOSS = reg("glimmer_moss", CarpetBlock::new, () -> BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(0.1f).sound(SoundType.MOSS_CARPET).pushReaction(PushReaction.DESTROY).lightLevel(s -> 3));
    public static final RegistryObject<Block> DUSK_LILY = reg("dusk_lily", p -> new OathFlowerBlock(MobEffects.NIGHT_VISION, 5f, OathFlowerBlock.Glint.DUSK, p), () -> plant(MapColor.COLOR_PURPLE).offsetType(BlockBehaviour.OffsetType.XZ).lightLevel(s -> 5));
    public static final RegistryObject<Block> EMBERROOT = reg("emberroot", p -> new OathFlowerBlock(MobEffects.FIRE_RESISTANCE, 4f, OathFlowerBlock.Glint.EMBER, p), () -> plant(MapColor.COLOR_ORANGE).offsetType(BlockBehaviour.OffsetType.XZ).lightLevel(s -> 6));
    public static final RegistryObject<Block> MOONPETAL = reg("moonpetal", p -> new OathFlowerBlock(MobEffects.REGENERATION, 6f, OathFlowerBlock.Glint.MOON, p), () -> plant(MapColor.COLOR_LIGHT_BLUE).offsetType(BlockBehaviour.OffsetType.XZ).lightLevel(s -> 4));
    public static final RegistryObject<Block> GLOAM_FERN = reg("gloam_fern", p -> new OathFlowerBlock(MobEffects.NIGHT_VISION, 3f, OathFlowerBlock.Glint.GLOAM, p), () -> plant(MapColor.COLOR_PURPLE).offsetType(BlockBehaviour.OffsetType.XZ).lightLevel(s -> 3));
    public static final RegistryObject<Block> POTTED_DUSK_LILY = reg("potted_dusk_lily", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.DUSK_LILY.get(), p), () -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY).lightLevel(s -> 5));
    public static final RegistryObject<Block> POTTED_EMBERROOT = reg("potted_emberroot", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.EMBERROOT.get(), p), () -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY).lightLevel(s -> 6));
    public static final RegistryObject<Block> POTTED_MOONPETAL = reg("potted_moonpetal", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.MOONPETAL.get(), p), () -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY).lightLevel(s -> 4));
    public static final RegistryObject<Block> POTTED_GLOAM_FERN = reg("potted_gloam_fern", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.GLOAM_FERN.get(), p), () -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY).lightLevel(s -> 3));
    public static final RegistryObject<Block> POTTED_VEILBLOOM = reg("potted_veilbloom", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.VEILBLOOM.get(), p), () -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY).lightLevel(s -> 7));
    public static final RegistryObject<Block> POTTED_GLOAMWOOD_SAPLING = reg("potted_gloamwood_sapling", p -> new FlowerPotBlock(() -> (FlowerPotBlock) Blocks.FLOWER_POT, () -> ModBlocks.GLOAMWOOD_SAPLING.get(), p), () -> BlockBehaviour.Properties.of().instabreak().noOcclusion().pushReaction(PushReaction.DESTROY));
    // ------------------------------------------------------------------ end of building families

    private static BlockBehaviour.Properties wardstone() {
        return props(MapColor.SAND, 2.0f, 7.0f, SoundType.STONE).requiresCorrectToolForDrops();
    }

    private static BlockBehaviour.Properties gloamstone() {
        return props(MapColor.COLOR_PURPLE, 2.0f, 6.0f, SoundType.DEEPSLATE).requiresCorrectToolForDrops();
    }

    /** Gloamwood is dusk-grown: like the woods of the Nether it does not burn. */
    private static BlockBehaviour.Properties gloamwood() {
        return props(MapColor.COLOR_BLACK, 2.0f, 2.0f, SoundType.CHERRY_WOOD);
    }

    private static BlockBehaviour.Properties tidestone() {
        return props(MapColor.WARPED_NYLIUM, 1.8f, 6.0f, SoundType.STONE).requiresCorrectToolForDrops();
    }

    private static BlockBehaviour.Properties barrowstone() {
        return props(MapColor.TERRACOTTA_GRAY, 2.0f, 6.0f, SoundType.TUFF).requiresCorrectToolForDrops();
    }

    private static BlockBehaviour.Properties runestone() {
        return props(MapColor.COLOR_BLUE, 2.5f, 8.0f, SoundType.DEEPSLATE_TILES).requiresCorrectToolForDrops();
    }

    private static BlockBehaviour.Properties leaves() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(0.2f).randomTicks().sound(SoundType.AZALEA_LEAVES)
            .noOcclusion().isValidSpawn((s, l, p, t) -> false).isSuffocating((s, l, p) -> false).isViewBlocking((s, l, p) -> false)
            .pushReaction(PushReaction.DESTROY).isRedstoneConductor((s, l, p) -> false).lightLevel(s -> 3);
    }

    private static BlockBehaviour.Properties plant(MapColor color) {
        return BlockBehaviour.Properties.of().mapColor(color).noCollision().instabreak().sound(SoundType.GRASS).pushReaction(PushReaction.DESTROY);
    }

    private static BlockBehaviour.Properties glass(MapColor color) {
        return BlockBehaviour.Properties.of().mapColor(color).strength(0.3f).sound(SoundType.GLASS).noOcclusion()
            .isValidSpawn((s, l, p, t) -> false).isRedstoneConductor((s, l, p) -> false).isSuffocating((s, l, p) -> false)
            .isViewBlocking((s, l, p) -> false);
    }

    private static BlockBehaviour.Properties button(SoundType sound) {
        return BlockBehaviour.Properties.of().noCollision().strength(0.5f).sound(sound).pushReaction(PushReaction.DESTROY);
    }

    private static BlockBehaviour.Properties lantern(int light) {
        return BlockBehaviour.Properties.of().mapColor(MapColor.METAL).forceSolidOn().strength(3.5f).sound(SoundType.LANTERN)
            .lightLevel(s -> light).noOcclusion().pushReaction(PushReaction.DESTROY);
    }

    private static BlockBehaviour.Properties props(MapColor color, float hardness, float resistance, SoundType sound) {
        return BlockBehaviour.Properties.of().mapColor(color).strength(hardness, resistance).sound(sound);
    }

    private static <B extends Block> RegistryObject<Block> reg(String name, Function<BlockBehaviour.Properties, B> factory, Supplier<BlockBehaviour.Properties> props) {
        return BLOCKS.register(name, () -> factory.apply(props.get().setId(BLOCKS.key(name))));
    }

    private ModBlocks() {}
}
