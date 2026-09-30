package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.Oathbound;
import com.oathbound.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.grower.TreeGrower;
import net.minecraft.world.level.block.state.BlockState;

import java.util.Optional;

/** A gloamwood sapling. It takes root only where the Gloam has touched the ground: gloam moss or gloamstone. */
public class GloamSaplingBlock extends SaplingBlock {
    public static final TreeGrower GROWER = new TreeGrower("oathbound_gloamwood", Optional.empty(),
        Optional.of(ResourceKey.create(Registries.CONFIGURED_FEATURE, Identifier.fromNamespaceAndPath(Oathbound.MODID, "gloamwood_tree"))), Optional.empty());
    public static final MapCodec<GloamSaplingBlock> CODEC = simpleCodec(GloamSaplingBlock::new);

    public GloamSaplingBlock(Properties props) {
        super(GROWER, props);
    }

    @Override
    public MapCodec<? extends SaplingBlock> codec() {
        return CODEC;
    }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(ModBlocks.GLOAM_MOSS.get()) || state.is(ModBlocks.GLOAMSTONE.get());
    }
}
