package com.oathbound.registry;

import com.oathbound.Oathbound;
import com.oathbound.item.*;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.consume_effects.ApplyStatusEffectsConsumeEffect;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ShovelItem;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.component.ItemAttributeModifiers;
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
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Oathbound.MODID);
    /** Creative-tab order. */
    public static final List<RegistryObject<? extends Item>> ORDER = new ArrayList<>();

    // ------------------------------------------------------------------ materials
    public static final ToolMaterial OATHSTEEL_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_IRON_TOOL, 900, 7.5f, 2.5f, 16, ModTags.OATHSTEEL_REPAIR);
    public static final ToolMaterial KEEPER_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1500, 8.0f, 3.0f, 18, ModTags.OATHSTEEL_REPAIR);
    public static final ToolMaterial GLOAM_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1600, 8.0f, 3.5f, 20, ModTags.OATHSTEEL_REPAIR);
    public static final ToolMaterial DAWN_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 2600, 9.0f, 5.0f, 22, ModTags.OATHSTEEL_REPAIR);

    public static final ResourceKey<EquipmentAsset> OATHSTEEL_ASSET = asset("oathsteel");
    public static final ResourceKey<EquipmentAsset> ARCANIST_ASSET = asset("arcanist");
    public static final ResourceKey<EquipmentAsset> CROWN_ASSET = asset("hollow_crown");

    public static final ArmorMaterial OATHSTEEL_ARMOR = new ArmorMaterial(25,
        Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 7, ArmorType.HELMET, 2, ArmorType.BODY, 9),
        14, SoundEvents.ARMOR_EQUIP_IRON, 1.0f, 0.0f, ModTags.OATHSTEEL_REPAIR, OATHSTEEL_ASSET);
    public static final ArmorMaterial ARCANIST_ARMOR = new ArmorMaterial(22,
        Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 4, ArmorType.CHESTPLATE, 6, ArmorType.HELMET, 2, ArmorType.BODY, 7),
        25, SoundEvents.ARMOR_EQUIP_LEATHER, 1.0f, 0.0f, ModTags.SPELLSILK_REPAIR, ARCANIST_ASSET);
    public static final ArmorMaterial CROWN_ARMOR = new ArmorMaterial(45,
        Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 8, ArmorType.HELMET, 4, ArmorType.BODY, 11),
        25, SoundEvents.ARMOR_EQUIP_GOLD, 3.0f, 0.1f, ModTags.OATHSTEEL_REPAIR, CROWN_ASSET);

    // ------------------------------------------------------------------ the Chronicle
    public static final RegistryObject<Item> LANTERN_CHRONICLE = reg("lantern_chronicle", ChronicleItem::new,
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));

    // ------------------------------------------------------------------ materials
    public static final RegistryObject<Item> LUMENITE_SHARD = reg("lumenite_shard", LumeniteShardItem::new, Item.Properties::new);
    public static final RegistryObject<Item> LUMENITE_DUST = reg("lumenite_dust", p -> new InscribedItem(p, 1, false), Item.Properties::new);
    public static final RegistryObject<Item> OATHSTEEL_BLEND = reg("oathsteel_blend", p -> new InscribedItem(p, 1, false), Item.Properties::new);
    public static final RegistryObject<Item> OATHSTEEL_INGOT = reg("oathsteel_ingot", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> OATHSTEEL_NUGGET = reg("oathsteel_nugget", Item::new, Item.Properties::new);
    public static final RegistryObject<Item> SPELLSILK = reg("spellsilk", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LUMINOUS_DUST = reg("luminous_dust", p -> new InscribedItem(p, 1, false), Item.Properties::new);
    public static final RegistryObject<Item> GLOAM_ESSENCE = reg("gloam_essence", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LANTERNGUARD_INSIGNIA = reg("lanternguard_insignia", p -> new InscribedItem(p, 2, false), () -> new Item.Properties().rarity(Rarity.RARE).stacksTo(16));
    public static final RegistryObject<Item> SEAL_OF_VALOR = reg("seal_of_valor", p -> new InscribedItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.RARE).stacksTo(1).fireResistant());
    public static final RegistryObject<Item> SEAL_OF_WISDOM = reg("seal_of_wisdom", p -> new InscribedItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.RARE).stacksTo(1).fireResistant());
    public static final RegistryObject<Item> SEAL_OF_SACRIFICE = reg("seal_of_sacrifice", p -> new InscribedItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.RARE).stacksTo(1).fireResistant());
    public static final RegistryObject<Item> OATHKEY = reg("oathkey", com.oathbound.item.OathkeyItem::new, () -> new Item.Properties().rarity(Rarity.EPIC).stacksTo(1).fireResistant());
    public static final RegistryObject<Item> EVERFLAME_EMBER = reg("everflame_ember", p -> new InscribedItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.EPIC).fireResistant());

    // ------------------------------------------------------------------ lanterns
    public static final RegistryObject<Item> WARDENS_LANTERN = reg("wardens_lantern", p -> new WardensLanternItem(p, false),
        () -> new Item.Properties().stacksTo(1).durability(480).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> EVERFLAME_LANTERN = reg("everflame_lantern", p -> new WardensLanternItem(p, true),
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant());

    // ------------------------------------------------------------------ weapons
    public static final RegistryObject<Item> OATHSTEEL_LONGSWORD = reg("oathsteel_longsword", p -> new InscribedItem(p, 2, false),
        () -> new Item.Properties().sword(OATHSTEEL_TOOL, 3.0f, -2.4f).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> WARDENS_HALBERD = reg("wardens_halberd", p -> new InscribedItem(p, 2, false),
        () -> new Item.Properties().sword(OATHSTEEL_TOOL, 5.0f, -3.0f).attributes(halberdAttributes()).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> DROWNED_ANCHOR = reg("drowned_anchor", DrownedAnchorItem::new,
        () -> new Item.Properties().sword(KEEPER_TOOL, 6.5f, -3.2f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> STAFF_OF_VEYL = reg("staff_of_veyl", StaffOfVeylItem::new,
        () -> new Item.Properties().durability(700).rarity(Rarity.RARE).enchantable(20).repairable(ModTags.SPELLSILK_REPAIR));
    public static final RegistryObject<Item> DAWNSTRING_LONGBOW = reg("dawnstring_longbow", DawnstringBowItem::new,
        () -> new Item.Properties().durability(760).rarity(Rarity.RARE).enchantable(16).repairable(ModTags.SPELLSILK_REPAIR));
    public static final RegistryObject<Item> HOUSECARL_WARHORN = reg("housecarl_warhorn", WarhornItem::new,
        () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
    public static final RegistryObject<Item> SHADOWREAP_SICKLE = reg("shadowreap_sickle", p -> new InscribedItem(p, 2, false),
        () -> new Item.Properties().sword(GLOAM_TOOL, 3.5f, -2.0f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> DAWNBREAKER = reg("dawnbreaker", DawnbreakerItem::new,
        () -> new Item.Properties().sword(DAWN_TOOL, 5.0f, -2.8f).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> LUMEN_FLASK = reg("lumen_flask", LumenFlaskItem::new,
        () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON));

    // ------------------------------------------------------------------ tools
    public static final RegistryObject<Item> OATHSTEEL_PICKAXE = reg("oathsteel_pickaxe", Item::new,
        () -> new Item.Properties().pickaxe(OATHSTEEL_TOOL, 1.0f, -2.8f));
    public static final RegistryObject<Item> OATHSTEEL_AXE = reg("oathsteel_axe", p -> new AxeItem(OATHSTEEL_TOOL, 6.0f, -3.1f, p), Item.Properties::new);
    public static final RegistryObject<Item> OATHSTEEL_SHOVEL = reg("oathsteel_shovel", p -> new ShovelItem(OATHSTEEL_TOOL, 1.5f, -3.0f, p), Item.Properties::new);

    // ------------------------------------------------------------------ armour
    public static final RegistryObject<Item> OATHSTEEL_HELMET = armor("oathsteel_helmet", OATHSTEEL_ARMOR, ArmorType.HELMET, Rarity.COMMON);
    public static final RegistryObject<Item> OATHSTEEL_CHESTPLATE = armor("oathsteel_chestplate", OATHSTEEL_ARMOR, ArmorType.CHESTPLATE, Rarity.COMMON);
    public static final RegistryObject<Item> OATHSTEEL_LEGGINGS = armor("oathsteel_leggings", OATHSTEEL_ARMOR, ArmorType.LEGGINGS, Rarity.COMMON);
    public static final RegistryObject<Item> OATHSTEEL_BOOTS = armor("oathsteel_boots", OATHSTEEL_ARMOR, ArmorType.BOOTS, Rarity.COMMON);
    public static final RegistryObject<Item> ARCANIST_HOOD = armor("arcanist_hood", ARCANIST_ARMOR, ArmorType.HELMET, Rarity.UNCOMMON);
    public static final RegistryObject<Item> ARCANIST_ROBE = armor("arcanist_robe", ARCANIST_ARMOR, ArmorType.CHESTPLATE, Rarity.UNCOMMON);
    public static final RegistryObject<Item> ARCANIST_LEGGINGS = armor("arcanist_leggings", ARCANIST_ARMOR, ArmorType.LEGGINGS, Rarity.UNCOMMON);
    public static final RegistryObject<Item> ARCANIST_BOOTS = armor("arcanist_boots", ARCANIST_ARMOR, ArmorType.BOOTS, Rarity.UNCOMMON);
    public static final RegistryObject<Item> HOLLOW_CROWN = reg("hollow_crown", p -> new InscribedItem(p, 3, false),
        () -> new Item.Properties().humanoidArmor(CROWN_ARMOR, ArmorType.HELMET).rarity(Rarity.EPIC).fireResistant());

    // ------------------------------------------------------------------ food & drink
    public static final RegistryObject<Item> WAYFARERS_BREAD = reg("wayfarers_bread", p -> new InscribedItem(p, 1, false),
        () -> new Item.Properties().food(new FoodProperties(7, 0.9f, false)));
    public static final RegistryObject<Item> HONEYED_MEAD = reg("honeyed_mead", p -> new OathFoodItem(p, OathFoodItem.Kind.MEAD),
        () -> new Item.Properties().stacksTo(16).food(new FoodProperties(3, 0.4f, true), net.minecraft.world.item.component.Consumables.DEFAULT_DRINK)
            .usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> KNIGHTS_STEW = reg("knights_stew", p -> new OathFoodItem(p, OathFoodItem.Kind.STEW),
        () -> new Item.Properties().stacksTo(1).food(new FoodProperties(10, 1.0f, false)).usingConvertsTo(net.minecraft.world.item.Items.BOWL));
    public static final RegistryObject<Item> ELIXIR_OF_DAWN = reg("elixir_of_dawn", p -> new OathFoodItem(p, OathFoodItem.Kind.ELIXIR),
        () -> new Item.Properties().stacksTo(16).rarity(Rarity.RARE).food(new FoodProperties(0, 0.0f, true), net.minecraft.world.item.component.Consumables.DEFAULT_DRINK)
            .usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));

    // ------------------------------------------------------------------ gear tiers (generated by tools/oath/gear.py)
    public static final RegistryObject<Item> OATHSTEEL_HOE = reg("oathsteel_hoe", p -> new net.minecraft.world.item.HoeItem(OATHSTEEL_TOOL, -2.0f, -1.0f, p), Item.Properties::new);
    public static final net.minecraft.tags.TagKey<Item> TIDEBRONZE_REPAIR = net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM, Identifier.fromNamespaceAndPath(Oathbound.MODID, "tidebronze_repair"));
    public static final ToolMaterial TIDEBRONZE_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_IRON_TOOL, 600, 7.0f, 2.0f, 18, TIDEBRONZE_REPAIR);
    public static final ResourceKey<EquipmentAsset> TIDEBRONZE_ASSET = asset("tidebronze");
    public static final ArmorMaterial TIDEBRONZE_ARMOR = new ArmorMaterial(18, Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 5, ArmorType.CHESTPLATE, 6, ArmorType.HELMET, 2, ArmorType.BODY, 7), 16, SoundEvents.ARMOR_EQUIP_CHAIN, 0.0f, 0.0f, TIDEBRONZE_REPAIR, TIDEBRONZE_ASSET);
    public static final RegistryObject<Item> TIDEBRONZE_BLEND = reg("tidebronze_blend", p -> new InscribedItem(p, 1, false), () -> new Item.Properties());
    public static final RegistryObject<Item> TIDEBRONZE_INGOT = reg("tidebronze_ingot", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_GLADIUS = reg("tidebronze_gladius", p -> new InscribedItem(p, 2, false), () -> new Item.Properties().sword(TIDEBRONZE_TOOL, 3.0f, -2.0f).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> TIDEBRONZE_PICKAXE = reg("tidebronze_pickaxe", Item::new, () -> new Item.Properties().pickaxe(TIDEBRONZE_TOOL, 1.0f, -2.8f).rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_AXE = reg("tidebronze_axe", p -> new AxeItem(TIDEBRONZE_TOOL, 5.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_SHOVEL = reg("tidebronze_shovel", p -> new ShovelItem(TIDEBRONZE_TOOL, 1.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_HOE = reg("tidebronze_hoe", p -> new net.minecraft.world.item.HoeItem(TIDEBRONZE_TOOL, -2.0f, -1.0f, p), () -> new Item.Properties().rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_HELMET = reg("tidebronze_helmet", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(TIDEBRONZE_ARMOR, ArmorType.HELMET).rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_CHESTPLATE = reg("tidebronze_chestplate", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(TIDEBRONZE_ARMOR, ArmorType.CHESTPLATE).rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_LEGGINGS = reg("tidebronze_leggings", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(TIDEBRONZE_ARMOR, ArmorType.LEGGINGS).rarity(Rarity.COMMON));
    public static final RegistryObject<Item> TIDEBRONZE_BOOTS = reg("tidebronze_boots", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(TIDEBRONZE_ARMOR, ArmorType.BOOTS).rarity(Rarity.COMMON));
    public static final net.minecraft.tags.TagKey<Item> RUNESILVER_REPAIR = net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM, Identifier.fromNamespaceAndPath(Oathbound.MODID, "runesilver_repair"));
    public static final ToolMaterial RUNESILVER_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_IRON_TOOL, 820, 7.5f, 2.5f, 28, RUNESILVER_REPAIR);
    public static final ResourceKey<EquipmentAsset> RUNESILVER_ASSET = asset("runesilver");
    public static final ArmorMaterial RUNESILVER_ARMOR = new ArmorMaterial(22, Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 5, ArmorType.CHESTPLATE, 6, ArmorType.HELMET, 2, ArmorType.BODY, 7), 28, SoundEvents.ARMOR_EQUIP_CHAIN, 0.5f, 0.0f, RUNESILVER_REPAIR, RUNESILVER_ASSET);
    public static final RegistryObject<Item> RUNESILVER_BLEND = reg("runesilver_blend", p -> new InscribedItem(p, 1, false), () -> new Item.Properties());
    public static final RegistryObject<Item> RUNESILVER_INGOT = reg("runesilver_ingot", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_RAPIER = reg("runesilver_rapier", p -> new InscribedItem(p, 2, false), () -> new Item.Properties().sword(RUNESILVER_TOOL, 2.0f, -1.6f).attributes(weapon(4.5, -1.6, 0.75)).rarity(Rarity.RARE));
    public static final RegistryObject<Item> RUNESILVER_PICKAXE = reg("runesilver_pickaxe", Item::new, () -> new Item.Properties().pickaxe(RUNESILVER_TOOL, 1.0f, -2.8f).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_AXE = reg("runesilver_axe", p -> new AxeItem(RUNESILVER_TOOL, 5.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_SHOVEL = reg("runesilver_shovel", p -> new ShovelItem(RUNESILVER_TOOL, 1.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_HOE = reg("runesilver_hoe", p -> new net.minecraft.world.item.HoeItem(RUNESILVER_TOOL, -2.0f, -1.0f, p), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_HELMET = reg("runesilver_helmet", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(RUNESILVER_ARMOR, ArmorType.HELMET).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_CHESTPLATE = reg("runesilver_chestplate", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(RUNESILVER_ARMOR, ArmorType.CHESTPLATE).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_LEGGINGS = reg("runesilver_leggings", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(RUNESILVER_ARMOR, ArmorType.LEGGINGS).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> RUNESILVER_BOOTS = reg("runesilver_boots", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(RUNESILVER_ARMOR, ArmorType.BOOTS).rarity(Rarity.UNCOMMON));
    public static final net.minecraft.tags.TagKey<Item> GRAVEGOLD_REPAIR = net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM, Identifier.fromNamespaceAndPath(Oathbound.MODID, "gravegold_repair"));
    public static final ToolMaterial GRAVEGOLD_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1150, 8.0f, 3.0f, 22, GRAVEGOLD_REPAIR);
    public static final ResourceKey<EquipmentAsset> GRAVEGOLD_ASSET = asset("gravegold");
    public static final ArmorMaterial GRAVEGOLD_ARMOR = new ArmorMaterial(30, Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 7, ArmorType.HELMET, 3, ArmorType.BODY, 9), 22, SoundEvents.ARMOR_EQUIP_GOLD, 1.5f, 0.0f, GRAVEGOLD_REPAIR, GRAVEGOLD_ASSET);
    public static final RegistryObject<Item> GRAVEGOLD_BLEND = reg("gravegold_blend", p -> new InscribedItem(p, 1, false), () -> new Item.Properties());
    public static final RegistryObject<Item> GRAVEGOLD_INGOT = reg("gravegold_ingot", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_KHOPESH = reg("gravegold_khopesh", p -> new InscribedItem(p, 2, false), () -> new Item.Properties().sword(GRAVEGOLD_TOOL, 4.0f, -2.6f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> GRAVEGOLD_PICKAXE = reg("gravegold_pickaxe", Item::new, () -> new Item.Properties().pickaxe(GRAVEGOLD_TOOL, 1.0f, -2.8f).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_AXE = reg("gravegold_axe", p -> new AxeItem(GRAVEGOLD_TOOL, 5.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_SHOVEL = reg("gravegold_shovel", p -> new ShovelItem(GRAVEGOLD_TOOL, 1.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_HOE = reg("gravegold_hoe", p -> new net.minecraft.world.item.HoeItem(GRAVEGOLD_TOOL, -3.0f, 0.0f, p), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_HELMET = reg("gravegold_helmet", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(GRAVEGOLD_ARMOR, ArmorType.HELMET).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_CHESTPLATE = reg("gravegold_chestplate", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(GRAVEGOLD_ARMOR, ArmorType.CHESTPLATE).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_LEGGINGS = reg("gravegold_leggings", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(GRAVEGOLD_ARMOR, ArmorType.LEGGINGS).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GRAVEGOLD_BOOTS = reg("gravegold_boots", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(GRAVEGOLD_ARMOR, ArmorType.BOOTS).rarity(Rarity.UNCOMMON));
    public static final net.minecraft.tags.TagKey<Item> DUSKIRON_REPAIR = net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM, Identifier.fromNamespaceAndPath(Oathbound.MODID, "duskiron_repair"));
    public static final ToolMaterial DUSKIRON_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_DIAMOND_TOOL, 1800, 8.5f, 3.5f, 14, DUSKIRON_REPAIR);
    public static final ResourceKey<EquipmentAsset> DUSKIRON_ASSET = asset("duskiron");
    public static final ArmorMaterial DUSKIRON_ARMOR = new ArmorMaterial(35, Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 8, ArmorType.HELMET, 3, ArmorType.BODY, 11), 12, SoundEvents.ARMOR_EQUIP_NETHERITE, 2.5f, 0.05f, DUSKIRON_REPAIR, DUSKIRON_ASSET);
    public static final RegistryObject<Item> RAW_DUSKIRON = reg("raw_duskiron", p -> new InscribedItem(p, 1, false), () -> new Item.Properties());
    public static final RegistryObject<Item> DUSKIRON_INGOT = reg("duskiron_ingot", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_GLAIVE = reg("duskiron_glaive", p -> new InscribedItem(p, 2, false), () -> new Item.Properties().sword(DUSKIRON_TOOL, 5.5f, -3.0f).attributes(weapon(9.0, -3.0, 1.5)).rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_PICKAXE = reg("duskiron_pickaxe", Item::new, () -> new Item.Properties().pickaxe(DUSKIRON_TOOL, 1.0f, -2.8f).rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_AXE = reg("duskiron_axe", p -> new AxeItem(DUSKIRON_TOOL, 5.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_SHOVEL = reg("duskiron_shovel", p -> new ShovelItem(DUSKIRON_TOOL, 1.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_HOE = reg("duskiron_hoe", p -> new net.minecraft.world.item.HoeItem(DUSKIRON_TOOL, -3.0f, 0.0f, p), () -> new Item.Properties().rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_HELMET = reg("duskiron_helmet", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DUSKIRON_ARMOR, ArmorType.HELMET).rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_CHESTPLATE = reg("duskiron_chestplate", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DUSKIRON_ARMOR, ArmorType.CHESTPLATE).rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_LEGGINGS = reg("duskiron_leggings", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DUSKIRON_ARMOR, ArmorType.LEGGINGS).rarity(Rarity.RARE));
    public static final RegistryObject<Item> DUSKIRON_BOOTS = reg("duskiron_boots", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DUSKIRON_ARMOR, ArmorType.BOOTS).rarity(Rarity.RARE));
    public static final net.minecraft.tags.TagKey<Item> DAWNSTEEL_REPAIR = net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM, Identifier.fromNamespaceAndPath(Oathbound.MODID, "dawnsteel_repair"));
    public static final ToolMaterial DAWNSTEEL_TOOL = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 2600, 9.5f, 4.5f, 20, DAWNSTEEL_REPAIR);
    public static final ResourceKey<EquipmentAsset> DAWNSTEEL_ASSET = asset("dawnsteel");
    public static final ArmorMaterial DAWNSTEEL_ARMOR = new ArmorMaterial(40, Map.of(ArmorType.BOOTS, 3, ArmorType.LEGGINGS, 6, ArmorType.CHESTPLATE, 8, ArmorType.HELMET, 3, ArmorType.BODY, 11), 20, SoundEvents.ARMOR_EQUIP_DIAMOND, 3.0f, 0.1f, DAWNSTEEL_REPAIR, DAWNSTEEL_ASSET);
    public static final RegistryObject<Item> DAWNSTEEL_INGOT = reg("dawnsteel_ingot", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().fireResistant().rarity(Rarity.EPIC));
    public static final RegistryObject<Item> DAWNSTEEL_GREATSWORD = reg("dawnsteel_greatsword", p -> new InscribedItem(p, 2, false), () -> new Item.Properties().sword(DAWNSTEEL_TOOL, 6.0f, -3.0f).attributes(weapon(10.5, -3.0, 0.5)).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_PICKAXE = reg("dawnsteel_pickaxe", Item::new, () -> new Item.Properties().pickaxe(DAWNSTEEL_TOOL, 1.0f, -2.8f).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_AXE = reg("dawnsteel_axe", p -> new AxeItem(DAWNSTEEL_TOOL, 5.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_SHOVEL = reg("dawnsteel_shovel", p -> new ShovelItem(DAWNSTEEL_TOOL, 1.5f, -3.0f, p), () -> new Item.Properties().rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_HOE = reg("dawnsteel_hoe", p -> new net.minecraft.world.item.HoeItem(DAWNSTEEL_TOOL, -4.0f, 0.0f, p), () -> new Item.Properties().rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_HELMET = reg("dawnsteel_helmet", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DAWNSTEEL_ARMOR, ArmorType.HELMET).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_CHESTPLATE = reg("dawnsteel_chestplate", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DAWNSTEEL_ARMOR, ArmorType.CHESTPLATE).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_LEGGINGS = reg("dawnsteel_leggings", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DAWNSTEEL_ARMOR, ArmorType.LEGGINGS).rarity(Rarity.EPIC).fireResistant());
    public static final RegistryObject<Item> DAWNSTEEL_BOOTS = reg("dawnsteel_boots", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().humanoidArmor(DAWNSTEEL_ARMOR, ArmorType.BOOTS).rarity(Rarity.EPIC).fireResistant());
    // ------------------------------------------------------------------ end of gear tiers

    // ------------------------------------------------------------------ wares (generated by tools/oath/wares.py)
    public static final RegistryObject<Item> BELL_OF_THE_DROWNED = reg("bell_of_the_drowned", p -> new RelicItem(p, RelicItem.Kind.BELL), () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
    public static final RegistryObject<Item> VEYLS_MIRROR = reg("veyls_mirror", p -> new RelicItem(p, RelicItem.Kind.MIRROR), () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
    public static final RegistryObject<Item> BARROW_CENSER = reg("barrow_censer", p -> new RelicItem(p, RelicItem.Kind.CENSER), () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
    public static final RegistryObject<Item> LANTERNGUARD_SIGNET = reg("lanternguard_signet", p -> new RelicItem(p, RelicItem.Kind.SIGNET), () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
    public static final RegistryObject<Item> HEART_OF_THE_GLOAM = reg("heart_of_the_gloam", p -> new RelicItem(p, RelicItem.Kind.HEART), () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC));
    public static final RegistryObject<Item> SUNSHARD_TALISMAN = reg("sunshard_talisman", p -> new RelicItem(p, RelicItem.Kind.SUNSHARD), () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC));
    public static final RegistryObject<Item> HUNTSMANS_HORN = reg("huntsmans_horn", p -> new RelicItem(p, RelicItem.Kind.HORN), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> GROVE_KINGS_CROWN = reg("grove_kings_crown", p -> new RelicItem(p, RelicItem.Kind.GROVE), () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC));
    public static final RegistryObject<Item> BOG_MOTHERS_LANTERN = reg("bog_mothers_lantern", p -> new RelicItem(p, RelicItem.Kind.MIRE), () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC));
    public static final RegistryObject<Item> CINDER_HEART = reg("cinder_heart", p -> new RelicItem(p, RelicItem.Kind.CINDER), () -> new Item.Properties().stacksTo(1).rarity(Rarity.EPIC));
    public static final RegistryObject<Item> HEARTH_PIE = reg("hearth_pie", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(10, 0.8f, false), Consumables.defaultFood().build()));
    public static final RegistryObject<Item> HONEYCAKE = reg("honeycake", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(6, 0.6f, false), Consumables.defaultFood().onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.ABSORPTION, 600, 0))).build()));
    public static final RegistryObject<Item> SALTED_COD = reg("salted_cod", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(64).food(new FoodProperties(6, 0.7f, false), Consumables.defaultFood().build()));
    public static final RegistryObject<Item> APPLE_TART = reg("apple_tart", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(7, 0.6f, false), Consumables.defaultFood().build()));
    public static final RegistryObject<Item> TRAIL_RATIONS = reg("trail_rations", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(8, 0.8f, false), Consumables.defaultFood().consumeSeconds(0.8f).build()));
    public static final RegistryObject<Item> EMBERROOT_STEW = reg("emberroot_stew", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(1).food(new FoodProperties(7, 0.8f, false), Consumables.defaultFood().onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 1200, 0))).build()).usingConvertsTo(net.minecraft.world.item.Items.BOWL));
    public static final RegistryObject<Item> MOONPETAL_TEA = reg("moonpetal_tea", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(2, 0.3f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 0))).onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 1200, 0))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> DUSKWINE = reg("duskwine", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(3, 0.4f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 3600, 0))).onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.NAUSEA, 120, 0))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> SPICED_CIDER = reg("spiced_cider", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().stacksTo(16).food(new FoodProperties(4, 0.5f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(new MobEffectInstance(MobEffects.HASTE, 2400, 0))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> ELIXIR_OF_TIDES = reg("elixir_of_tides", p -> new InscribedItem(p, 1, true), () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON).food(new FoodProperties(0, 0.0f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(java.util.List.of(new MobEffectInstance(MobEffects.WATER_BREATHING, 9600, 0), new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 3600, 0)))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> ELIXIR_OF_WARDS = reg("elixir_of_wards", p -> new InscribedItem(p, 1, true), () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON).food(new FoodProperties(0, 0.0f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(java.util.List.of(new MobEffectInstance(MobEffects.RESISTANCE, 3600, 0), new MobEffectInstance(MobEffects.ABSORPTION, 1200, 1)))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> ELIXIR_OF_SHROUDS = reg("elixir_of_shrouds", p -> new InscribedItem(p, 1, true), () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON).food(new FoodProperties(0, 0.0f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(java.util.List.of(new MobEffectInstance(MobEffects.INVISIBILITY, 3600, 0), new MobEffectInstance(MobEffects.NIGHT_VISION, 3600, 0)))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> ELIXIR_OF_THE_WAYFARER = reg("elixir_of_the_wayfarer", p -> new InscribedItem(p, 1, true), () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON).food(new FoodProperties(0, 0.0f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(java.util.List.of(new MobEffectInstance(MobEffects.SPEED, 3600, 1), new MobEffectInstance(MobEffects.JUMP_BOOST, 3600, 0)))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> ELIXIR_OF_VALOR = reg("elixir_of_valor", p -> new InscribedItem(p, 1, true), () -> new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON).food(new FoodProperties(0, 0.0f, true), Consumables.defaultDrink().onConsume(new ApplyStatusEffectsConsumeEffect(java.util.List.of(new MobEffectInstance(MobEffects.STRENGTH, 1800, 1), new MobEffectInstance(MobEffects.HASTE, 1800, 0)))).build()).usingConvertsTo(net.minecraft.world.item.Items.GLASS_BOTTLE));
    public static final RegistryObject<Item> RAW_VENISON = reg("raw_venison", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.COMMON).food(new FoodProperties(3, 0.3f, false)));
    public static final RegistryObject<Item> COOKED_VENISON = reg("cooked_venison", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.COMMON).food(new FoodProperties(8, 0.9f, false)));
    public static final RegistryObject<Item> GLIMMER_ANTLER = reg("glimmer_antler", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> MOSSBACK_SCUTE = reg("mossback_scute", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> BOAR_TUSK = reg("boar_tusk", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.COMMON));
    public static final RegistryObject<Item> HAG_EYE = reg("hag_eye", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> SHADOW_FANG = reg("shadow_fang", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.RARE));
    public static final RegistryObject<Item> EMBER_CORE = reg("ember_core", p -> new InscribedItem(p, 1, false), () -> new Item.Properties().rarity(Rarity.UNCOMMON).fireResistant());
    public static final RegistryObject<Item> LORE_PAGE_FIRST_LANTERN = reg("lore_page_first_lantern", p -> new LorePageItem(p, "first_lantern", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_OATH_OF_EMBER = reg("lore_page_oath_of_ember", p -> new LorePageItem(p, "oath_of_ember", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_TIDE_KNIGHT = reg("lore_page_tide_knight", p -> new LorePageItem(p, "tide_knight", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_FOUR_RIDDLES = reg("lore_page_four_riddles", p -> new LorePageItem(p, "four_riddles", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_HONEST_KING = reg("lore_page_honest_king", p -> new LorePageItem(p, "honest_king", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_LORD_COMMANDER = reg("lore_page_lord_commander", p -> new LorePageItem(p, "lord_commander", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_THE_GLOAMING = reg("lore_page_the_gloaming", p -> new LorePageItem(p, "the_gloaming", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_HOLLOW_CROWN = reg("lore_page_hollow_crown", p -> new LorePageItem(p, "hollow_crown", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_SUNDERING = reg("lore_page_sundering", p -> new LorePageItem(p, "sundering", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_THREE_SEALS = reg("lore_page_three_seals", p -> new LorePageItem(p, "three_seals", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_EVERFLAME = reg("lore_page_everflame", p -> new LorePageItem(p, "everflame", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_LAST_SQUIRE = reg("lore_page_last_squire", p -> new LorePageItem(p, "last_squire", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_GROVE_KING = reg("lore_page_grove_king", p -> new LorePageItem(p, "grove_king", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_BOG_MOTHER = reg("lore_page_bog_mother", p -> new LorePageItem(p, "bog_mother", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_SUN_CULT = reg("lore_page_sun_cult", p -> new LorePageItem(p, "sun_cult", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_LAST_WATCH = reg("lore_page_last_watch", p -> new LorePageItem(p, "last_watch", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_DROWNED_CHOIR = reg("lore_page_drowned_choir", p -> new LorePageItem(p, "drowned_choir", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_LUMENITE_RUSH = reg("lore_page_lumenite_rush", p -> new LorePageItem(p, "lumenite_rush", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> LORE_PAGE_STAR_READERS = reg("lore_page_star_readers", p -> new LorePageItem(p, "star_readers", 2), () -> new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final RegistryObject<Item> MUSIC_DISC_LANTERNGUARD_HYMN = reg("music_disc_lanternguard_hymn", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE).jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "lanternguard_hymn"))));
    public static final RegistryObject<Item> MUSIC_DISC_WAYSHRINE_NOCTURNE = reg("music_disc_wayshrine_nocturne", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE).jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "wayshrine_nocturne"))));
    public static final RegistryObject<Item> MUSIC_DISC_CHAPEL_TIDES = reg("music_disc_chapel_tides", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE).jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "chapel_tides"))));
    public static final RegistryObject<Item> MUSIC_DISC_CROWN_OF_ASH = reg("music_disc_crown_of_ash", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE).jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "crown_of_ash"))));
    public static final RegistryObject<Item> MUSIC_DISC_WILD_HUNT = reg("music_disc_wild_hunt", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE).jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "wild_hunt"))));
    public static final RegistryObject<Item> MUSIC_DISC_STARS_WENT_OUT = reg("music_disc_stars_went_out", Item::new, () -> new Item.Properties().stacksTo(1).rarity(Rarity.RARE).jukeboxPlayable(ResourceKey.create(net.minecraft.core.registries.Registries.JUKEBOX_SONG, Identifier.fromNamespaceAndPath(Oathbound.MODID, "stars_went_out"))));
    // ------------------------------------------------------------------ end of wares

    // ------------------------------------------------------------------ spawn eggs
    public static final RegistryObject<Item> LANTERNMOTH_SPAWN_EGG = egg("lanternmoth_spawn_egg", () -> ModEntities.LANTERNMOTH.get());
    public static final RegistryObject<Item> GLOAMLING_SPAWN_EGG = egg("gloamling_spawn_egg", () -> ModEntities.GLOAMLING.get());
    public static final RegistryObject<Item> FORSWORN_KNIGHT_SPAWN_EGG = egg("forsworn_knight_spawn_egg", () -> ModEntities.FORSWORN_KNIGHT.get());
    public static final RegistryObject<Item> BARROW_WIGHT_SPAWN_EGG = egg("barrow_wight_spawn_egg", () -> ModEntities.BARROW_WIGHT.get());
    public static final RegistryObject<Item> ANIMATED_TOME_SPAWN_EGG = egg("animated_tome_spawn_egg", () -> ModEntities.ANIMATED_TOME.get());
    public static final RegistryObject<Item> VEILHOUND_SPAWN_EGG = egg("veilhound_spawn_egg", () -> ModEntities.VEILHOUND.get());
    public static final RegistryObject<Item> SPECTRAL_HOUSECARL_SPAWN_EGG = egg("spectral_housecarl_spawn_egg", () -> ModEntities.SPECTRAL_HOUSECARL.get());
    public static final RegistryObject<Item> SIR_CALDRIS_SPAWN_EGG = egg("sir_caldris_spawn_egg", () -> ModEntities.SIR_CALDRIS.get());
    public static final RegistryObject<Item> ARCHMAGE_VEYL_SPAWN_EGG = egg("archmage_veyl_spawn_egg", () -> ModEntities.ARCHMAGE_VEYL.get());
    public static final RegistryObject<Item> HRODGAR_SPAWN_EGG = egg("hrodgar_spawn_egg", () -> ModEntities.HRODGAR.get());
    public static final RegistryObject<Item> MORVANE_SPAWN_EGG = egg("morvane_spawn_egg", () -> ModEntities.MORVANE.get());

    // ------------------------------------------------------------------ the wider roster (generated by tools/oath/roster.py)
    public static final RegistryObject<Item> GLIMMERFAWN_SPAWN_EGG = egg("glimmerfawn_spawn_egg", () -> ModEntities.GLIMMERFAWN.get());
    public static final RegistryObject<Item> DUSKHARE_SPAWN_EGG = egg("duskhare_spawn_egg", () -> ModEntities.DUSKHARE.get());
    public static final RegistryObject<Item> MOSSBACK_TORTOISE_SPAWN_EGG = egg("mossback_tortoise_spawn_egg", () -> ModEntities.MOSSBACK_TORTOISE.get());
    public static final RegistryObject<Item> LUMEN_BEETLE_SPAWN_EGG = egg("lumen_beetle_spawn_egg", () -> ModEntities.LUMEN_BEETLE.get());
    public static final RegistryObject<Item> TIDEWADER_SPAWN_EGG = egg("tidewader_spawn_egg", () -> ModEntities.TIDEWADER.get());
    public static final RegistryObject<Item> THORNBACK_BOAR_SPAWN_EGG = egg("thornback_boar_spawn_egg", () -> ModEntities.THORNBACK_BOAR.get());
    public static final RegistryObject<Item> STONEWARDEN_SPAWN_EGG = egg("stonewarden_spawn_egg", () -> ModEntities.STONEWARDEN.get());
    public static final RegistryObject<Item> RUNEWISP_SPAWN_EGG = egg("runewisp_spawn_egg", () -> ModEntities.RUNEWISP.get());
    public static final RegistryObject<Item> DROWNED_CHOIRMONK_SPAWN_EGG = egg("drowned_choirmonk_spawn_egg", () -> ModEntities.DROWNED_CHOIRMONK.get());
    public static final RegistryObject<Item> MIRE_HAG_SPAWN_EGG = egg("mire_hag_spawn_egg", () -> ModEntities.MIRE_HAG.get());
    public static final RegistryObject<Item> GRAVE_CRAWLER_SPAWN_EGG = egg("grave_crawler_spawn_egg", () -> ModEntities.GRAVE_CRAWLER.get());
    public static final RegistryObject<Item> GLOAM_STALKER_SPAWN_EGG = egg("gloam_stalker_spawn_egg", () -> ModEntities.GLOAM_STALKER.get());
    public static final RegistryObject<Item> SHADE_WRAITH_SPAWN_EGG = egg("shade_wraith_spawn_egg", () -> ModEntities.SHADE_WRAITH.get());
    public static final RegistryObject<Item> LUMENITE_MITE_SPAWN_EGG = egg("lumenite_mite_spawn_egg", () -> ModEntities.LUMENITE_MITE.get());
    public static final RegistryObject<Item> ASHEN_REVENANT_SPAWN_EGG = egg("ashen_revenant_spawn_egg", () -> ModEntities.ASHEN_REVENANT.get());
    public static final RegistryObject<Item> ELDERHORN_SPAWN_EGG = egg("elderhorn_spawn_egg", () -> ModEntities.ELDERHORN.get());
    public static final RegistryObject<Item> BOG_MOTHER_SPAWN_EGG = egg("bog_mother_spawn_egg", () -> ModEntities.BOG_MOTHER.get());
    public static final RegistryObject<Item> CINDER_COLOSSUS_SPAWN_EGG = egg("cinder_colossus_spawn_egg", () -> ModEntities.CINDER_COLOSSUS.get());
    public static final RegistryObject<Item> GLIMMERSTAG_SPAWN_EGG = egg("glimmerstag_spawn_egg", () -> ModEntities.GLIMMERSTAG.get());
    public static final RegistryObject<Item> LANTERNGUARD_PILGRIM_SPAWN_EGG = egg("lanternguard_pilgrim_spawn_egg", () -> ModEntities.LANTERNGUARD_PILGRIM.get());
    // ------------------------------------------------------------------ end of the wider roster
    // ------------------------------------------------------------------ block items
    static {
        for (var entry : ModBlocks.BLOCKS.getEntries()) {
            String name = entry.getId().getPath();
            if (name.equals("wisplight") || name.equals("gloam_veil") || name.startsWith("potted_")) continue;
            Rarity rarity = switch (name) {
                case "sundered_keystone", "ward_lantern" -> Rarity.EPIC;
                case "lore_tablet", "hymn_stone", "cipher_lectern", "rune_dial", "chapel_bell", "sarcophagus", "arcane_ward",
                     "sealed_grate", "barrow_seal", "wayshrine_brazier" -> Rarity.RARE;
                case "lumenite_block", "oathsteel_block" -> Rarity.UNCOMMON;
                default -> Rarity.COMMON;
            };
            ORDER.add(ITEMS.register(name, () -> {
                Item.Properties props = new Item.Properties().setId(ITEMS.key(name)).useBlockDescriptionPrefix().rarity(rarity);
                return entry.get() instanceof net.minecraft.world.level.block.DoorBlock
                    ? new net.minecraft.world.item.DoubleHighBlockItem(entry.get(), props) : new BlockItem(entry.get(), props);
            }));
        }
    }

    private static ItemAttributeModifiers halberdAttributes() {
        return ItemAttributeModifiers.builder()
            .add(Attributes.ATTACK_DAMAGE, new AttributeModifier(Item.BASE_ATTACK_DAMAGE_ID, 7.5, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ATTACK_SPEED, new AttributeModifier(Item.BASE_ATTACK_SPEED_ID, -3.0, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ENTITY_INTERACTION_RANGE, new AttributeModifier(Identifier.fromNamespaceAndPath(Oathbound.MODID, "halberd_reach"), 1.5, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .build();
    }

    /** Main-hand damage, speed and extra reach for weapons that outreach a sword. */
    private static ItemAttributeModifiers weapon(double damage, double speed, double reach) {
        return ItemAttributeModifiers.builder()
            .add(Attributes.ATTACK_DAMAGE, new AttributeModifier(Item.BASE_ATTACK_DAMAGE_ID, damage, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ATTACK_SPEED, new AttributeModifier(Item.BASE_ATTACK_SPEED_ID, speed, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ENTITY_INTERACTION_RANGE, new AttributeModifier(Identifier.fromNamespaceAndPath(Oathbound.MODID, "weapon_reach"), reach, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .build();
    }

    private static ResourceKey<EquipmentAsset> asset(String name) {
        return ResourceKey.create(EquipmentAssets.ROOT_ID, Identifier.fromNamespaceAndPath(Oathbound.MODID, name));
    }

    private static RegistryObject<Item> armor(String name, ArmorMaterial material, ArmorType type, Rarity rarity) {
        return reg(name, Item::new, () -> new Item.Properties().humanoidArmor(material, type).rarity(rarity));
    }

    private static RegistryObject<Item> egg(String name, Supplier<EntityType<?>> type) {
        return reg(name, SpawnEggItem::new, () -> new Item.Properties().spawnEgg(type.get()));
    }

    private static <I extends Item> RegistryObject<Item> reg(String name, Function<Item.Properties, I> factory, Supplier<Item.Properties> props) {
        RegistryObject<Item> ro = ITEMS.register(name, () -> factory.apply(props.get().setId(ITEMS.key(name))));
        ORDER.add(ro);
        return ro;
    }

    private ModItems() {}
}
