package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import com.rimeheart.world.BlueprintPiece;
import com.rimeheart.world.BlueprintStructure;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModWorldgen {
    public static final DeferredRegister<StructureType<?>> STRUCTURE_TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, Rimeheart.MODID);
    public static final DeferredRegister<StructurePieceType> STRUCTURE_PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, Rimeheart.MODID);

    public static final RegistryObject<StructureType<BlueprintStructure>> BLUEPRINT_STRUCTURE =
        STRUCTURE_TYPES.register("blueprint", () -> () -> BlueprintStructure.CODEC);
    public static final RegistryObject<StructurePieceType> BLUEPRINT_PIECE =
        STRUCTURE_PIECES.register("blueprint", () -> BlueprintPiece::new);

    private ModWorldgen() {}
}
