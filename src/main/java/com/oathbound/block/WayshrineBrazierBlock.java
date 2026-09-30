package com.oathbound.block;

import com.oathbound.entity.SpellMarkEntity;
import com.mojang.serialization.MapCodec;
import com.oathbound.item.WardensLanternItem;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * The bronze brazier at the heart of every Wayshrine. Touch a lit Warden's Lantern to it to rekindle the
 * shrine: it burns forever after and grants the Wayfarer's Blessing to anyone who warms their lantern there.
 */
public class WayshrineBrazierBlock extends Block {
    public static final MapCodec<WayshrineBrazierBlock> CODEC = simpleCodec(WayshrineBrazierBlock::new);
    public static final BooleanProperty LIT = BooleanProperty.create("lit");
    private static final VoxelShape SHAPE = Shapes.or(Block.box(2, 0, 2, 14, 3, 14), Block.box(4, 3, 4, 12, 8, 12), Block.box(1, 8, 1, 15, 12, 15));

    public WayshrineBrazierBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(LIT, false));
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
        if (!(stack.getItem() instanceof WardensLanternItem lantern)) return InteractionResult.TRY_WITH_EMPTY_HAND;
        if (level instanceof ServerLevel server && player instanceof ServerPlayer sp) {
            if (!lantern.isLit(stack)) {
                player.sendOverlayMessage(Component.translatable("message.oathbound.lantern.empty").withStyle(ChatFormatting.RED));
                return InteractionResult.FAIL;
            }
            Vec3 c = Vec3.atCenterOf(pos).add(0, 0.6, 0);
            if (!state.getValue(LIT)) {
                server.setBlock(pos, state.setValue(LIT, true), 3);
                server.playSound(null, pos, ModSounds.WAYSHRINE_KINDLE.get(), SoundSource.BLOCKS, 1.6f, 1.0f);
                Vfx.burst(server, ModParticles.EMBER.get(), c, 50, 0.4, 0.12);
                Vfx.burst(server, ParticleTypes.FLAME, c, 20, 0.3, 0.05);
                Vfx.ring(server, ModParticles.LUMEN_MOTE.get(), c.add(0, -0.5, 0), 2.5, 32, 0.08);
                Vec3 foot = Vec3.atBottomCenterOf(pos);
                SpellMarkEntity.sigil(server, foot, 2.6f, SpellMarkEntity.Hue.DAWN, 70);
                SpellMarkEntity.pillar(server, foot.add(0, 0.8, 0), 0.55f, SpellMarkEntity.Hue.DAWN, 45);
                SpellMarkEntity.ring(server, foot, 7f, SpellMarkEntity.Hue.DAWN, 22);
                player.sendSystemMessage(Component.translatable("message.oathbound.wayshrine.kindled").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
            } else {
                server.playSound(null, pos, ModSounds.LANTERN_IGNITE.get(), SoundSource.BLOCKS, 1.0f, 1.2f);
                Vfx.burst(server, ModParticles.EMBER.get(), c, 15, 0.3, 0.06);
            }
            // The Wayfarer's Blessing, and a free refuel.
            player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 1));
            player.addEffect(new MobEffectInstance(MobEffects.SPEED, 1200, 0));
            player.addEffect(new MobEffectInstance(MobEffects.SATURATION, 20, 0));
            lantern.refuel(stack, 9999);
            player.sendOverlayMessage(Component.translatable("message.oathbound.wayshrine.blessing").withStyle(ChatFormatting.YELLOW));
            QuestLog.grant(sp, "wayshrine", "kindle");
            QuestLog.payTithes(sp, pos);
            com.oathbound.entity.npc.PilgrimVisits.atWayshrine(server, pos, sp);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.isClientSide() || !(player instanceof ServerPlayer sp)) return InteractionResult.SUCCESS;
        if (!state.getValue(LIT)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.wayshrine.hint").withStyle(ChatFormatting.GOLD));
            return InteractionResult.SUCCESS;
        }
        // Warm your hands at a kindled shrine: the Order pays every tithe it owes you.
        int paid = QuestLog.payTithes(sp, pos);
        if (paid == 0) player.sendOverlayMessage(Component.translatable("message.oathbound.wayshrine.no_tithes").withStyle(ChatFormatting.GOLD));
        return InteractionResult.SUCCESS;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        double x = pos.getX() + 0.5, y = pos.getY() + 0.8, z = pos.getZ() + 0.5;
        if (state.getValue(LIT)) {
            for (int i = 0; i < 2; i++) {
                level.addParticle(ParticleTypes.FLAME, x + (random.nextDouble() - 0.5) * 0.6, y, z + (random.nextDouble() - 0.5) * 0.6, 0, 0.03, 0);
            }
            level.addParticle(ModParticles.EMBER.get(), x + (random.nextDouble() - 0.5) * 0.5, y + 0.2, z + (random.nextDouble() - 0.5) * 0.5, 0, 0.06, 0);
            if (random.nextInt(8) == 0) level.playLocalSound(x, y, z, net.minecraft.sounds.SoundEvents.CAMPFIRE_CRACKLE, SoundSource.BLOCKS, 0.6f, 1.0f, false);
        } else if (random.nextInt(6) == 0) {
            level.addParticle(ParticleTypes.SMOKE, x + (random.nextDouble() - 0.5) * 0.5, y, z + (random.nextDouble() - 0.5) * 0.5, 0, 0.02, 0);
        }
    }
}
