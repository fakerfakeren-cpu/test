package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.levelgen.structure.Structure;

public final class ModTags {
    public static final TagKey<Item> FROSTIRON_REPAIR = TagKey.create(Registries.ITEM, id("frostiron_repair"));
    public static final TagKey<Item> WRAITHWEAVE_REPAIR = TagKey.create(Registries.ITEM, id("wraithweave_repair"));
    /** Creatures of the Long Winter: immune to chill, and never hurt by the Sovereign's attacks. */
    public static final TagKey<EntityType<?>> WINTER_CREATURES = TagKey.create(Registries.ENTITY_TYPE, id("winter_creatures"));
    public static final TagKey<Structure> FROZEN_SANCTUM = TagKey.create(Registries.STRUCTURE, id("frozen_sanctum"));

    private static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(Rimeheart.MODID, path);
    }

    private ModTags() {}
}
