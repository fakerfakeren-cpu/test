package com.oathbound.registry;

import com.oathbound.Oathbound;
import com.oathbound.world.SketchPiece;
import com.oathbound.world.SketchStructure;
import com.oathbound.world.GloamFeatures;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModWorldgen {
    public static final DeferredRegister<StructureType<?>> STRUCTURE_TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, Oathbound.MODID);
    public static final DeferredRegister<StructurePieceType> STRUCTURE_PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, Oathbound.MODID);
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(ForgeRegistries.FEATURES, Oathbound.MODID);

    public static final RegistryObject<StructureType<SketchStructure>> SKETCH_STRUCTURE =
        STRUCTURE_TYPES.register("sketch", () -> () -> SketchStructure.CODEC);
    public static final RegistryObject<StructurePieceType> SKETCH_PIECE =
        STRUCTURE_PIECES.register("sketch", () -> SketchPiece::new);

    /** A twisted, leafless gloamwood tree with hanging veilbloom. */
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> GLOAMWOOD_TREE =
        FEATURES.register("gloamwood_tree", () -> new GloamFeatures.Tree(NoneFeatureConfiguration.CODEC));
    /** A broken Lanternguard pillar or wall stump, half-swallowed by gloamstone. */
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> GLOAM_RUIN =
        FEATURES.register("gloam_ruin", () -> new GloamFeatures.Ruin(NoneFeatureConfiguration.CODEC));
    /** A cluster of veilbloom flowers. */
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> VEILBLOOM_PATCH =
        FEATURES.register("veilbloom_patch", () -> new GloamFeatures.Flowers(NoneFeatureConfiguration.CODEC));

    public static final ResourceKey<Level> GLOAMING = ResourceKey.create(Registries.DIMENSION, Identifier.fromNamespaceAndPath(Oathbound.MODID, "gloaming"));

    private ModWorldgen() {}
}
