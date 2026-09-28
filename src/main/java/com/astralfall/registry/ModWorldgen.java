package com.astralfall.registry;

import com.astralfall.Astralfall;
import com.astralfall.world.BlueprintPiece;
import com.astralfall.world.BlueprintStructure;
import com.astralfall.world.ImpactSiteFeature;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModWorldgen {
    public static final DeferredRegister<StructureType<?>> STRUCTURE_TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, Astralfall.MODID);
    public static final DeferredRegister<StructurePieceType> STRUCTURE_PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, Astralfall.MODID);
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(ForgeRegistries.FEATURES, Astralfall.MODID);

    public static final RegistryObject<StructureType<BlueprintStructure>> BLUEPRINT_STRUCTURE =
        STRUCTURE_TYPES.register("blueprint", () -> () -> BlueprintStructure.CODEC);
    public static final RegistryObject<StructurePieceType> BLUEPRINT_PIECE =
        STRUCTURE_PIECES.register("blueprint", () -> BlueprintPiece::new);
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> IMPACT_SITE =
        FEATURES.register("impact_site", () -> new ImpactSiteFeature(NoneFeatureConfiguration.CODEC));

    private ModWorldgen() {}
}
