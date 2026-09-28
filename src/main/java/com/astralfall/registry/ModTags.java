package com.astralfall.registry;

import com.astralfall.Astralfall;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.levelgen.structure.Structure;

public final class ModTags {
    public static final TagKey<Item> STARMETAL_REPAIR = TagKey.create(Registries.ITEM, id("starmetal_repair"));
    public static final TagKey<Item> VOIDWALKER_REPAIR = TagKey.create(Registries.ITEM, id("voidwalker_repair"));
    public static final TagKey<EntityType<?>> VOID_CREATURES = TagKey.create(Registries.ENTITY_TYPE, id("void_creatures"));
    public static final TagKey<Structure> OBSERVATORY = TagKey.create(Registries.STRUCTURE, id("observatory"));
    public static final TagKey<Structure> FALLEN_VESSEL = TagKey.create(Registries.STRUCTURE, id("fallen_vessel"));
    public static final TagKey<Structure> SKY_SHRINE = TagKey.create(Registries.STRUCTURE, id("sky_shrine"));

    private static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(Astralfall.MODID, path);
    }

    private ModTags() {}
}
