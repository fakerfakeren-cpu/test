package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.entity.mob.BarrowWightEntity;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import com.oathbound.util.Puzzles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * A king's tomb in the Barrow of Kings. Right-click to read the epitaph; kneel (sneak) and touch the tomb of
 * the one king who told the truth to open the way to Hrodgar. Exactly one epitaph is true in every barrow,
 * and which king it is changes from barrow to barrow.
 */
public class SarcophagusBlock extends HorizontalDirectionalBlock {
    public static final MapCodec<SarcophagusBlock> CODEC = simpleCodec(SarcophagusBlock::new);
    public static final IntegerProperty KING = IntegerProperty.create("king", 0, 2);
    public static final BooleanProperty OPEN = BooleanProperty.create("open");
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 13, 16);
    private static final int[][] PERMS = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
    private static final Map<Long, Long> WAKE_COOLDOWN = new HashMap<>();

    public SarcophagusBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(FACING, net.minecraft.core.Direction.NORTH).setValue(KING, 0).setValue(OPEN, false));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, KING, OPEN);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    /** (honest, liar who accuses, boaster) for this barrow, keyed by the first king's tomb. */
    public static int[] roles(ServerLevel level, BlockPos near) {
        BlockPos anchor = near;
        for (BlockPos p : Puzzles.find(level, near, 10, ModBlocks.SARCOPHAGUS.get())) {
            if (level.getBlockState(p).getValue(KING) == 0) {
                anchor = p;
                break;
            }
        }
        return PERMS[Puzzles.key(anchor) % PERMS.length];
    }

    public static Component kingName(int king) {
        return Component.translatable("king.oathbound." + king).withStyle(ChatFormatting.GOLD);
    }

    /** The epitaph carved on {@code king}'s tomb. */
    public static Component epitaph(int[] roles, int king) {
        int honest = roles[0], accused = roles[1], boaster = roles[2];
        if (king == honest) return Component.translatable("epitaph.oathbound.accuse", kingName(accused));
        if (king == accused) return Component.translatable("epitaph.oathbound.vouch", kingName(boaster));
        return Component.translatable("epitaph.oathbound.boast");
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level instanceof ServerLevel server)) return InteractionResult.SUCCESS;
        int king = state.getValue(KING);
        int[] roles = roles(server, pos);
        if (state.getValue(OPEN)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.tomb.open", kingName(king)).withStyle(ChatFormatting.GRAY));
            return InteractionResult.SUCCESS;
        }
        if (!player.isShiftKeyDown()) {
            server.playSound(null, pos, ModSounds.CHRONICLE_PAGE.get(), SoundSource.BLOCKS, 0.7f, 0.6f);
            player.sendSystemMessage(Component.literal(""));
            player.sendSystemMessage(Component.translatable("message.oathbound.tomb.here_lies", kingName(king)).withStyle(ChatFormatting.GRAY));
            player.sendSystemMessage(Component.literal("   “").withStyle(ChatFormatting.DARK_GRAY)
                .append(epitaph(roles, king).copy().withStyle(ChatFormatting.WHITE, ChatFormatting.ITALIC))
                .append(Component.literal("”").withStyle(ChatFormatting.DARK_GRAY)));
            player.sendSystemMessage(Component.translatable("message.oathbound.tomb.kneel_hint").withStyle(ChatFormatting.DARK_GRAY));
            return InteractionResult.SUCCESS;
        }
        if (!Puzzles.has(player, ModItems.SEAL_OF_WISDOM.get())) {
            player.sendSystemMessage(Component.translatable("message.oathbound.tomb.wisdom").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            return InteractionResult.SUCCESS;
        }
        if (king == roles[0]) {
            open(server, pos, player);
        } else {
            wakeLiar(server, pos, player, king);
        }
        return InteractionResult.SUCCESS;
    }

    public static void open(ServerLevel level, BlockPos pos, Player player) {
        BlockState state = level.getBlockState(pos);
        level.setBlock(pos, state.setValue(OPEN, true), 3);
        level.playSound(null, pos, ModSounds.TOMB_OPEN.get(), SoundSource.BLOCKS, 2.0f, 1.0f);
        level.playSound(null, pos, ModSounds.PUZZLE_SOLVED.get(), SoundSource.BLOCKS, 2.0f, 0.85f);
        Vec3 c = Vec3.atCenterOf(pos);
        Vfx.burst(level, ModParticles.SPIRIT.get(), c.add(0, 0.8, 0), 40, 0.4, 0.06);
        Vfx.burst(level, net.minecraft.core.particles.ParticleTypes.CLOUD, c.add(0, 0.8, 0), 20, 0.5, 0.02);
        Puzzles.unseal(level, pos, 24, ModBlocks.BARROW_SEAL.get(), ModParticles.SPIRIT.get(), ModSounds.WARD_DISSOLVE.get());
        if (player != null) {
            player.sendSystemMessage(Component.translatable("message.oathbound.tomb.honest", kingName(state.getValue(KING))).withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
            if (player instanceof ServerPlayer sp) QuestLog.grant(sp, "honest_king", "solved");
        }
    }

    private static void wakeLiar(ServerLevel level, BlockPos pos, Player player, int king) {
        level.playSound(null, pos, ModSounds.LIAR_WAKES.get(), SoundSource.HOSTILE, 2.0f, 1.0f);
        player.sendSystemMessage(Component.translatable("message.oathbound.tomb.liar", kingName(king)).withStyle(ChatFormatting.DARK_RED, ChatFormatting.ITALIC));
        Long last = WAKE_COOLDOWN.get(pos.asLong());
        long now = level.getGameTime();
        if (last != null && now - last < 300) return;
        WAKE_COOLDOWN.put(pos.asLong(), now);
        RandomSource r = level.getRandom();
        for (int i = 0; i < 2; i++) {
            BarrowWightEntity w = ModEntities.BARROW_WIGHT.get().create(level, EntitySpawnReason.EVENT);
            if (w == null) continue;
            double a = r.nextDouble() * Math.PI * 2;
            w.snapTo(pos.getX() + 0.5 + Math.cos(a) * 2, pos.getY() + 1, pos.getZ() + 0.5 + Math.sin(a) * 2, r.nextFloat() * 360, 0);
            w.setTarget(player);
            level.addFreshEntity(w);
            Vfx.burst(level, ModParticles.SPIRIT.get(), w.position().add(0, 1, 0), 30, 0.4, 0.05);
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(OPEN) && random.nextInt(3) == 0) {
            level.addParticle(ModParticles.SPIRIT.get(), pos.getX() + 0.2 + random.nextDouble() * 0.6, pos.getY() + 0.9, pos.getZ() + 0.2 + random.nextDouble() * 0.6, 0, 0.04, 0);
        }
    }

    public static List<BlockPos> tombs(ServerLevel level, BlockPos near) {
        return Puzzles.find(level, near, 10, ModBlocks.SARCOPHAGUS.get());
    }
}
