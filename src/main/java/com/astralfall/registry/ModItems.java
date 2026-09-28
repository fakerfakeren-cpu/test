package com.astralfall.registry;

import com.astralfall.Astralfall;
import com.astralfall.item.*;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Unit;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.WrittenBookItem;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Supplier;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Astralfall.MODID);
    /** Creative-tab order. */
    public static final List<RegistryObject<? extends Item>> ORDER = new ArrayList<>();

    // ------------------------------------------------------------------ materials
    public static final ToolMaterial STARMETAL_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1800, 9.0f, 3.0f, 18, ModTags.STARMETAL_REPAIR);
    public static final ToolMaterial VOID_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1400, 8.0f, 3.5f, 20, ModTags.VOIDWALKER_REPAIR);
    public static final ToolMaterial ECLIPSE_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 3000, 10.0f, 5.0f, 22, ModTags.STARMETAL_REPAIR);

    public static final ResourceKey<EquipmentAsset> STARMETAL_ASSET = asset("starmetal");
    public static final ResourceKey<EquipmentAsset> VOIDWALKER_ASSET = asset("voidwalker");
    public static final ResourceKey<EquipmentAsset> CROWN_ASSET = asset("crown_of_astraeus");
    public static final ResourceKey<EquipmentAsset> WINGS_ASSET = asset("nebula_wings");

    public static final ArmorMaterial STARMETAL_ARMOR = new ArmorMaterial(35,
        Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 8, ArmorType.HELMET, 3, ArmorType.BODY, 11),
        15, SoundEvents.ARMOR_EQUIP_IRON, 2.5f, 0.1f, ModTags.STARMETAL_REPAIR, STARMETAL_ASSET);
    public static final ArmorMaterial VOIDWALKER_ARMOR = new ArmorMaterial(30,
        Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 7, ArmorType.HELMET, 3, ArmorType.BODY, 10),
        20, SoundEvents.ARMOR_EQUIP_LEATHER, 2.0f, 0.0f, ModTags.VOIDWALKER_REPAIR, VOIDWALKER_ASSET);
    public static final ArmorMaterial CROWN_ARMOR = new ArmorMaterial(40,
        Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 8, ArmorType.HELMET, 5, ArmorType.BODY, 11),
        25, SoundEvents.ARMOR_EQUIP_GOLD, 3.5f, 0.1f, ModTags.STARMETAL_REPAIR, CROWN_ASSET);

    // ------------------------------------------------------------------ guide
    public static final RegistryObject<Item> ASTRAL_JOURNAL = reg("astral_journal", WrittenBookItem::new,
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON).component(DataComponents.WRITTEN_BOOK_CONTENT, AstralJournal.content()));

    // ------------------------------------------------------------------ materials
    public static final RegistryObject<Item> RAW_STARMETAL = reg("raw_starmetal", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> STARMETAL_INGOT = reg("starmetal_ingot", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> STARMETAL_NUGGET = reg("starmetal_nugget", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> SKYSHARD = reg("skyshard", p -> new LoreItem(p, 1, false), Item.Properties::new);
    public static final RegistryObject<Item> STARDUST = reg("stardust", p -> new LoreItem(p, 1, false), Item.Properties::new);
    public static final RegistryObject<Item> VOID_ESSENCE = reg("void_essence", p -> new LoreItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> FALLEN_STAR_SHARD = reg("fallen_star", p -> new LoreItem(p, 2, false), () -> new Item.Properties().rarity(Rarity.RARE).fireResistant());
    public static final RegistryObject<Item> STELLAR_CORE = reg("stellar_core", p -> new LoreItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> ECLIPSE_SIGIL = reg("eclipse_sigil", p -> new LoreItem(p, 3, true), () -> new Item.Properties().rarity(Rarity.EPIC).stacksTo(1).fireResistant());

    // ------------------------------------------------------------------ weapons & tools
    public static final RegistryObject<Item> STARBLADE = reg("starblade", StarbladeItem::new,
        () -> new Item.Properties().sword(STARMETAL_TOOL, 4.0f, -2.2f).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> COMET_MAUL = reg("comet_maul", CometMaulItem::new,
        () -> new Item.Properties().sword(STARMETAL_TOOL, 7.5f, -3.3f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> RIFTCALLER = reg("riftcaller", RiftcallerItem::new,
        () -> new Item.Properties().sword(VOID_TOOL, 5.0f, -2.6f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> CONSTELLATION_BOW = reg("constellation_bow", ConstellationBowItem::new,
        () -> new Item.Properties().durability(640).rarity(Rarity.RARE).enchantable(15));
    public static final RegistryObject<Item> ECLIPSE_GREATSWORD = reg("eclipse_greatsword", EclipseGreatswordItem::new,
        () -> new Item.Properties().sword(ECLIPSE_TOOL, 9.0f, -2.9f).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> STARMETAL_PICKAXE = reg("starmetal_pickaxe", StarmetalPickaxeItem::new,
        () -> new Item.Properties().pickaxe(STARMETAL_TOOL, 1.0f, -2.8f).rarity(Rarity.UNCOMMON));

    // ------------------------------------------------------------------ gadgets
    public static final RegistryObject<Item> GRAVITY_GAUNTLET = reg("gravity_gauntlet", GravityGauntletItem::new,
        () -> new Item.Properties().durability(500).rarity(Rarity.RARE));
    public static final RegistryObject<Item> SINGULARITY_GRENADE = reg("singularity_grenade", SingularityGrenadeItem::new,
        () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> ASTRAL_COMPASS = reg("astral_compass", AstralCompassItem::new,
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));

    // ------------------------------------------------------------------ armour
    public static final RegistryObject<Item> STARMETAL_HELMET = armor("starmetal_helmet", STARMETAL_ARMOR, ArmorType.HELMET, Rarity.UNCOMMON);
    public static final RegistryObject<Item> STARMETAL_CHESTPLATE = armor("starmetal_chestplate", STARMETAL_ARMOR, ArmorType.CHESTPLATE, Rarity.UNCOMMON);
    public static final RegistryObject<Item> STARMETAL_LEGGINGS = armor("starmetal_leggings", STARMETAL_ARMOR, ArmorType.LEGGINGS, Rarity.UNCOMMON);
    public static final RegistryObject<Item> STARMETAL_BOOTS = armor("starmetal_boots", STARMETAL_ARMOR, ArmorType.BOOTS, Rarity.UNCOMMON);
    public static final RegistryObject<Item> VOIDWALKER_HELMET = armor("voidwalker_helmet", VOIDWALKER_ARMOR, ArmorType.HELMET, Rarity.RARE);
    public static final RegistryObject<Item> VOIDWALKER_CHESTPLATE = armor("voidwalker_chestplate", VOIDWALKER_ARMOR, ArmorType.CHESTPLATE, Rarity.RARE);
    public static final RegistryObject<Item> VOIDWALKER_LEGGINGS = armor("voidwalker_leggings", VOIDWALKER_ARMOR, ArmorType.LEGGINGS, Rarity.RARE);
    public static final RegistryObject<Item> VOIDWALKER_BOOTS = armor("voidwalker_boots", VOIDWALKER_ARMOR, ArmorType.BOOTS, Rarity.RARE);
    public static final RegistryObject<Item> CROWN_OF_ASTRAEUS = reg("crown_of_astraeus", p -> new LoreItem(p, 3, false),
        () -> new Item.Properties().humanoidArmor(CROWN_ARMOR, ArmorType.HELMET).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> NEBULA_WINGS = reg("nebula_wings", p -> new LoreItem(p, 3, false),
        () -> new Item.Properties().durability(864).rarity(Rarity.EPIC)
            .component(DataComponents.GLIDER, Unit.INSTANCE)
            .component(DataComponents.EQUIPPABLE, Equippable.builder(EquipmentSlot.CHEST).setEquipSound(SoundEvents.ARMOR_EQUIP_ELYTRA).setAsset(WINGS_ASSET).setDamageOnHurt(false).build())
            .repairable(ModTags.VOIDWALKER_REPAIR));

    // ------------------------------------------------------------------ spawn eggs
    public static final RegistryObject<Item> ASTRAL_WISP_SPAWN_EGG = egg("astral_wisp_spawn_egg", () -> ModEntities.ASTRAL_WISP.get());
    public static final RegistryObject<Item> VOID_STALKER_SPAWN_EGG = egg("void_stalker_spawn_egg", () -> ModEntities.VOID_STALKER.get());
    public static final RegistryObject<Item> METEORITE_CRAWLER_SPAWN_EGG = egg("meteorite_crawler_spawn_egg", () -> ModEntities.METEORITE_CRAWLER.get());
    public static final RegistryObject<Item> VOID_GAZER_SPAWN_EGG = egg("void_gazer_spawn_egg", () -> ModEntities.VOID_GAZER.get());
    public static final RegistryObject<Item> ASTRAEUS_SPAWN_EGG = egg("astraeus_spawn_egg", () -> ModEntities.ASTRAEUS.get());

    // ------------------------------------------------------------------ block items
    static {
        for (var entry : ModBlocks.BLOCKS.getEntries()) {
            String name = entry.getId().getPath();
            Rarity rarity = switch (name) {
                case "sealed_astral_bricks", "star_lock" -> Rarity.EPIC;
                case "fallen_star_block", "astral_altar", "telescope_eyepiece", "star_jar" -> Rarity.RARE;
                default -> Rarity.COMMON;
            };
            ORDER.add(ITEMS.register(name, () -> new BlockItem(entry.get(), new Item.Properties().setId(ITEMS.key(name)).useBlockDescriptionPrefix().rarity(rarity))));
        }
    }

    private static ResourceKey<EquipmentAsset> asset(String name) {
        return ResourceKey.create(EquipmentAssets.ROOT_ID, Identifier.fromNamespaceAndPath(Astralfall.MODID, name));
    }

    private static RegistryObject<Item> armor(String name, ArmorMaterial material, ArmorType type, Rarity rarity) {
        return reg(name, Item::new, () -> new Item.Properties().humanoidArmor(material, type).rarity(rarity));
    }

    private static RegistryObject<Item> egg(String name, Supplier<net.minecraft.world.entity.EntityType<?>> type) {
        return reg(name, SpawnEggItem::new, () -> new Item.Properties().spawnEgg(type.get()));
    }

    private static <I extends Item> RegistryObject<Item> reg(String name, Function<Item.Properties, I> factory, Supplier<Item.Properties> props) {
        RegistryObject<Item> ro = ITEMS.register(name, () -> factory.apply(props.get().setId(ITEMS.key(name))));
        ORDER.add(ro);
        return ro;
    }

    private ModItems() {}
}
