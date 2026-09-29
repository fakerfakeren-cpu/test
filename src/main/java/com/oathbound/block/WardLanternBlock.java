package com.oathbound.block;

import com.oathbound.entity.SpellMarkEntity;
import com.mojang.serialization.MapCodec;
import com.oathbound.entity.boss.MorvaneEntity;
import com.oathbound.item.WardensLanternItem;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * One of the four great Ward Lanterns around the Hollow Throne. When Morvane becomes the Hollow they gutter
 * out; relight them with a lit Warden's Lantern or a Lumenite Shard to tear his shadow away.
 */
public class WardLanternBlock extends Block {
    public static final MapCodec<WardLanternBlock> CODEC = simpleCodec(WardLanternBlock::new);
    public static final BooleanProperty LIT = BooleanProperty.create("lit");
    private static final VoxelShape SHAPE = Shapes.or(Block.box(3, 0, 3, 13, 2, 13), Block.box(4, 2, 4, 12, 13, 12), Block.box(5, 13, 5, 11, 16, 11));

    public WardLanternBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(LIT, true));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(LIT);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        boolean lantern = stack.getItem() instanceof WardensLanternItem l && l.isLit(stack);
        boolean shard = stack.is(ModItems.LUMENITE_SHARD.get());
        if (!lantern && !shard) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (state.getValue(LIT)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            relight(server, pos);
            if (shard && !player.hasInfiniteMaterials()) stack.shrink(1);
            if (lantern && stack.getItem() instanceof WardensLanternItem l) l.burn(stack, player, 20);
            for (MorvaneEntity m : server.getEntitiesOfClass(MorvaneEntity.class, new AABB(pos).inflate(48))) m.onLanternLit(server, pos, player);
        }
        return InteractionResult.SUCCESS;
    }

    public static void relight(ServerLevel level, BlockPos pos) {
        level.setBlock(pos, level.getBlockState(pos).setValue(LIT, true), 3);
        level.playSound(null, pos, ModSounds.LANTERN_RELIGHT.get(), SoundSource.BLOCKS, 2.5f, 1.0f);
        Vec3 c = Vec3.atCenterOf(pos);
        Vfx.burst(level, ModParticles.SUNBURST.get(), c, 30, 0.3, 0.1);
        Vfx.burst(level, ModParticles.EMBER.get(), c, 20, 0.3, 0.08);
        SpellMarkEntity.pillar(level, Vec3.atBottomCenterOf(pos), 0.45f, SpellMarkEntity.Hue.DAWN, 26);
        SpellMarkEntity.ring(level, Vec3.atBottomCenterOf(pos), 3f, SpellMarkEntity.Hue.DAWN, 12);
    }

    public static void snuff(ServerLevel level, BlockPos pos) {
        if (!level.getBlockState(pos).getValue(LIT)) return;
        level.setBlock(pos, level.getBlockState(pos).setValue(LIT, false), 3);
        level.playSound(null, pos, ModSounds.LANTERN_SNUFF.get(), SoundSource.BLOCKS, 2.5f, 1.0f);
        Vfx.burst(level, ParticleTypes.LARGE_SMOKE, Vec3.atCenterOf(pos), 20, 0.3, 0.03);
        Vfx.burst(level, ModParticles.GLOAM_WISP.get(), Vec3.atCenterOf(pos), 20, 0.4, 0.05);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide() && !state.getValue(LIT)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.ward_lantern.hint").withStyle(ChatFormatting.GOLD));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        double x = pos.getX() + 0.5, y = pos.getY() + 0.6, z = pos.getZ() + 0.5;
        if (state.getValue(LIT)) {
            level.addParticle(ModParticles.EMBER.get(), x + (random.nextDouble() - 0.5) * 0.4, y + 0.5, z + (random.nextDouble() - 0.5) * 0.4, 0, 0.05, 0);
            if (random.nextInt(3) == 0) level.addParticle(ModParticles.LUMEN_MOTE.get(), x + (random.nextDouble() - 0.5) * 2, y + random.nextDouble() * 2, z + (random.nextDouble() - 0.5) * 2, 0, 0.01, 0);
        } else {
            level.addParticle(ModParticles.GLOAM_WISP.get(), x + (random.nextDouble() - 0.5) * 0.4, y, z + (random.nextDouble() - 0.5) * 0.4, 0, 0.02, 0);
        }
    }
}
