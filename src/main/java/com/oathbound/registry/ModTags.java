package com.oathbound.registry;

import com.oathbound.Oathbound;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.levelgen.structure.Structure;

public final class ModTags {
    public static final TagKey<Item> OATHSTEEL_REPAIR = TagKey.create(Registries.ITEM, id("oathsteel_repair"));
    public static final TagKey<Item> SPELLSILK_REPAIR = TagKey.create(Registries.ITEM, id("spellsilk_repair"));
    public static final TagKey<Item> SUNMENDED = TagKey.create(Registries.ITEM, id("sunmended"));
    public static final TagKey<Item> OATH_FORGED = TagKey.create(Registries.ITEM, id("oath_forged"));
    public static final TagKey<EntityType<?>> GLOAM_CREATURES = TagKey.create(Registries.ENTITY_TYPE, id("gloam_creatures"));
    public static final TagKey<Structure> WAYSHRINE = TagKey.create(Registries.STRUCTURE, id("wayshrine"));
    public static final TagKey<Structure> DROWNED_CHAPEL = TagKey.create(Registries.STRUCTURE, id("drowned_chapel"));
    public static final TagKey<Structure> ARCANIST_SPIRE = TagKey.create(Registries.STRUCTURE, id("arcanist_spire"));
    public static final TagKey<Structure> BARROW = TagKey.create(Registries.STRUCTURE, id("barrow"));
    public static final TagKey<Structure> SUNDERED_CITADEL = TagKey.create(Registries.STRUCTURE, id("sundered_citadel"));

    private static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(Oathbound.MODID, path);
    }

    private ModTags() {}
}
