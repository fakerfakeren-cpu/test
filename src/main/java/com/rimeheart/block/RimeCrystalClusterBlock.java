package com.rimeheart.block;

import com.mojang.serialization.MapCodec;
import com.rimeheart.Config;
import com.rimeheart.entity.mob.ShardlingEntity;
import com.rimeheart.registry.ModEntities;
import com.rimeheart.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.EnchantmentTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A glowing cluster of rime crystal. Some clusters are hollow nests: breaking one without Silk Touch can
 * release a Shardling that was sleeping inside.
 */
public class RimeCrystalClusterBlock extends Block {
    public static final MapCodec<RimeCrystalClusterBlock> CODEC = simpleCodec(RimeCrystalClusterBlock::new);
    private static final VoxelShape SHAPE = Block.box(3, 0, 3, 13, 12, 13);

    public RimeCrystalClusterBlock(Properties props) {
        super(props);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    protected void spawnAfterBreak(BlockState state, ServerLevel level, BlockPos pos, ItemStack tool, boolean dropExperience) {
        super.spawnAfterBreak(state, level, pos, tool, dropExperience);
        if (EnchantmentHelper.hasTag(tool, EnchantmentTags.PREVENTS_INFESTED_SPAWNS)) return;
        if (level.getRandom().nextInt(100) >= Config.shardlingAmbushChance()) return;
        ShardlingEntity s = ModEntities.SHARDLING.get().create(level, EntitySpawnReason.TRIGGERED);
        if (s != null) {
            s.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, level.getRandom().nextFloat() * 360f, 0f);
            level.addFreshEntity(s);
            s.spawnAnim();
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(4) == 0) {
            level.addParticle(ModParticles.FROST_GLINT.get(), pos.getX() + 0.2 + random.nextDouble() * 0.6, pos.getY() + 0.3 + random.nextDouble() * 0.6,
                pos.getZ() + 0.2 + random.nextDouble() * 0.6, 0, 0.01, 0);
        }
    }
}
