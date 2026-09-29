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
    public static final RegistryObject<Item> OATHKEY = reg("oathkey", p -> new InscribedItem(p, 2, true), () -> new Item.Properties().rarity(Rarity.EPIC).stacksTo(1).fireResistant());
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

    // ------------------------------------------------------------------ block items
    static {
        for (var entry : ModBlocks.BLOCKS.getEntries()) {
            String name = entry.getId().getPath();
            if (name.equals("wisplight") || name.equals("gloam_veil")) continue;
            Rarity rarity = switch (name) {
                case "sundered_keystone", "ward_lantern" -> Rarity.EPIC;
                case "lore_tablet", "hymn_stone", "cipher_lectern", "rune_dial", "chapel_bell", "sarcophagus", "arcane_ward",
                     "sealed_grate", "barrow_seal", "wayshrine_brazier" -> Rarity.RARE;
                case "lumenite_block", "oathsteel_block" -> Rarity.UNCOMMON;
                default -> Rarity.COMMON;
            };
            ORDER.add(ITEMS.register(name, () -> new BlockItem(entry.get(), new Item.Properties().setId(ITEMS.key(name)).useBlockDescriptionPrefix().rarity(rarity))));
        }
    }

    private static ItemAttributeModifiers halberdAttributes() {
        return ItemAttributeModifiers.builder()
            .add(Attributes.ATTACK_DAMAGE, new AttributeModifier(Item.BASE_ATTACK_DAMAGE_ID, 7.5, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ATTACK_SPEED, new AttributeModifier(Item.BASE_ATTACK_SPEED_ID, -3.0, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
            .add(Attributes.ENTITY_INTERACTION_RANGE, new AttributeModifier(Identifier.fromNamespaceAndPath(Oathbound.MODID, "halberd_reach"), 1.5, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
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
