package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import com.rimeheart.item.*;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ShovelItem;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Supplier;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Rimeheart.MODID);
    /** Creative-tab order. */
    public static final List<RegistryObject<? extends Item>> ORDER = new ArrayList<>();

    // ------------------------------------------------------------------ materials (tiers)
    /** Frostiron sits between iron and diamond. */
    public static final ToolMaterial FROSTIRON_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_IRON_TOOL, 700, 7.0f, 2.5f, 16, ModTags.FROSTIRON_REPAIR);
    /** Boss-tier weapon material: roughly netherite damage, lower durability. */
    public static final ToolMaterial SOVEREIGN_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1800, 8.0f, 3.5f, 15, ModTags.FROSTIRON_REPAIR);

    public static final ResourceKey<EquipmentAsset> FROSTIRON_ASSET = asset("frostiron");
    public static final ResourceKey<EquipmentAsset> WRAITHWEAVE_ASSET = asset("wraithweave");

    public static final ArmorMaterial FROSTIRON_ARMOR = new ArmorMaterial(22,
        Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 5, ArmorType.CHESTPLATE, 7, ArmorType.HELMET, 2, ArmorType.BODY, 7),
        12, SoundEvents.ARMOR_EQUIP_IRON, 0.5f, 0.0f, ModTags.FROSTIRON_REPAIR, FROSTIRON_ASSET);
    public static final ArmorMaterial WRAITHWEAVE_ARMOR = new ArmorMaterial(18,
        Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 4, ArmorType.CHESTPLATE, 5, ArmorType.HELMET, 2, ArmorType.BODY, 5),
        20, SoundEvents.ARMOR_EQUIP_LEATHER, 0.0f, 0.0f, ModTags.WRAITHWEAVE_REPAIR, WRAITHWEAVE_ASSET);

    // ------------------------------------------------------------------ guide
    public static final RegistryObject<Item> WARDENS_JOURNAL = reg("wardens_journal", JournalItem::new,
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));

    // ------------------------------------------------------------------ materials
    public static final RegistryObject<Item> RAW_FROSTIRON = reg("raw_frostiron", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> FROSTIRON_INGOT = reg("frostiron_ingot", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> FROSTIRON_NUGGET = reg("frostiron_nugget", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> RIME_SHARD = reg("rime_shard", p -> new LoreItem(p, 1, false), Item.Properties::new);
    public static final RegistryObject<Item> WRAITH_ESSENCE = reg("wraith_essence", p -> new LoreItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GLACIAL_HEART = reg("glacial_heart", p -> new LoreItem(p, 2, false), () -> new Item.Properties().rarity(Rarity.RARE).fireResistant());
    public static final RegistryObject<Item> SOVEREIGN_CORE = reg("sovereign_core", p -> new LoreItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.EPIC).fireResistant());

    // ------------------------------------------------------------------ tools
    public static final RegistryObject<Item> FROSTIRON_SWORD = reg("frostiron_sword", Item::new,
        () -> new Item.Properties().sword(FROSTIRON_TOOL, 3.0f, -2.4f));
    public static final RegistryObject<Item> FROSTIRON_PICKAXE = reg("frostiron_pickaxe", Item::new,
        () -> new Item.Properties().pickaxe(FROSTIRON_TOOL, 1.0f, -2.8f));
    public static final RegistryObject<Item> FROSTIRON_AXE = reg("frostiron_axe", p -> new AxeItem(FROSTIRON_TOOL, 6.0f, -3.1f, p), Item.Properties::new);
    public static final RegistryObject<Item> FROSTIRON_SHOVEL = reg("frostiron_shovel", p -> new ShovelItem(FROSTIRON_TOOL, 1.5f, -3.0f, p), Item.Properties::new);

    // ------------------------------------------------------------------ weapons & gadgets
    public static final RegistryObject<Item> FROSTBITE_BLADE = reg("frostbite_blade", FrostbiteBladeItem::new,
        () -> new Item.Properties().sword(FROSTIRON_TOOL, 3.5f, -2.4f).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GLACIER_MAUL = reg("glacier_maul", GlacierMaulItem::new,
        () -> new Item.Properties().sword(FROSTIRON_TOOL, 6.0f, -3.2f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> RIMEBOW = reg("rimebow", RimebowItem::new,
        () -> new Item.Properties().durability(384).enchantable(14).rarity(Rarity.RARE));
    public static final RegistryObject<Item> BLIZZARD_STAFF = reg("blizzard_staff", BlizzardStaffItem::new,
        () -> new Item.Properties().durability(250).rarity(Rarity.RARE));
    public static final RegistryObject<Item> WINTERFANG = reg("winterfang", WinterfangItem::new,
        () -> new Item.Properties().sword(SOVEREIGN_TOOL, 4.5f, -2.4f).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> FROST_CHARGE = reg("frost_charge", FrostChargeItem::new,
        () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> WINTER_HORN = reg("winter_horn", WinterHornItem::new,
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> HEARTHFIRE_STEW = reg("hearthfire_stew", HearthfireStewItem::new,
        () -> new Item.Properties().stacksTo(1)
            .food(new FoodProperties.Builder().nutrition(8).saturationModifier(0.8f).build())
            .usingConvertsTo(Items.BOWL));

    // ------------------------------------------------------------------ armour
    public static final RegistryObject<Item> FROSTIRON_HELMET = armor("frostiron_helmet", FROSTIRON_ARMOR, ArmorType.HELMET, Rarity.COMMON);
    public static final RegistryObject<Item> FROSTIRON_CHESTPLATE = armor("frostiron_chestplate", FROSTIRON_ARMOR, ArmorType.CHESTPLATE, Rarity.COMMON);
    public static final RegistryObject<Item> FROSTIRON_LEGGINGS = armor("frostiron_leggings", FROSTIRON_ARMOR, ArmorType.LEGGINGS, Rarity.COMMON);
    public static final RegistryObject<Item> FROSTIRON_BOOTS = armor("frostiron_boots", FROSTIRON_ARMOR, ArmorType.BOOTS, Rarity.COMMON);
    public static final RegistryObject<Item> WRAITHWEAVE_HOOD = armor("wraithweave_hood", WRAITHWEAVE_ARMOR, ArmorType.HELMET, Rarity.UNCOMMON);
    public static final RegistryObject<Item> WRAITHWEAVE_ROBE = armor("wraithweave_robe", WRAITHWEAVE_ARMOR, ArmorType.CHESTPLATE, Rarity.UNCOMMON);
    public static final RegistryObject<Item> WRAITHWEAVE_LEGGINGS = armor("wraithweave_leggings", WRAITHWEAVE_ARMOR, ArmorType.LEGGINGS, Rarity.UNCOMMON);
    public static final RegistryObject<Item> WRAITHWEAVE_BOOTS = armor("wraithweave_boots", WRAITHWEAVE_ARMOR, ArmorType.BOOTS, Rarity.UNCOMMON);

    // ------------------------------------------------------------------ spawn eggs
    public static final RegistryObject<Item> FROST_WRAITH_SPAWN_EGG = egg("frost_wraith_spawn_egg", () -> ModEntities.FROST_WRAITH.get());
    public static final RegistryObject<Item> SHARDLING_SPAWN_EGG = egg("shardling_spawn_egg", () -> ModEntities.SHARDLING.get());
    public static final RegistryObject<Item> FROST_SOVEREIGN_SPAWN_EGG = egg("frost_sovereign_spawn_egg", () -> ModEntities.FROST_SOVEREIGN.get());

    // ------------------------------------------------------------------ block items
    static {
        for (var entry : ModBlocks.BLOCKS.getEntries()) {
            String name = entry.getId().getPath();
            Rarity rarity = switch (name) {
                case "glacial_altar" -> Rarity.RARE;
                case "rime_crystal_cluster", "rime_crystal_block" -> Rarity.UNCOMMON;
                default -> Rarity.COMMON;
            };
            ORDER.add(ITEMS.register(name, () -> new BlockItem(entry.get(), new Item.Properties().setId(ITEMS.key(name)).useBlockDescriptionPrefix().rarity(rarity))));
        }
    }

    private static ResourceKey<EquipmentAsset> asset(String name) {
        return ResourceKey.create(EquipmentAssets.ROOT_ID, Identifier.fromNamespaceAndPath(Rimeheart.MODID, name));
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
